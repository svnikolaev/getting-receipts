from pydantic import BaseSettings


class Settings(BaseSettings):
    HOST: str
    ACCEPT: str
    DEVICE_OS: str
    DEVICE_ID: str
    ACCEPT_LANGUAGE: str
    USER_AGENT: str
    CLIENT_SECRET: str
    OS: str
    CONNECTION_TIMEOUT: int
    VERBOSE: bool = False
    DATABASE_URL: str = 'sqlite:///default.db'

    def get_headers(self):
        return {
            'Host': self.HOST,
            'Accept': self.ACCEPT,
            'Device-OS': self.DEVICE_OS,
            'Device-Id': self.DEVICE_ID,
            'Accept-Language': self.ACCEPT_LANGUAGE,
            'User-Agent': self.USER_AGENT,
        }

    class Config:
        # `.env.prod` takes priority over `.env`
        env_file = '.env', '.env.prod'
        env_file_encoding = 'utf-8'


def get_settings():
    return Settings()
