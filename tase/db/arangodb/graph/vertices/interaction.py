from __future__ import annotations

import uuid
from typing import Optional, TYPE_CHECKING

from tase.errors import InvalidFromVertex, InvalidToVertex
from tase.my_logger import logger
from .base_vertex import BaseVertex
from .user import User
from ...enums import ChatType, InteractionType

if TYPE_CHECKING:
    from .. import ArangoGraphMethods


class Interaction(BaseVertex):
    _collection_name = "interactions"
    schema_version = 1

    type: InteractionType
    chat_type: ChatType

    @classmethod
    def parse(
        cls,
        key: str,
        type_: InteractionType,
        chat_type: ChatType,
    ) -> Optional[Interaction]:
        if key is None:
            return None

        return Interaction(
            key=key,
            type=type_,
            chat_type=chat_type,
        )


class InteractionMethods:
    def create_interaction(
        self: ArangoGraphMethods,
        hit_download_url: str,
        user: User,
        bot_id: int,
        type_: InteractionType,
        chat_type: ChatType,
    ) -> Optional[Interaction]:
        """
        Create `Download` vertex from the given `hit_download_url` parameter.

        Parameters
        ----------
        hit_download_url : str
            Hit's `download_url` to create the `Download` vertex
        user : User
            User to create the `Download` vertex for
        bot_id : int
            Telegram ID of the Bot which the query has been made to
        type_ : InteractionType
            Type of interaction to create
        chat_type : ChatType
            Type of the chat this interaction happened in

        Returns
        -------
        Interaction, optional
            Interaction vertex if the creation was successful, otherwise, return None

        """
        if (
            hit_download_url is None
            or user is None
            or bot_id is None
            or type_ is None
            or chat_type is None
        ):
            return None

        bot = self.get_user_by_telegram_id(bot_id)
        if bot is None:
            return None

        hit = self.find_hit_by_download_url(hit_download_url)
        if hit is None:
            return None

        try:
            audio = self.get_audio_from_hit(hit)
        except ValueError:
            # happens when the `Hit` has more than linked `Audio` vertices
            return None

        while True:
            key = str(uuid.uuid4())
            if Interaction.get(key) is None:
                break

        interaction = Interaction.parse(
            key,
            type_,
            chat_type,
        )
        if interaction is None:
            return None

        interaction, created = Interaction.insert(interaction)
        if not interaction or not created:
            return None

        from tase.db.arangodb.graph.edges import Has
        from tase.db.arangodb.graph.edges import FromHit

        # from tase.db.arangodb.graph.edges import FromBot

        try:
            Has.get_or_create_edge(interaction, audio)
        except (InvalidFromVertex, InvalidToVertex):
            logger.error(
                "ValueError: Could not create `has` edge from `Interaction` vertex to `Audio` vertex"
            )
            return None

        try:
            FromHit.get_or_create_edge(interaction, hit)
        except (InvalidFromVertex, InvalidToVertex):
            logger.error(
                "ValueError: Could not create `from_hit` edge from `Interaction` vertex to `Hit` vertex"
            )
            return None

        try:
            Has.get_or_create_edge(user, interaction)
        except (InvalidFromVertex, InvalidToVertex):
            logger.error(
                "ValueError: Could not create `has` edge from `User` vertex to `Interaction` vertex"
            )
            return None

        # try:
        #     FromBot.get_or_create_edge(download, bot)
        # except (InvalidFromVertex, InvalidToVertex):
        #     logger.error(
        #         "ValueError: Could not create `from_bot` edge from `Interaction` vertex to `User` vertex"
        #     )
        #     return None

        return interaction
