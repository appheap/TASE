from enum import Enum


class ShardingStrategy(Enum):
    """
    Specifies the name of the sharding strategy to use for
    the collection. Since ArangoDB 3.4 there are different sharding strategies
    to select from when creating a new collection. The selected shardingStrategy
    value will remain fixed for the collection and cannot be changed afterwards.
    This is important to make the collection keep its sharding settings and
    always find documents already distributed to shards using the same
    initial sharding algorithm.
    """

    COMMUNITY_COMPAT = "community-compat"
    """
    default sharding used by ArangoDB Community Edition before version 3.4.
    """

    ENTERPRISE_COMPAT = "enterprise-compat"
    """
    default sharding used by ArangoDB Enterprise Edition before version 3.4.
    """

    ENTERPRISE_SMART_EDGE_COMPAT = "enterprise-smart-edge-compat"
    """
    default sharding used by smart edge collections in ArangoDB Enterprise Edition before version 3.4.
    """

    HASH = "hash"
    """
    default sharding used for new collections starting from version 3.4 (excluding smart edge collections).
    """

    ENTERPRISE_HASH_SMART_EDGE = "enterprise-hash-smart-edge"
    """
    default sharding used for new
    smart edge collections starting from version 3.4.
    
    If no sharding strategy is specified, the default will be `hash` for
    all collections, and `enterprise-hash-smart-edge` for all smart edge
    collections (requires the Enterprise Edition of ArangoDB).
    Manually overriding the sharding strategy does not yet provide a 
    benefit, but it may later in case other sharding strategies are added.
    """
