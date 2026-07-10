from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str

    # MinIO
    MINIO_HOST: str = "minio"
    MINIO_PORT: int = 9000
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "taskflow-files"
    MINIO_SECURE: bool = False

    # Keycloak
    KEYCLOAK_URL: str = "http://keycloak:8080"
    KEYCLOAK_REALM: str = "taskflow"
    KEYCLOAK_CLIENT_ID: str = "taskflow-api"
    KEYCLOAK_CLIENT_SECRET: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()