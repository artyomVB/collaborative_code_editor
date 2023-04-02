from pydantic import BaseSettings


class DBSettings(BaseSettings):
    host: str
    port: int
    login: str
    password: str
    name: str

    class Config:
        env_prefix = "DB_"
        env_file = ".env"
