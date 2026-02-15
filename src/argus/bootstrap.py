import io
import logging
import sys
from pathlib import Path

from dotenv import find_dotenv, load_dotenv


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def setup_environment() -> Path:
    root = project_root()
    if getattr(sys, "frozen", False):
        base_path = Path(sys.executable).resolve().parent
    else:
        base_path = root

    env_path = base_path / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv(find_dotenv())

    if sys.platform == "win32":
        if sys.stdout is not None:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        if sys.stderr is not None:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    return root
