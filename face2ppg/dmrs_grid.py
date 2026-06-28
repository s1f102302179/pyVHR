"""DMRS grid split + per-cell RGB mean (Face2PPG paper, DMRS step 2-a).

Block 2-a of 4 (see STEP2_pyVHR_Face2PPG_correspondence.md, Section 4).

Purpose
-------
Split the normalized face image into an n x n grid (default 9 x 9 = 81 cells)
and compute, for each cell across time, the mean RGB of its skin pixels.

Inputs
------
- normalized_frames : np.ndarray, shape [num_frames, H_norm, W_norm, 3]
- n : int (default 9)
- skin_mask : optional np.ndarray of shape [H_norm, W_norm] (bool) or
              [num_frames, H_norm, W_norm] for per-frame masks.

Outputs
-------
- sig : np.ndarray, shape [num_frames, N_cells, 3]
        Designed to plug directly into pyVHR's
        pyVHR.extraction.utils.sig_windowing(sig, wsize, stride, fps).

NOTE: Skeleton only. No implementation yet.
"""

from __future__ import annotations

import numpy as np


def grid_cell_rgb(
    normalized_frames: np.ndarray,
    n: int = 9,
    skin_mask: np.ndarray | None = None,
) -> np.ndarray:
    """Compute per-cell mean RGB time series.

    Parameters
    ----------
    normalized_frames : [num_frames, H_norm, W_norm, 3]
    n : grid size per side (n x n cells)
    skin_mask : optional skin pixel mask

    Returns
    -------
    np.ndarray, shape [num_frames, n*n, 3]
    """
    raise NotImplementedError("DMRS grid RGB extraction not implemented yet.")
