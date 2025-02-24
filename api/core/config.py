from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    GITHUB_APP_PRIVATE_KEY:str
    GEMINI_API_KEY:str
    
    model_config=SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    
Config=Settings()    
    