import asyncio
from src.infrastructure.grpc.server import serve_grpc
from src.core.di import Container
from src.core.logger import logger
from functools import wraps

def with_kafka_cleanup(main_func):
    @wraps(main_func)
    async def wrapper():
        container = Container()
        try:
            await main_func()
        finally:
            publisher = container.kafka_publisher()
            await publisher.disconnect()
            logger.info("Kafka publisher disconnected")
    return wrapper


@with_kafka_cleanup
async def main():
    # Dependency injection before start up
    container = Container()
    container.wire(modules=["src.infrastructure.grpc.server"])

    await container.kafka_publisher().connect()

    await asyncio.gather(
        serve_grpc(),  # gRPC-сервер
        # app.run()      # Kafka-консьюмер
    )

container = Container()
container.wire(modules=["src.infrastructure.grpc.server"])
asyncio.run(main())