from __future__ import annotations

from enum import Enum

import numpy as np

common_bit_rates = np.array(
    [
        16000,
        32000,
        64000,
        96000,
        128000,
        160000,
        192000,
        256000,
        320000,
        1411000,
        5699800,
        6144000,
        9216000,
        9600000,
        18000000,
    ]
)

bit_rate_string_mapping = {
    0: "",
    1: "16",
    2: "32",
    3: "64",
    4: "96",
    5: "128",
    6: "160",
    7: "192",
    8: "256",
    9: "320",
    10: "FLAC",
    11: "SACD",
    12: "EC-3",
    13: "Hi-Res",
    14: "DVD-Audio",
    15: "HQ",
}


class BitRateType(Enum):
    UNKNOWN = 0
    B_16K = 1
    B_32K = 2
    B_64K = 3
    B_96K = 4
    B_128K = 5
    B_160K = 6
    B_192K = 7
    B_256K = 8
    B_320K = 9
    B_1411K = 10
    B_5699K = 11
    B_6144K = 12
    B_9600K = 13
    B_18000K = 14

    @classmethod
    def estimate(
        cls,
        file_size: int,
        duration: int,
    ) -> BitRateType:
        if file_size is None or duration is None:
            return BitRateType.UNKNOWN

        if file_size == 0 or duration == 0:
            return BitRateType.UNKNOWN

        bit_rate = int(file_size * 8 / duration)
        argmin = np.abs(bit_rate - common_bit_rates).argmin()
        return BitRateType(argmin + 1)

    def get_bit_rate_string(
        self,
        include_bps: bool = False,
    ) -> str:
        q = bit_rate_string_mapping[self.value]

        if include_bps and 1 <= int(self.value) <= 9:
            return q + " kbps"

        return q


if __name__ == "__main__":
    print(
        BitRateType.estimate(249573313, 15571)
    )  # it must be `AudioQualityType.B_128K`
    print(
        BitRateType.estimate(1450467, 56)
    )  # it must be `AudioQualityType.B_128K`, but it `AudioQualityType.B_192K`
    print(BitRateType.estimate(6501646, 136))  # it must be `AudioQualityType.B_320K`
    print(BitRateType.estimate(5063869, 312))  # it must be `AudioQualityType.B_128K`

    print()
