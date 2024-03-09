from sqlite3 import Cursor
from typing import Any, List, Optional, NamedTuple


class ViewRow(NamedTuple):
    view_id: str
    view_name: str
    media_type: str


class JellyfinDatabase:
    cursor: Cursor = ...
    def __init__(self, cursor: Cursor) -> None: ...
    def get_view(self, *args: Any) -> Optional[ViewRow]: ...
    def get_views(self) -> List[ViewRow]: ...

    # def get_item_by_id(self, *args: Any): ...
    # def add_reference(self, *args: Any) -> None: ...
    # def update_reference(self, *args: Any) -> None: ...
    # def update_parent_id(self, *args: Any) -> None: ...
    # def get_item_id_by_parent_id(self, *args: Any): ...
    # def get_item_by_parent_id(self, *args: Any): ...
    # def get_item_by_media_folder(self, *args: Any): ...
    # def get_item_by_wild_id(self, item_id: Any): ...
    # def get_checksum(self, *args: Any): ...
    # def get_item_by_kodi_id(self, *args: Any): ...
    # def get_full_item_by_kodi_id(self, *args: Any): ...
    # def get_media_by_id(self, *args: Any): ...
    # def get_media_by_parent_id(self, *args: Any): ...
    # def remove_item(self, *args: Any) -> None: ...
    # def remove_items_by_parent_id(self, *args: Any) -> None: ...
    # def remove_item_by_kodi_id(self, *args: Any) -> None: ...
    # def remove_wild_item(self, item_id: Any) -> None: ...
    # def get_view_name(self, item_id: Any): ...
    # def add_view(self, *args: Any) -> None: ...
    # def remove_view(self, *args: Any) -> None: ...
    # def get_views_by_media(self, *args: Any): ...
    # def get_items_by_media(self, *args: Any): ...
    # def remove_media_by_parent_id(self, *args: Any) -> None: ...
