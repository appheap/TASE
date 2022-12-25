from typing import Optional

from pydantic import BaseModel


class ChatScores(BaseModel):
    audio_indexer_score: Optional[float]
    audio_doc_indexer_score: Optional[float]
    username_extractor_score: Optional[float]
