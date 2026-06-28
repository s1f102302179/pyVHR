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

---

## ステップ③着手前に決めること

`STEP2_pyVHR_Face2PPG_correspondence.md` §7 より:

1. 剛体メッシュ正規化のメッシュ定義
   - 論文 85点 / 131三角形 を再現するか
   - MediaPipe `FACEMESH_TESSELATION` (468点ベースの既製分割) を使うか
2. 抽出窓 (OMIT入力) と MTF画像化窓 (60s/5s) の関係
3. ablation の FIR Kaiser と Butterworth の固定パラメータ

---

## 流用する pyVHR 側 API (改変しない)

| API | 場所 | 用途 |
|---|---|---|
| `sig_windowing(sig, wsize, stride, fps)` | `pyVHR/extraction/utils.py` | 窓化 |
| `apply_filter(...)` | `pyVHR/BVP/filters.py` | 窓ごとフィルタ適用 |
| `BPfilter(...)` | `pyVHR/BVP/filters.py` | Butterworth (ablation 比較対象) |
| `RGB_sig_to_BVP(...)` | `pyVHR/BVP/BVP.py` | OMITをN_cells一括適用 |
| `cpu_OMIT(signal)` | `pyVHR/BVP/methods.py` | 論文と数学的に等価 (STEP2 §3) |
