# face2ppg DESIGN DECISIONS

実装方針と環境構成の確定事項。設計の議論経緯は
[STEP2_pyVHR_Face2PPG_correspondence.md](../../STEP2_pyVHR_Face2PPG_correspondence.md)
を参照。

---

## 1. 実装方針 (ステップ③着手前の確定)

### 1-1. 剛体メッシュ正規化のメッシュ定義
**採用: MediaPipe 468点 + `FACEMESH_TESSELATION` (既製2556エッジ三角形分割)**

- 理由
  - ランドマーク検出源が MediaPipe で確定済み (pyVHR `sig_processing.py` 既存路線)
  - 論文の 85点 / 131三角形 への対応付け再構築は労力が大きく、
    その労力が下流分類精度に効く保証がない
  - MediaPipe テッセレーションは点番号と三角形がそのまま流用でき実装が自然
- 懸念 / 既知の差分
  - 論文の剛体メッシュ正規化 (85点 / 131三角形) を厳密再現してはいない
  - 再現性/ablation の議論では本差分を必ず明記する

### 1-2. 抽出窓 / MTF画像化窓
**採用: 60秒 / 5秒オーバーラップで統一**

- 理由: 最終段の CCT-LSTM パイプラインが 60s/5s の MTF 画像列を入力とする
- 実装: `pyVHR.extraction.utils.sig_windowing(sig, wsize=60, stride=5, fps=fps)`
- 注: 論文の HR 評価用窓 (10s/1s) は採用しない (用途が違う)

### 1-3. ablation のフィルタ固定パラメータ
**未定**

- 当面は `face2ppg.fir_kaiser_filter.fir_kaiser_bandpass` のデフォルト
  (`minHz=0.75, maxHz=4.0, beta=25`) を仮置きとし、後続ステップで確定する

---

## 2. 環境構成

### 2-1. Python ランタイム
**採用: Python 3.11 (具体: 3.11.9)**

- 理由 (調査で確定済みの事実)
  - mediapipe は **Python 3.13 用 wheel を提供していない**
    (公式 issue #6159)
  - mediapipe の `solutions` API は **0.10.30 以降で完全削除**
    (公式 issue #6192)。pyVHR v2.0 が使う
    `mp.solutions.face_mesh.FaceMesh` は 0.10.30+ では import 不可
  - pyVHR v2.0 はもともと Python 3.9 想定。3.11 への変更は後退ではなく整合方向
- 配置: `pyVHR/.venv311/` (既存 `pyVHR/.venv` (3.13) は当面残置、判断後削除)

### 2-2. 確定パッケージ構成 (.venv311 で検証済み, 検証日 2026-06-28)

| パッケージ | 確定版 | 役割 |
|---|---|---|
| Python | 3.11.9 | ランタイム |
| numpy | 1.26.4 | 全ブロック数値計算 (mediapipe 0.10.x が numpy<2 を要求) |
| scipy | 1.13.1 | `firwin` / `filtfilt` / PSD |
| opencv-python | 4.10.0.84 | 三角形アフィン写像 (`cv2.getAffineTransform` / `warpAffine`) |
| mediapipe | 0.10.21 | FaceMesh (468点) + `FACEMESH_TESSELATION` |
| pytest | 8.4.2 | 単体検証 |
| numba | 0.60.0 | pyVHR JIT |
| h5py | 3.16.0 | pyVHR HDF5 IO |
| matplotlib | 3.9.4 | pyVHR plot |
| tqdm | 4.68.3 | pyVHR 進捗 |
| scikit-image | 0.26.0 | pyVHR extraction utilities |
| scikit-learn | 1.4.2 | pyVHR `__init__` の要求 |

補足:
- `mediapipe==0.10.21` 採用理由 = 「solutions 同梱 (<0.10.30) かつ py3.11 wheel あり」
  を満たす **最大版**。pip 上の実在 wheel リスト: `... 0.10.20, 0.10.21, 0.10.30 ...`
  (0.10.22 ～ 0.10.29 は py3.11 wheel 欠番)
- `numpy<2` は mediapipe 0.10.x のメタデータ要求
- `opencv-python` 4.10 を要求しているが、mediapipe が `opencv-contrib-python` 4.11 を
  追加依存として持ち込むため、`cv2` import 時は contrib 側 (4.11) が優先される。
  機能的支障なし

### 2-3. 検証済み API import (.venv311 上で動作確認)

```
python                                              : 3.11.9
numpy                                               : 1.26.4
scipy.signal.firwin / filtfilt                      : OK
cv2.getAffineTransform / cv2.warpAffine             : OK
mediapipe                                           : 0.10.21
  mediapipe.solutions.face_mesh                     : OK
  FACEMESH_TESSELATION                              : 2556 edges
  FACEMESH_FACE_OVAL                                :   36 edges
  FaceMesh(max_num_faces=1)                         : OK
pytest                                              : 8.4.2
pyVHR.extraction.utils.sig_windowing                : OK
```

### 2-4. import が通らないもの (今回の検証範囲外)

| API | 不足依存 | 影響 |
|---|---|---|
| `import pyVHR` | cupy | パッケージ root の import |
| `pyVHR.extraction.sig_processing.SignalProcessing` | cupy | 動画読込～RGB抽出全体 |
| `pyVHR.BVP.methods.cpu_OMIT` | cupy | OMIT 本体 (CPU 関数自体は cupy 不要だがモジュール冒頭で cupy import) |
| `pyVHR.BVP.filters.apply_filter` / `BPfilter` | cupy | 既存フィルタ |
| `pyVHR.BVP.BVP.RGB_sig_to_BVP` | cupy | 窓ごとの BVP 変換 |

理由: pyVHR v2.0 は GPU パス (cupy/cusignal) を含み、これらのモジュールが冒頭で
`import cupy` を無条件に行う設計。`cupy` は CUDA toolkit に紐付く重い依存で、
Windows + Python 3.11 用 wheel は CUDA バージョン依存のため別判断とする。

**face2ppg 自作4ブロックの実装作業自体には支障しない**:
- 4ブロックは numpy / scipy / cv2 / mediapipe だけで完結
- 配管に必要な `pyVHR.extraction.utils.sig_windowing` は **cupy 無しで import 可**

`pyVHR` 全体を CPU で完全に動かしたい場合の対応候補:
- (a) `cupy` を CUDA 環境付きで導入
- (b) pyVHR の該当モジュールで cupy import をガード (ソース修正)
- (c) 自作ブロック側に sig_windowing 相当を再実装し、pyVHR 本体結合は OMIT 部だけに絞る

---

## 3. リポジトリ上の構成変更ログ

| 日付 | 変更 |
|---|---|
| 2026-06-28 | `.venv311/` (Python 3.11.9) 作成 |
| 2026-06-28 | `face2ppg/requirements.txt` を 3.11 + numpy<2 + mediapipe==0.10.21 に再設計 |
| 2026-06-28 | pyVHR runtime extras (numba/h5py/matplotlib/tqdm/scikit-image/scikit-learn) を requirements に追記 |
| 2026-06-28 | 既存 `.venv/` (Python 3.13) は残置 (判断保留) |
