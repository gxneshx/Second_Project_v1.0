"""The application configuration module.

This module defines the AppConfig class, which loads application settings from
environment variables using Pydantic. It supports configurable paths for image
storage, logging, allowed file formats, and file size limits.

Side effects:
    - Reads and parses environment variables from the `.env` file during import.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# The base directory for resolving relative paths
BASE_DIR = Path(__file__).parent.parent.parent

class AppConfig(BaseSettings):
    """The application settings loaded from environment variables.

        Attributes:
            IMAGES_DIR (str): The directory path where uploaded images are stored.
            WEB_SERVER_WORKERS (int): The number of worker processes to run for the HTTP server.
            WEB_SERVER_START_PORT (int): The starting port number for worker processes.
            LOG_DIR (Path): The directory path where log files are saved.
            MAX_FILE_SIZE (int): Maximum allowed size of uploaded files (in bytes).
            SUPPORTED_FORMATS (set[str]): A set of allowed file extensions.
    """

    IMAGES_DIR: str # = f"{BASE_DIR.parent.parent}/images"
    WEB_SERVER_WORKERS: int
    WEB_SERVER_START_PORT: int
    LOG_DIR: Path = f"{BASE_DIR.parent.parent}/logs"

    MAX_SIZE: int = 5 * 1024 * 1024
    SUPPORTED_FORMATS: set[str] = {'.jpg', '.png', '.gif'}

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra='ignore'
    )

# The global application config instance
config = AppConfig()