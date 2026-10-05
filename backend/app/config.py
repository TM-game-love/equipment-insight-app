from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Equipment Insight API"
    api_prefix: str = "/api"
    frontend_origin: str = "http://localhost:3000"
    mock_mode: bool = True
    mock_csv_path: str = "mock_data/period_features_3months.csv"

    db1_url: str
    db2_url: str
    db3_url: str
    db4_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

settings = Settings()
