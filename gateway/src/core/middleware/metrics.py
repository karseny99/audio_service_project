import time
from fastapi import Request
from src.core.monitoring import REQUEST_COUNT, REQUEST_DURATION

async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Извлекаем имя эндпоинта (например: "/api/v1/users")
    endpoint = request.scope.get("route").path if hasattr(request.scope, "route") else "unknown"
    
    # Регистрируем метрики
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        http_status=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=endpoint
    ).observe(duration)
    
    return response