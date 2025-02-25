from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_API_KEY:str
    GITHUB_APP_ID :str
    GITHUB_PRIVATE_KEY:str  
    
    model_config=SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    
Config=Settings()    
    