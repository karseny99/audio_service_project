import asyncio
from functools import wraps
import time

from dependency_injector.wiring import inject, Provide
from src.infrastructure.grpc.server import serve_grpc
from src.infrastructure.kafka.consumer import KafkaConsumer
from src.core.di import Container
from src.core.logger import logger

def di_raii(main_func):
    @wraps(main_func)
    async def wrapper():
        container = Container()
        try:
            # Инициализация ресурсов перед запуском
            await Container.init_resources()
            await main_func()
        except asyncio.CancelledError:
            logger.info("Received shutdown signal")
            raise
        except Exception as e:
            logger.error(f"Application error: {e}")
            raise
        finally:
            # Гарантированная очистка ресурсов
            try:
                await Container.shutdown_resources()
                logger.info("Resources cleaned up successfully")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
                raise
    return wrapper




@di_raii
async def main():
    container = Container()
    container.wire(modules=["src.infrastructure.grpc.server"])
    # t1 = time.time()
    # use_case = container.get_track_use_case()
    # track = await use_case.execute(5)
    # logger.info(track)
    # # Вызываем метод
    # result = time.time() - t1
    # print(result) # 0.000000xxxx

    # consumer = await container.kafka_consumer().start()

    await asyncio.gather(
        serve_grpc(),  # gRPC-сервер
        asyncio.Future(),  # infinite cycle
    )


if __name__ == "__main__":
    asyncio.run(main())