from collections import deque
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import FastAPI, Request
from time import monotonic


class CustomRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, limits: dict):
        super().__init__(app)
        self.limits = limits
        self.request_counts = {}  # key -> deque of timestamps

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path not in self.limits:
            return await call_next(request)

        rate, period = self.limits[path]
        
        client = request.headers.get(
            "x-forwarded-for", request.client.host).split(",")[0].strip()
        key = f"{client}:{path}:{request.method}"

        bucket = self.request_counts.get(key)
        if bucket is None:
            bucket = deque(maxlen=rate)
            self.request_counts[key] = bucket

        now = monotonic()
        # purge oldest outside the window
        while bucket and (now - bucket[0]) >= period:
            bucket.popleft()

        if len(bucket) >= rate:
            retry_after = max(0, int(period - (now - bucket[0])))
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(rate),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(retry_after),
                },
            )

        bucket.append(now)
        resp = await call_next(request)
        resp.headers["X-RateLimit-Limit"] = str(rate)
        resp.headers["X-RateLimit-Remaining"] = str(rate - len(bucket))
        return resp


