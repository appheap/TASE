from enum import Enum


class HostResolverType(Enum):
    SINGLE = "single"
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
