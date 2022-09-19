class TASEError(Exception):
    """Base `TASE` Error"""

    MESSAGE = "TASE Error {}"

    def __init__(
        self,
        *args,
    ):
        super().__init__(
            f"TASE says: {self.MESSAGE.format(*args)}",
        )
