"""End-to-end Face2PPG-Multi + OMIT pipeline.

Wires the four custom blocks (rigid mesh normalization, DMRS grid,
DMRS selection, FIR Kaiser filter) with pyVHR v2.0's existing
sig_windowing -> apply_filter -> RGB_sig_to_BVP(cpu_OMIT) flow.

Data-shape contract (see STEP2 doc, Section 2):

    video frames
      -> [self ①] rigid_mesh_normalization.normalize_sequence
           normalized_frames : [num_frames, H_norm, W_norm, 3]
      -> [self ②-a] dmrs_grid.grid_cell_rgb
           sig : [num_frames, N_cells, 3]
      -> [pyVHR] pyVHR.extraction.utils.sig_windowing(sig, wsize, stride, fps)
           list of [N_cells, 3, win_frames]
      -> [pyVHR / self ③] pyVHR.BVP.filters.apply_filter
           (Butterworth = pyVHR BPfilter, FIR Kaiser = fir_kaiser_bandpass)
      -> [pyVHR] pyVHR.BVP.BVP.RGB_sig_to_BVP(method=cpu_OMIT)
           per-window [N_cells, win_frames]
      -> [self ②-b] dmrs_selection.select_and_sum
           per-window rPPG : [1, win_frames]

NOTE: Skeleton only. No implementation yet.
"""

from __future__ import annotations

import numpy as np


def run_face2ppg(
    frames: np.ndarray,
    landmarks_seq: np.ndarray,
    fps: float,
    wsize: float = 60.0,
    stride: float = 5.0,
    grid_n: int = 9,
    filter_kind: str = "fir_kaiser",  # or "butterworth"
) -> list[np.ndarray]:
    """Run the full pipeline and return per-window rPPG signals.

    Parameters
    ----------
    frames : [num_frames, H, W, 3]
    landmarks_seq : [num_frames, 468, 2] in (y, x)
    fps : sampling rate
    wsize, stride : windowing in seconds (defaults from paper for MTF: 60 / 5)
    grid_n : DMRS grid size per side (default 9 -> 81 cells)
    filter_kind : "fir_kaiser" or "butterworth"

    Returns
    -------
    list of np.ndarray, each shape [1, win_frames]
    """
    raise NotImplementedError("Face2PPG pipeline not wired yet.")
