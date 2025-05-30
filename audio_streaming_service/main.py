# import asyncio
# from src.infrastructure.grpc.server import serve_grpc
# from src.core.di import Container
# from src.core.logger import logger
# from functools import wraps

# def di_raii(main_func):
#     @wraps(main_func)
#     async def wrapper():
#         container = Container()
#         try:
#             # Инициализация ресурсов перед запуском
#             await Container.init_resources()
#             await main_func()
#         except asyncio.CancelledError:
#             logger.info("Received shutdown signal")
#             raise
#         except Exception as e:
#             logger.error(f"Application error: {e}")
#             raise
#         finally:
#             # Гарантированная очистка ресурсов
#             try:
#                 await Container.shutdown_resources()
#                 logger.info("Resources cleaned up successfully")
#             except Exception as e:
#                 logger.error(f"Error during cleanup: {e}")
#                 raise
#     return wrapper


# @di_raii
# async def main():
#     container = Container()
#     container.wire(modules=["src.infrastructure.grpc.server"])
    
#     await asyncio.gather(
#         serve_grpc(),
#         # тут еще консумер должен быть
#     )

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         logger.info("Application shutdown by user")

import asyncio
from src.infrastructure.storage.audio_streamer import S3AudioStreamer
from src.core.di import Container

async def main():

    container = Container()

    streamer = S3AudioStreamer(
        bucket_name="tracks",
        track_id="1",
        initial_bitrate="320",
        chunk_size=32768  # 32KB
    )

    print(streamer.available_bitrates)
    
    for i, chunk in enumerate(streamer.chunks()):
        if i % 10:
            streamer.switch_bitrate("128")
        print(f"Chunk #{chunk.number} | Size: {len(chunk.data)}")

asyncio.run(main())