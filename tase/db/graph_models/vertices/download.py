from dataclasses import dataclass

from .base_vertex import BaseVertex


@dataclass
class Download(BaseVertex):
    _vertex_name = 'downloads'

