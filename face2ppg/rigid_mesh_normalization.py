"""Rigid Mesh Normalization (Face2PPG paper, Section "Rigid Mesh Normalization").

Block 1 of 4 to be implemented from scratch (see
STEP2_pyVHR_Face2PPG_correspondence.md, Section 4).

Purpose
-------
Take per-frame MediaPipe FaceMesh landmarks and warp each face image to a fixed
canonical frontal-face shape via per-triangle affine maps, so that the same
spatial cell across time always covers the same anatomical region.

Inputs
------
- frame      : np.ndarray of shape [H, W, 3] (BGR or RGB; convention TBD)
- landmarks  : np.ndarray of shape [468, 2] in (y, x) order (matches pyVHR's
               sig_processing.py convention: ldmks[idx,0]=row, ldmks[idx,1]=col)

Outputs
-------
- normalized : np.ndarray of shape [H_norm, W_norm, 3]

Open decisions (see STEP2 doc, Section 7)
-----------------------------------------
- Mesh definition: paper's 85-point / 131-triangle layout vs MediaPipe's
  FACEMESH_TESSELATION (468-point based). Pick one before implementing.
- Canonical target shape (H_norm, W_norm) and target landmark coordinates.

NOTE: Skeleton only. No implementation yet.
"""

from __future__ import annotations

import numpy as np


def normalize_face(frame: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
    """Warp a single face frame to the canonical mesh.

    Parameters
    ----------
    frame : np.ndarray, shape [H, W, 3]
    landmarks : np.ndarray, shape [468, 2] in (y, x)

    Returns
    -------
    np.ndarray, shape [H_norm, W_norm, 3]
    """
    raise NotImplementedError("Rigid Mesh Normalization not implemented yet.")


def normalize_sequence(frames: np.ndarray, landmarks_seq: np.ndarray) -> np.ndarray:
    """Warp a sequence of frames.

    Parameters
    ----------
    frames : np.ndarray, shape [num_frames, H, W, 3]
    landmarks_seq : np.ndarray, shape [num_frames, 468, 2]

    Returns
    -------
    np.ndarray, shape [num_frames, H_norm, W_norm, 3]
    """
    raise NotImplementedError("Rigid Mesh Normalization not implemented yet.")
