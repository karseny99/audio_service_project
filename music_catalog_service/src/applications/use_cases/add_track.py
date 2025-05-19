# from dependency_injector.wiring import inject, Provide

# from src.domain.playlists.repository import PlaylistRepository
# from src.domain.music_catalog.services import AbstractTrackService
# from src.domain.events.publisher import EventPublisher
# from src.core.exceptions import (
#     TrackNotFoundError,
#     InsufficientPermission,
# )  
# from src.core.logger import logger



# class AddTrackToPlaylistUseCase:
#     @inject #  TODO: where abstractions ????????????????????????????????????????????????????????????????????????????
#     def __init__(
#         self,
#         playlist_repo: PlaylistRepository,
#         track_service: AbstractTrackService,
#         event_publisher: EventPublisher,
#     ):
#         self._playlist_repo = playlist_repo
#         self._track_service = track_service
#         self._event_publisher = event_publisher

#     async def execute(self, playlist_id: str, track_id: str, user_id: str) -> None:
#         # 1. Проверяем существование трека (синхронный вызов)
#         track_exists = await self._track_service.verify_track_exists(track_id)
#         if not track_exists:
#             raise TrackNotFoundError(f"Track {track_id} not found")
        
#         # 1.5 Проверяем, что этот юзер - владелец плейлиста
#         actual_owner = await self._playlist_repo.get_playlist_owner(playlist_id)
#         if actual_owner.id != user_id:
#             raise InsufficientPermission(f"User {user_id} does not have such rights")

#         # 2. Добавляем в плейлист
#         playlist = await self._playlist_repo.get_by_id(playlist_id)
#         playlist.add_track(track_id)
#         await self._playlist_repo.update(playlist)
        
#         # # 3. Отправляем событие (вроде не надо)
#         # await self._event_publisher.publish(
#         #     event=TrackAddedToPlaylist(
#         #         playlist_id=playlist_id,
#         #         track_id=track_id,
#         #         user_id=user_id
#         #     ).to_proto(),
#         #     topic="playlist_events"
#         # )

