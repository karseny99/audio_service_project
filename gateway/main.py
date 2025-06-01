from src.core.middleware.auth import AuthMiddleware
import random


from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from src.core.container import Container
from src.api.v1.auth import router as auth_router
from src.api.v1.users import router as users_router
from src.api.v1.streaming import router as streaming_router
import uvicorn

app = FastAPI(title="API Gateway")
container = Container()
app.container = container
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(streaming_router)
app.add_middleware(AuthMiddleware)



templates = Jinja2Templates(directory="templates")

@app.get("/")
async def get_player(request: Request):
    return templates.TemplateResponse("player.html", {"request": request})

if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True,
        reload=True,
    )