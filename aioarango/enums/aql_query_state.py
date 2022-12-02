from enum import Enum


class AQLQueryState(Enum):
    INITIALIZING = "initializing"
    PARSING = "parsing"
    OPTIMIZING_AST = "optimizing ast"
    LOADING_COLLECTIONS = "loading collections"
    INSTANTIATING_PLAN = "instantiating plan"
    OPTIMIZING_PLAN = "optimizing plan"
    EXECUTING = "executing"
    FINALIZING = "finalizing"
    FINISHED = "finished"
    KILLED = "killed"
    INVALID = "invalid"
