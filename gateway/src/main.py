from fastapi import FastAPI
from api.v1 import users
from core.container import Container
import asyncio

app = FastAPI()
container = Container()
app.container = container
app.include_router(users.router)

@app.on_event("startup")
async def startup_event():
    producer = container.kafka_producer()
    await producer.start()

@app.on_event("shutdown")
async def shutdown_event():
    producer = container.kafka_producer()
    await producer.stop()
