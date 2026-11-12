import argparse
import sys
import os
from urllib.parse import urlparse
import urllib.request
import urllib.error
import json

# Блок 1: функции валидации параметров

def validate_package_name(name: str) -> str:
    if not name:
        raise argparse.ArgumentTypeError("Имя пакета не может быть пустым")

    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-_./@")
    if not all(c in allowed for c in name.lower()):
        raise argparse.ArgumentTypeError(
            f"Недопустимое имя пакета: {name}. "
            "Разрешены только строчные буквы, цифры, символы -, _, ., @, /"
        )
    return name

def validate_repo(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme in ("http", "https"):
        return value
    return value

def validate_depth(value: str) -> int:
    try:
        depth = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Глубина должна быть цулым числом, получено: {value}")

    if depth < 1:
        raise argparse.ArgumentTypeError(f"Глубина должна быть >= 1, получено: {depth}")

    return depth

# Блок 2: функции для работы с данными
def fetch_package_data(repo_url: str, package_name: str) -> dict:
    url = f"{repo_url.rstrip('/')}/{package_name}"

    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except urllib.error.HTTPError as e:
        print(f"Ошибка HTTP: {e.code}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Ошибка сети: {e.reason}", file=sys.stderr)
        sys.exit(1)

def get_direct_dependencies(package_data: dict, version: str) -> dict:
    if version == "latest":
        version = package_data.get("dist-tags", {}).get("latest")
        print(f"Выбрана последняя версия: {version}")

    versions = package_data.get("versions", {})
    if version not in versions:
        print(f"Ошибка: версия {version} не найдена для пакета {package_data.get('name')}", file=sys.stderr)
        sys.exit(1)

    dependencies = versions[version].get("dependencies", {})
    return dependencies, version

def load_test_graph(file_path: str) -> dict:
    graph = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split(':')
                if len(parts) != 2:
                    continue

                node = parts[0].strip()
                deps = parts[1].strip().split()
                graph[node] = deps
    except FileNotFoundError:
        print(f"Ошибка: тестовый файл не найден: {file_path}", file=sys.stderr)
        sys.exit(1)
    return graph

def build_graph_bfs(package_name: str, repo_url: str, mode: str, max_depth: int, filter_substring: str) -> dict:
    graph = {}
    queue = [(package_name, 0)]
    visited = set()
    test_graph = {}

    if mode == "test":
        test_graph = load_test_graph(repo_url)

    while queue:
        current_package, current_depth = queue.pop(0)

        if current_package in visited:
            continue

        visited.add(current_package)

        if filter_substring and filter_substring in current_package:
            continue

        dep_list = []
        if mode == "test":
            dep_list = test_graph.get(current_package, [])
        else:
            try:
                package_data = fetch_package_data(repo_url, current_package)
                deps, _ = get_direct_dependencies(package_data, "latest")
                dep_list = list(deps.keys())
            except Exception:
                dep_list = []
        graph[current_package] = dep_list

        if current_depth < max_depth:
            for dep in dep_list:
                if dep not in visited:
                    queue.append((dep, current_depth + 1))
    return graph


def get_load_order(graph: dict, root_package: str) -> list:
    order = []
    visited = set()
    visiting = set()

    def visit(node):
        if node in visited:
            return
        if node in visiting:
            print(f"Предупреждение: обнаружен цикл с участием пакета {node}. Порядок может быть неточным.",
                  file=sys.stderr)
            return
        visiting.add(node)

        for dep in graph.get(node, []):
            visit(dep)

        visiting.remove(node)
        visited.add(node)
        order.append(node)
    visit(root_package)
    return order

# Блок 3: настройка argparse

def parse_args(argv):
    parser = argparse.ArgumentParser(
    description="Визуализатор графа зависимостей для npm-пакетов.",
    formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--package", "-p",
        required=True,
        type=validate_package_name,
        help="Имя анализируемого пакета"
    )

    parser.add_argument(
        "--repo", "-r",
        required=True,
        type=validate_repo,
        help="URL реестра npm или путь к файлу тестового графа"
    )

    parser.add_argument(
        "--mode", "-m",
        choices=["real", "test"],
        default="real",
        help="Режим работы: real (через интернет) или test (локальный файл)"
    )

    parser.add_argument(
        "--version", "-v",
        default="latest",
        help="Версия пакета"
    )

    parser.add_argument(
        "--ascii", "-a",
        action="store_true",
        help="Вывести зависимости в виде ASCII-дерева"
    )

    parser.add_argument(
        "--depth", "-d",
        type=validate_depth,
        default=3,
        help="Максимальная глубина анализа зависимостей (по умолчанию: 3)"
    )

    parser.add_argument(
        "--filter", "-f",
        default="",
        help="Подстрока для исключения пакетов из анализа"
    )

    parser.add_argument(
        "--order", "-o", action="store_true",
        help="Вывести порядок загрузки зависимостей"
    )

    return parser.parse_args(argv)


# Блок 4: Главная функция программы

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_args(argv)

    print("Текущая конфигурация")
    print(f"Пакет: {args.package}")
    print(f"Репозиторий: {args.repo}")
    print(f"Режим работы: {args.mode}")
    print(f"Версия: {args.version}")
    print(f"ASCII-дерево: {args.ascii}")
    print(f"Глубина: {args.depth}")
    print(f"Фильтр: {args.filter}")

    if args.mode == "test" and not args.repo.startswith("http"):
        if not os.path.isfile(args.repo):
            print(f"Ошибка: для тестового режима требуется существующий файл, получено: {args.repo}", file=sys.stderr)
            return 1

    graph = build_graph_bfs(
        package_name=args.package,
        repo_url=args.repo,
        mode=args.mode,
        max_depth=args.depth,
        filter_substring=args.filter
    )
    print(f"Граф успешно построен. Найдено уникальных пакетов: {len(graph)}")

    print("\nСодержимое графа:")
    for node, dependencies in graph.items():
        if dependencies:
            print(f"{node} -> {', '.join(dependencies)}")
        else:
            print(f"{node} (нет зависимостей)")
    if args.order:
        print("Порядок загрузки зависимостей")
        load_order = get_load_order(graph, args.package)

        for i, pkg in enumerate(load_order, 1):
            print(f"{i}. {pkg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())