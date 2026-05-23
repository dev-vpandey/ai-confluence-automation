from pathlib import Path
import yaml

_config_path = Path(__file__).parent.parent / "config.yaml"
_raw = yaml.safe_load(_config_path.read_text()) if _config_path.exists() else {}


def _get(section: str, key: str, default):
    return _raw.get(section, {}).get(key, default)


BASE_URL = _get("confluence", "base_url", "https://confluence.ops.expertcity.com")
SESSION_FILE = Path(_get("confluence", "session_file", "~/.confluence-session")).expanduser()

TIMEOUT_HEALTH = _get("timeouts", "health_check", 5)
TIMEOUT_SEARCH = _get("timeouts", "search", 10)
TIMEOUT_CREATE = _get("timeouts", "create_page", 30)
