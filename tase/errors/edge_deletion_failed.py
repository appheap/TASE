from .tase_error import TASEError


class EdgeDeletionFailed(TASEError):
    """Edge deletion failed"""

    MESSAGE = "Edge `{}` deletion failed"
