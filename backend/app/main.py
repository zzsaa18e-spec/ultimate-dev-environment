from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from app.config import settings

app = FastAPI(title="App Backend")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/auth/login")
@limiter.limit(f"{settings.RATE_LIMIT_AUTH_PER_MINUTE}/minute")
async def login(request: Request, phone: str):
    # Placeholder — real impl sends OTP to phone
    return {"detail": "OTP sent"}


@app.post("/otp/verify")
@limiter.limit(f"{settings.RATE_LIMIT_OTP_PER_MINUTE}/minute")
async def verify_otp(request: Request, phone: str, otp: str):
    if settings.DEV_FIXED_OTP_ENABLED and otp == settings.DEV_FIXED_OTP_VALUE:
        return {"token": "dev-token"}
    # Placeholder — real impl validates OTP from DB/cache
    return {"detail": "OTP verified"}
