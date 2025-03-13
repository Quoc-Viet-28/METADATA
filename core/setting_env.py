from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    ENVIRONMENT: str = "prod"
    PORT: int = 8001
    MINIO_PROTOCOL: str = "https"
    QUALITY_IMAGE: int = 50

    MONGO_DATABASE_URI: str
    MONGO_DATABASE: str

    MINIO_SERVER: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    BUCKET: str

    URL_KEYCLOAK: str
    REALM_KEYCLOAK: str
    CLIENT_ID_KEYCLOAK: str
    CLIENT_SECRET_KEYCLOAK: str



settings = Settings()
