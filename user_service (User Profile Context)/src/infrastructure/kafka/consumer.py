@broker.subscriber("user_events")
async def on_user_registered(msg: bytes):
    data = deserialize_user_registered(msg)  # Protobuf → Python dict
    user = User(id=data["user_id"], email=data["email"])
    await user_repository.save(user)
    KAFKA_EVENTS_PROCESSED.labels(topic="user_events").inc()
