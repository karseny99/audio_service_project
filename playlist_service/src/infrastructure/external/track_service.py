from src.core.config import settings
from src.domain.tracks.services import AbstractTrackService
from src.core.protos.generated import TrackCommands_pb2_grpc, TrackCommands_pb2
from src.infrastructure.grpc.client import BaseGrpcClient

class TrackServiceClient(AbstractTrackService, BaseGrpcClient[TrackCommands_pb2_grpc.TrackServiceStub]):
    @property
    def stub_class(self):
        return TrackCommands_pb2_grpc.TrackServiceStub

    @property
    def service_address(self):
        return settings.get_grpc_music_service_url()

    async def verify_track_exists(self, track_id: str) -> bool:
        request = TrackCommands_pb2.VerifyTrackRequest(track_id=track_id)
        response = await self._call("VerifyTrackExists", request)
        return response.exists