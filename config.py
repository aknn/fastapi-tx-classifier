from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    app_host: str = Field("0.0.0.0", env="APP_HOST")
    app_port: int = Field(5000, env="APP_PORT")
    testing: bool = Field(False, env="TESTING")
    # MLflow tracking URI using local file store
    mlflow_tracking_uri: str = Field("file:./mlruns", env="MLFLOW_TRACKING_URI")
    mlflow_experiment_name: str = Field(
        "classification_experiments", env="MLFLOW_EXPERIMENT_NAME"
    )  # Default experiment name

    class Config:
        env_file = ".env"

    @classmethod
    def for_testing(cls):
        """Return settings configured for testing environment"""
        return cls(
            testing=True, redis_url="redis://localhost:6379/1"
        )  # Use a different DB for tests
