from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    token: SecretStr
    address_blacklist: list[str] = ["street", "house"]

class DatabaseSettings(BaseSettings):
    db_url: str = "sqlite+aiosqlite:///./dev.db"

class Settings(BaseSettings):
    bot: BotSettings
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore"
    )

env = Settings() # noqa