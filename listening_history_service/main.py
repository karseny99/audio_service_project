import asyncio
from functools import wraps

from src.infrastructure.grpc.server import serve_grpc
from src.infrastructure.kafka.consumer import KafkaConsumer
from src.core.di import Container
from src.core.logger import logger

# def with_kafka_cleanup(main_func):
#     @wraps(main_func)
#     async def wrapper():
#         container = Container()
#         try:
#             await main_func()
#         finally:
#             publisher = container.kafka_publisher()
#             await publisher.disconnect()
#             logger.info("Kafka publisher disconnected")
#     return wrapper


# @with_kafka_cleanup
async def main():
    container = Container()
    container.wire(modules=["src.infrastructure.grpc.server"])

    # consumer = await container.kafka_consumer().start()

    await asyncio.gather(
        serve_grpc(),  # gRPC-сервер
        asyncio.Future(),  # infinite cycle
    )

if __name__ == "__main__":
    asyncio.run(main())