"""Загрузка и проверка YAML-конфигурации."""
from pathlib import Path
import yaml


REQUIRED_KEYS = (
    "package_name",
    "repository_url",
    "test_repository_file",
    "test_mode",
    "max_depth",
)


def load_config(path: str = "config.yaml") -> dict:
    config_path = Path(path)
    if not config_path.is_file():
        raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")

    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"Некорректный YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("Конфигурация должна быть YAML-словарём.")

    missing = [key for key in REQUIRED_KEYS if key not in data]
    if missing:
        raise ValueError("Отсутствуют параметры: " + ", ".join(missing))

    name = data["package_name"]
    if not isinstance(name, str) or not name.strip():
        raise ValueError("package_name должен быть непустой строкой.")

    url = data["repository_url"]
    if not isinstance(url, str):
        raise ValueError("repository_url должен быть строкой.")
    if not data["test_mode"] and not url.startswith(("https://", "http://")):
        raise ValueError("Для реального режима repository_url должен начинаться с http:// или https://.")

    test_file = data["test_repository_file"]
    if not isinstance(test_file, str) or not test_file.strip():
        raise ValueError("test_repository_file должен быть непустым путём.")

    test_mode = data["test_mode"]
    if not isinstance(test_mode, bool):
        raise ValueError("test_mode должен иметь значение true или false.")

    depth = data["max_depth"]
    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 0:
        raise ValueError("max_depth должен быть целым числом не меньше 0.")

    show_reverse = data.get("show_reverse", False)
    if not isinstance(show_reverse, bool):
        raise ValueError("show_reverse должен иметь значение true или false.")

    data["package_name"] = name.strip()
    data["repository_url"] = url.strip()
    data["test_repository_file"] = test_file.strip()
    data["show_reverse"] = show_reverse
    return data
