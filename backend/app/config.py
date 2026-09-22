import os


class Settings:
    DATABASE_URL: str = os.environ["DATABASE_URL"]

    # DEV-ONLY fixed OTP — must be explicitly enabled via env var.
    # This flag is OFF in docker-compose.yml and must never be true in production.
    DEV_FIXED_OTP_ENABLED: bool = (
        os.environ.get("DEV_FIXED_OTP_ENABLED", "false").strip().lower() == "true"
    )
    DEV_FIXED_OTP_VALUE: str = os.environ.get("DEV_FIXED_OTP_VALUE", "000000")

    RATE_LIMIT_AUTH_PER_MINUTE: int = int(
        os.environ.get("RATE_LIMIT_AUTH_PER_MINUTE", "5")
    )
    RATE_LIMIT_OTP_PER_MINUTE: int = int(
        os.environ.get("RATE_LIMIT_OTP_PER_MINUTE", "3")
    )


settings = Settings()
