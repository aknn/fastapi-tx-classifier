from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = Field(default="redis://localhost:6379/0")
    log_level: str = Field(default="INFO")
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=5000)
    testing: bool = Field(default=False)
    # MLflow tracking URI using local file store
    mlflow_tracking_uri: str = Field(default="file:./mlruns")
    mlflow_experiment_name: str = Field(
        default="classification_experiments"
    )  # Default experiment name

    class Config:
        env_file = ".env"

    @classmethod
    def for_testing(cls) -> "Settings":
        """Return settings configured for testing environment"""
        return cls(
            testing=True, redis_url="redis://localhost:6379/1"
        )  # Use a different DB for tests
