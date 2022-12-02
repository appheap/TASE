from enum import Enum


class KeyOptionsType(Enum):
    """
    Specifies the type of the key generator.
    """

    TRADITIONAL = "traditional"
    """
    The `traditional` key generator generates numerical keys in ascending order.
    The sequence of keys is not guaranteed to be gap-free.
    """

    AUTOINCREMENT = "autoincrement"
    """
    The `autoincrement` key generator generates numerical keys in ascending order,
    the initial offset and the spacing can be configured (note: autoincrement
    is currently only supported for non-sharded collections).
    The sequence of generated keys is not guaranteed to be gap-free, because a new key
    will be generated on every document insert attempt, not just for successful
    inserts.
    """

    UUID = "uuid"
    """
    he `uuid` key generator generates universally unique 128 bit keys, which
    are stored in hexadecimal human-readable format. This key generator can be used
    in a single-server or cluster to generate "seemingly random" keys. The keys
    produced by this key generator are not lexicographically sorted.
    Please note that keys are only guaranteed to be truly ascending in single
    server deployments and for collections that only have a single shard (that includes
    collections in a OneShard database).
    The reason is that for collections with more than a single shard, document keys
    are generated on coordinator(s). For collections with a single shard, the document
    keys are generated on the leader DB server, which has full control over the key
    sequence.
    """

    PADDED = "padded"
    """
    he padded key generator generates keys of a fixed length (16 bytes) in
    ascending lexicographical sort order. This is ideal for usage with the RocksDB
    engine, which will slightly benefit keys that are inserted in lexicographically
    ascending order. The key generator can be used in a single-server or cluster.
    The sequence of generated keys is not guaranteed to be gap-free.
    """
