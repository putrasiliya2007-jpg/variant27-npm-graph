"""Построение графа зависимостей: BFS, реализованный рекурсивной обработкой очереди."""
from collections import deque
import json
from pathlib import Path


def load_test_graph(path: str) -> dict[str, list[str]]:
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Файл тестового графа не найден: {file_path}")
    try:
        raw = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Некорректный JSON тестового графа: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError("Тестовый граф должен быть JSON-объектом.")
    graph = {}
    for package, dependencies in raw.items():
        if not isinstance(package, str) or not package.isalpha() or not package.isupper():
            raise ValueError(f"Имя тестового пакета '{package}' должно состоять из заглавных латинских букв.")
        if not isinstance(dependencies, list) or any(not isinstance(x, str) for x in dependencies):
            raise ValueError(f"Зависимости пакета {package} должны быть списком строк.")
        for dependency in dependencies:
            if not dependency.isalpha() or not dependency.isupper():
                raise ValueError(f"Имя тестовой зависимости '{dependency}' должно состоять из заглавных латинских букв.")
        graph[package] = dependencies[:]
    # Добавляем узлы, встречающиеся только как зависимости.
    for deps in list(graph.values()):
        for dep in deps:
            graph.setdefault(dep, [])
    return graph


def build_graph_bfs_recursive(root: str, get_dependencies, max_depth: int) -> dict[str, list[str]]:
    """Строит достижимую часть графа. Очередь BFS обрабатывается рекурсивно."""
    if max_depth < 0:
        raise ValueError("max_depth не может быть отрицательной.")
    graph: dict[str, list[str]] = {}
    visited_depth: dict[str, int] = {}
    queue = deque([(root, 0)])

    def process_queue():
        if not queue:
            return
        package, depth = queue.popleft()
        # Один пакет может быть найден более коротким путём; повторно обходим,
        # только если новая глубина меньше ранее известной.
        if package in visited_depth and visited_depth[package] <= depth:
            process_queue()
            return
        visited_depth[package] = depth
        dependencies = sorted(set(get_dependencies(package))) if depth < max_depth else []
        graph[package] = dependencies
        for dependency in dependencies:
            if dependency not in visited_depth or depth + 1 < visited_depth[dependency]:
                queue.append((dependency, depth + 1))
        process_queue()

    process_queue()
    return graph


def reverse_dependencies(graph: dict[str, list[str]], target: str) -> list[str]:
    """Возвращает пакеты, которые прямо или транзитивно зависят от target."""
    reverse = {node: [] for node in graph}
    for package, dependencies in graph.items():
        for dependency in dependencies:
            reverse.setdefault(dependency, []).append(package)

    result, visited = [], set()
    queue = deque(reverse.get(target, []))
    while queue:
        package = queue.popleft()
        if package == target or package in visited:
            continue
        visited.add(package)
        result.append(package)
        queue.extend(reverse.get(package, []))
    return sorted(result)


def to_d2(graph: dict[str, list[str]]) -> str:
    lines = ["direction: right", ""]
    for package in sorted(graph):
        if not graph[package]:
            lines.append(f'"{package}"')
        for dependency in sorted(graph[package]):
            lines.append(f'"{package}" -> "{dependency}"')
    return "\n".join(lines) + "\n"
