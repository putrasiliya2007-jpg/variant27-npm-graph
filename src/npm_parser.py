"""Получение npm-зависимостей напрямую по HTTP без npm и сторонних API-библиотек."""
import json
import urllib.error
import urllib.parse
import urllib.request


def fetch_npm_dependencies(package_name: str, repository_url: str) -> list[str]:
    """Читает package metadata из npm registry и возвращает прямые dependencies.

    repository_url может быть URL npm registry для пакета, например:
    https://registry.npmjs.org/lodash
    """
    url = repository_url.strip()
    if not url:
        raise ValueError("Не задан repository_url.")

    # Поддерживаем как базовый URL registry, так и URL конкретного пакета.
    encoded_name = urllib.parse.quote(package_name, safe="@")
    if url.rstrip("/").endswith("registry.npmjs.org"):
        url = url.rstrip("/") + "/" + encoded_name
    else:
        # Для обхода графа заменяем имя исходного пакета в URL на имя текущего.
        # Так один шаблон URL подходит для всех пакетов графа.
        parsed = urllib.parse.urlsplit(url)
        path = parsed.path.rstrip("/")
        original_encoded = urllib.parse.quote(package_name, safe="@")
        if path.endswith("/" + original_encoded):
            path = path[:-(len(original_encoded))] + encoded_name
        elif path.rsplit("/", 1)[-1] != encoded_name:
            path = path + "/" + encoded_name
        url = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, parsed.fragment))

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "variant27-dependency-visualizer/1.0",
                 "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            metadata = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP-ошибка при получении npm metadata: {exc.code} {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Не удалось подключиться к репозиторию: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("Сервер вернул некорректный JSON.") from exc

    # Registry package document содержит dependencies в выбранной latest-версии.
    version = metadata.get("dist-tags", {}).get("latest")
    versions = metadata.get("versions", {})
    version_data = versions.get(version, {}) if version else {}
    dependencies = version_data.get("dependencies", {})
    if not isinstance(dependencies, dict):
        raise RuntimeError("В npm metadata поле dependencies имеет неверный формат.")
    return sorted(dependencies.keys())
