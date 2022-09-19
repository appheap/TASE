from .tase_error import TASEError


class EdgeCreationFailed(TASEError):
    """Edge creation failed"""

    MESSAGE = "Edge `{}` creation failed"
