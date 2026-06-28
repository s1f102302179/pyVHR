"""FIR + Kaiser-window bandpass filter (Face2PPG ablation: FIR vs Butterworth).

Block 3 of 4 (see STEP2_pyVHR_Face2PPG_correspondence.md, Section 4).

pyVHR v2.0 only ships a Butterworth IIR (BPfilter in pyVHR/BVP/filters.py).
This module adds the FIR + Kaiser variant the paper uses (beta = 25,
passband 0.75 .. 4.0 Hz = 45 .. 240 bpm).

Signature must match pyVHR.BVP.filters.apply_filter so this can be passed
directly as the `method` argument:
  - Input  : np.ndarray of shape [num_estimators, 3, num_frames]
             or [num_estimators, num_frames]
  - Output : same shape

Implementation reference:
  scipy.signal.firwin(numtaps, [0.75, 4.0], fs=fps,
                      pass_zero=False, window=('kaiser', 25))
  followed by scipy.signal.filtfilt (zero-phase) along the time axis.

NOTE: Skeleton only. No implementation yet.
"""

from __future__ import annotations

import numpy as np


def fir_kaiser_bandpass(
    sig: np.ndarray,
    fps: float,
    minHz: float = 0.75,
    maxHz: float = 4.0,
    beta: float = 25.0,
    numtaps: int | None = None,
) -> np.ndarray:
    """Apply zero-phase FIR + Kaiser bandpass along the time axis.

    Parameters
    ----------
    sig : np.ndarray, shape [num_estimators, 3, num_frames]
                  or  [num_estimators, num_frames]
    fps : sampling rate in Hz
    minHz, maxHz : passband edges
    beta : Kaiser beta (default 25, per paper)
    numtaps : filter length; if None, choose from window length / fps

    Returns
    -------
    np.ndarray, same shape as `sig`
    """
    raise NotImplementedError("FIR + Kaiser bandpass not implemented yet.")
