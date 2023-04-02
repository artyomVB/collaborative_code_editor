from pydantic import BaseSettings


class RabbitSettings(BaseSettings):
    host: str
    port: int
    login: str
    password: str

    class Config:
        env_prefix = "RABBIT_"
        env_file = '.env'