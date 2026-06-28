"""face2ppg: Face2PPG-Multi + OMIT pipeline built on pyVHR v2.0.

This package implements the four blocks that are NOT present in pyVHR v2.0,
as identified in STEP2_pyVHR_Face2PPG_correspondence.md:

  1) Rigid Mesh Normalization      -> rigid_mesh_normalization.py
  2-a) DMRS grid split + cell RGB  -> dmrs_grid.py
  2-b) DMRS selection + BVP sum    -> dmrs_selection.py
  3) FIR + Kaiser bandpass filter  -> fir_kaiser_filter.py

The full pipeline (wiring with pyVHR's sig_windowing / apply_filter /
RGB_sig_to_BVP / cpu_OMIT) lives in pipeline.py.
"""

__version__ = "0.0.0"
