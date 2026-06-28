# face2ppg

Face2PPG-Multi + OMIT パイプラインを pyVHR v2.0 上に自作する作業用パッケージ。

設計の根拠は親リポジトリの
[`STEP2_pyVHR_Face2PPG_correspondence.md`](../STEP2_pyVHR_Face2PPG_correspondence.md)
を参照。本 README はその対応表の **実装側ビュー**。

---

## ステータス

スケルトンのみ。全関数は `NotImplementedError`。
実装はステップ③以降で進める。

---

## パッケージ構成

| ファイル | 役割 | 論文での位置 |
|---|---|---|
| [`rigid_mesh_normalization.py`](rigid_mesh_normalization.py) | 自作① 剛体メッシュ正規化 (三角形アフィン写像で正面顔へ) | Rigid Mesh Normalization |
| [`dmrs_grid.py`](dmrs_grid.py) | 自作②-a 正規化顔を n×n 分割しセルRGB時系列を生成 | DMRS pre-OMIT |
| [`dmrs_selection.py`](dmrs_selection.py) | 自作②-b セル別BVPを KFD→DFA→energy で選別し時間領域で総和 | DMRS post-OMIT (§4.3.1) |
| [`fir_kaiser_filter.py`](fir_kaiser_filter.py) | 自作③ FIR + Kaiser (β=25) bandpass 0.75–4 Hz | ablation FIR 側 |
| [`pipeline.py`](pipeline.py) | 上記を pyVHR の windowing/filter/BVP と接続する全体配管 | — |
| [`requirements.txt`](requirements.txt) | 自作4ブロックの最小依存 | — |

---

## データ配管 (再掲)

```
frames [T,H,W,3]
  -> rigid_mesh_normalization.normalize_sequence
normalized [T, H', W', 3]
  -> dmrs_grid.grid_cell_rgb(n=9)
sig [T, 81, 3]                                    ← num_estimators = 81
  -> pyVHR.extraction.utils.sig_windowing(sig, 60, 5, fps)
windows: list of [81, 3, win_frames]
  -> pyVHR.BVP.filters.apply_filter
       (Butterworth = pyVHR BPfilter | FIR Kaiser = face2ppg.fir_kaiser_filter)
filtered: 同形状
  -> pyVHR.BVP.BVP.RGB_sig_to_BVP(method=cpu_OMIT)
bvp per window: [81, win_frames]
  -> dmrs_selection.select_and_sum
rPPG per window: [1, win_frames]
```

---

## セットアップ

リポジトリ直下に作成済みの venv を使う。

```bash
# プロジェクトルート (pyVHR/) で
python -m venv .venv          # 既に作成済み
.venv\Scripts\activate        # Windows
pip install -r face2ppg\requirements.txt
```

pyVHR 本体側 (`pyVHR/extraction/utils.sig_windowing`, `pyVHR/BVP/BVP.RGB_sig_to_BVP`,
`pyVHR/BVP/methods.cpu_OMIT`, `pyVHR/BVP/filters.apply_filter`) は別途
`pyVHR_env.yml` または `pip install -e .` で利用可能にする想定。

### インストール後に判明している既知の問題 (Python 3.13 + 最新wheel構成)

検証日時点で確認した版: numpy 2.5.0 / scipy 1.18.0 / opencv-python 4.13.0 /
mediapipe 0.10.35 / pytest 9.1.1 / Python 3.13.5。

1. **mediapipe 0.10.35 の Python 3.13 wheel には `mediapipe.solutions` が含まれない**
   (`mediapipe.tasks` 系のみ)。pyVHR v2.0 の `sig_processing.py` が使う
   `mediapipe.solutions.face_mesh.FaceMesh` がそのままでは import できない。
   - 対応候補:
     (a) Python を 3.10/3.11 に下げて旧 mediapipe (0.10.x の solutions 同梱版) を入れる
     (b) `mediapipe.tasks.vision.FaceLandmarker` (Tasks API) に書き換える層を自作①側に置く
     (c) mediapipe の古いバージョン (例: 0.10.9 等) を 3.13 で入れられるか試す

2. **pyVHR 本体は `numba` 他 (pyVHR_env.yml の依存) を必要とする**。
   face2ppg/requirements.txt はあくまで「自作4ブロック単体」の最小依存であり、
   pyVHR 本体を動かすには別途インストールが必要。

これらは「自作4ブロックを書く」作業自体には支障しない (各ブロックは numpy/scipy/cv2
だけで完結)。pyVHR 本体との結合テストを始めるタイミングで解消する。

---

## ステップ③着手前の決定事項

`STEP2_pyVHR_Face2PPG_correspondence.md` §7 への回答:

1. **剛体メッシュ正規化のメッシュ定義** → **MediaPipe 468点 + `FACEMESH_TESSELATION` を採用**
   - 理由: 検出源が MediaPipe で確定済み。85点への対応付け再構築は労力が大きく、
     その労力が分類精度に効く保証がない。MediaPipe テッセレーションはそのまま流用でき
     実装が自然。
   - 懸念: 論文の剛体メッシュ正規化 (85点 / 131三角形) を厳密再現してはいない。
     ablation/再現性議論ではこの差分を明記すること。

2. **抽出窓 / MTF画像化窓** → **60秒 / 5秒オーバーラップで統一**
   - 理由: 最終段の CCT-LSTM パイプラインが 60s/5s の MTF 画像列を入力とする設計のため、
     OMIT 抽出窓もこれに合わせる。
   - 実装: `pyVHR.extraction.utils.sig_windowing(sig, wsize=60, stride=5, fps=fps)`。

3. **ablation のフィルタ固定パラメータ** → **未定**
   - 後続ステップで決定する。当面は `face2ppg.fir_kaiser_filter.fir_kaiser_bandpass`
     のデフォルト (`minHz=0.75, maxHz=4.0, beta=25`) を仮置きとする。

---

## 流用する pyVHR 側 API (改変しない)

| API | 場所 | 用途 |
|---|---|---|
| `sig_windowing(sig, wsize, stride, fps)` | `pyVHR/extraction/utils.py` | 窓化 |
| `apply_filter(...)` | `pyVHR/BVP/filters.py` | 窓ごとフィルタ適用 |
| `BPfilter(...)` | `pyVHR/BVP/filters.py` | Butterworth (ablation 比較対象) |
| `RGB_sig_to_BVP(...)` | `pyVHR/BVP/BVP.py` | OMITをN_cells一括適用 |
| `cpu_OMIT(signal)` | `pyVHR/BVP/methods.py` | 論文と数学的に等価 (STEP2 §3) |
