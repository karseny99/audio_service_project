from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from core.container import Container
from core.kafka_producer import KafkaProducer

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register")
@inject
async def register_user(
    username: str,
    email: str,
    password: str,
    producer: KafkaProducer = Depends(Provide[Container.kafka_producer])
):
    try:
        event = {
            "event_type": "user_registered",
            "data": {
                "username": username,
                "email": email,
                "password": password
            }
        }
        await producer.send("user_events", event)
        return {"status": "event_published"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
