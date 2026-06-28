"""DMRS statistical selection + BVP summation (Face2PPG paper, Section 4.3.1).

Block 2-b of 4 (see STEP2_pyVHR_Face2PPG_correspondence.md, Section 4).

Pipeline (per window)
---------------------
Inputs:
  - bvp_cells : np.ndarray, shape [N_cells, win_frames] (from cpu_OMIT)
  - rgb_cells : np.ndarray, shape [N_cells, 3, win_frames] (for stats)

Selection order (paper):
  1. Initial pruning: drop cells with zero variance along t.
  2. Relative KFD : D_KFD = KFD_region / KFD_global,  keep >= 0.85.
  3. DFA exponent : keep 0.5 < alpha < 1 (default 0.75 .. 1.0); drop
     alpha == 0.5 (uncorrelated) and alpha < 0.5 (anti-correlated).
  4. Energy final selection:
        valid count V:
          if V > rmax (default 32) -> top-rmax by energy
          if 1 <= V <= rmax        -> keep all V
          if V == 0                -> fallback: top-rmax by energy from full pool

Output:
  - rppg : np.ndarray, shape [1, win_frames]
           Time-domain SUM of the selected BVPs.

Statistics referenced by the paper (KFD, DFA, energy/PSD, variance) are
implemented here. Other listed metrics (mean, std, SNR, zero-crossings,
sample entropy) are not required for the selection itself.

NOTE: Skeleton only. No implementation yet.
"""

from __future__ import annotations

import numpy as np


# ----- statistics ---------------------------------------------------------

def katz_fractal_dimension(x: np.ndarray) -> float:
    """KFD for a 1-D signal."""
    raise NotImplementedError


def dfa_alpha(x: np.ndarray) -> float:
    """Detrended Fluctuation Analysis exponent alpha for a 1-D signal."""
    raise NotImplementedError


def band_energy(x: np.ndarray, fps: float, fmin: float = 0.75, fmax: float = 4.0) -> float:
    """PSD energy inside [fmin, fmax] for a 1-D signal."""
    raise NotImplementedError


# ----- selection + sum ----------------------------------------------------

def select_and_sum(
    bvp_cells: np.ndarray,
    fps: float,
    kfd_thresh: float = 0.85,
    dfa_range: tuple[float, float] = (0.75, 1.0),
    rmax: int = 32,
) -> np.ndarray:
    """Run DMRS selection on per-cell BVPs and return summed rPPG.

    Parameters
    ----------
    bvp_cells : [N_cells, win_frames]
    fps : sampling rate in Hz
    kfd_thresh : relative KFD threshold (default 0.85)
    dfa_range : (alpha_min, alpha_max) inclusive (default 0.75 .. 1.0)
    rmax : maximum number of selected regions (default 32)

    Returns
    -------
    np.ndarray, shape [1, win_frames]
    """
    raise NotImplementedError("DMRS selection + summation not implemented yet.")
