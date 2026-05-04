import os
import time
import configparser

from api_server import start_api_server


def _load_config_env(path: str = "config.ini") -> str | None:
    cfg = configparser.ConfigParser()
    if not os.path.exists(path):
        return os.getenv("ERP_API_TOKEN", "").strip() or None
    cfg.read(path)
    token = None
    if cfg.has_section("api"):
        token = cfg.get("api", "ERP_API_TOKEN", fallback="").strip() or None
        expose = cfg.get("api", "ERP_API_EXPOSE_NETWORK", fallback="").strip().lower()
        if expose in {"1", "true", "yes", "on"}:
            os.environ["ERP_API_EXPOSE_NETWORK"] = "true"
        else:
            os.environ.pop("ERP_API_EXPOSE_NETWORK", None)

    # Respect existing environment variable if set; otherwise set from config
    if not os.getenv("ERP_API_TOKEN", "").strip() and token:
        os.environ["ERP_API_TOKEN"] = token
    return os.getenv("ERP_API_TOKEN", "").strip() or None


if __name__ == "__main__":
    token = _load_config_env("config.ini")
    start_api_server(port=5000, token=token)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
