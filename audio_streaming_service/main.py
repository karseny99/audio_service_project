import asyncio
from src.infrastructure.grpc.server import serve_grpc
from src.core.di import Container
from src.core.logger import logger
from functools import wraps

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
    
    await asyncio.gather(
        serve_grpc(),
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application shutdown by user")