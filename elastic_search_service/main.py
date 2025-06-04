import asyncio
import uvloop 
from src.core.di import Container
from src.infrastructure.grpc.server import serve_grpc
from src.core.logger import logger

async def main():
    await Container.init_resources()

    try:
        await serve_grpc()
    finally:
        await Container.shutdown_resources()

if __name__ == "__main__":
    uvloop.install()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
