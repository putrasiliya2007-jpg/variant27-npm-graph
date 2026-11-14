"""CLI-приложение для визуализации графа npm-зависимостей."""
import argparse
from pathlib import Path
import subprocess
import sys

from src.config import load_config
from src.graph import build_graph_bfs_recursive, load_test_graph, reverse_dependencies, to_d2
from src.npm_parser import fetch_npm_dependencies


def main():
    parser = argparse.ArgumentParser(description="Визуализатор графа зависимостей npm-пакетов")
    parser.add_argument("-c", "--config", default="config.yaml", help="путь к YAML-конфигурации")
    parser.add_argument("--show-config", action="store_true", help="вывести параметры конфигурации")
    parser.add_argument("--reverse", action="store_true", help="показать обратные зависимости")
    args = parser.parse_args()

    try:
        config = load_config(args.config)
        if args.show_config:
            print("Параметры конфигурации:")
            for key in ("package_name", "repository_url", "test_repository_file",
                        "test_mode", "max_depth", "show_reverse"):
                print(f"{key}: {config.get(key)}")

        if config["test_mode"]:
            test_graph = load_test_graph(config["test_repository_file"])
            if config["package_name"] not in test_graph:
                raise ValueError(f"Пакет {config['package_name']} отсутствует в тестовом графе.")

            def dependency_provider(name):
                return test_graph.get(name, [])
        else:
            cache = {}

            def dependency_provider(name):
                if name not in cache:
                    cache[name] = fetch_npm_dependencies(name, config["repository_url"])
                return cache[name]

        root = config["package_name"]
        direct = dependency_provider(root)
        print(f"\nПрямые зависимости пакета {root}:")
        print("\n".join(f"  - {item}" for item in direct) if direct else "  (нет прямых зависимостей)")

        graph = build_graph_bfs_recursive(root, dependency_provider, config["max_depth"])
        print("\nГраф зависимостей:")
        for package, dependencies in sorted(graph.items()):
            print(f"{package} -> {', '.join(dependencies) if dependencies else '(нет / достигнута глубина)'}")

        if args.reverse or config["show_reverse"]:
            print(f"\nОбратные зависимости пакета {root}:")
            reverse = reverse_dependencies(graph, root)
            print("\n".join(f"  - {item}" for item in reverse) if reverse else "  (не найдены)")

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        d2_path = output_dir / f"{root.replace('/', '_')}_dependencies.d2"
        svg_path = output_dir / f"{root.replace('/', '_')}_dependencies.svg"
        d2_path.write_text(to_d2(graph), encoding="utf-8")
        print(f"\nФайл диаграммы D2 сохранён: {d2_path}")

        try:
            subprocess.run(["d2", str(d2_path), str(svg_path)], check=True)
            print(f"Изображение графа сохранено: {svg_path}")
        except FileNotFoundError:
            print("Команда d2 не найдена. Установите D2 (инструкция в README.md), затем повторите запуск.")
        except subprocess.CalledProcessError as exc:
            print(f"D2 не смог построить изображение (код {exc.returncode}).")
        return 0
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
