from typing import Optional, Tuple

from elastic_transport import ObjectApiResponse
from pydantic import BaseModel, Field

from tase.utils import get_timestamp


class BaseDocument(BaseModel):
    _index_name = "base_index_name"

    _to_db_mapping = ['id']

    id: Optional[str]

    created_at: int = Field(default_factory=get_timestamp)
    modified_at: int = Field(default_factory=get_timestamp)

    def parse_for_db(self) -> Tuple[str, dict]:
        temp_dict = self.dict()
        for key in self._to_db_mapping:
            del temp_dict[key]

        return self.id, temp_dict

    @classmethod
    def parse_from_db(cls, response: ObjectApiResponse):
        if response is None or not len(response.body):
            return None

        body = dict(**response.body['_source'])
        body.update({'id': response.body['_id']})

        return cls(**body)
