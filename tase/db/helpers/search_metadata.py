from pydantic import BaseModel


class SearchMetaData(BaseModel):
    rank: int
    score: float
