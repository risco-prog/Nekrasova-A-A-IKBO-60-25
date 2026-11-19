import argparse
import sys
import os
from urllib.parse import urlparse
import urllib.request
import urllib.error
import json

MIN_DEPTH = 1
START_DEPTH = 0


def validate_package_name(name: str) -> str:
    """Проверяет имя пакета на допустимые символы"""
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
    """Проверяет URL или локальный путь"""
    parsed = urlparse(value)
    if parsed.scheme in ("http", "https"):
        return value
    return value


def validate_depth(value: str) -> int:
    """Проверяет, что глубина - целое число >= 1"""
    try:
        depth = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Глубина должна быть цулым числом, "
                                         f"получено: {value}")

    if depth < MIN_DEPTH:
        raise argparse.ArgumentTypeError(f"Глубина должна быть >= 1, "
                                         f"получено: {depth}")

    return depth


def fetch_package_data(repo_url: str, package_name: str) -> dict:
    """Скачивает JSON с данными о пакете из реестра npm"""
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
    """Извлекает прямые зависимости для указанной версии"""
    if version == "latest":
        version = package_data.get("dist-tags", {}).get("latest")
        print(f"Выбрана последняя версия: {version}")

    versions = package_data.get("versions", {})
    if version not in versions:
        print(f"Ошибка: версия {version} не найдена для пакета "
              f"{package_data.get('name')}", file=sys.stderr)
        sys.exit(1)

    dependencies = versions[version].get("dependencies", {})
    return dependencies, version


def load_test_graph(file_path: str) -> dict:
    """Загружает тестовый граф из текстового файла"""
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


def get_package_dependencies(current_package, mode, test_graph, repo_url):
    """Получает список зависимостей для одного пакета"""
    if mode == "test":
        return test_graph.get(current_package, [])
    else:
        try:
            package_data = fetch_package_data(repo_url, current_package)
            deps, _ = get_direct_dependencies(package_data, "latest")
            return list(deps.keys())
        except Exception:
            return []


def build_graph_bfs(package_name: str, repo_url: str,
                    mode: str, max_depth: int, filter_substring: str) -> dict:
    """Строит граф зависимостей алгоритмом BFS"""
    graph = {}
    queue = [(package_name, START_DEPTH)]
    visited = set()

    test_graph = load_test_graph(repo_url) if mode == "test" else {}

    while queue:
        current_package, current_depth = queue.pop(0)

        if current_package in visited:
            continue

        visited.add(current_package)

        if filter_substring and filter_substring in current_package:
            continue

        dep_list = get_package_dependencies(current_package, mode, test_graph,
                                            repo_url)
        graph[current_package] = dep_list

        if current_depth < max_depth:
            for dep in dep_list:
                if dep not in visited:
                    queue.append((dep, current_depth + 1))
    return graph


def get_load_order(graph: dict, root_package: str) -> list:
    """Возвращает порядок загрузки"""
    order = []
    visited = set()
    visiting = set()

    def visit(node):
        if node in visited:
            return
        if node in visiting:
            print(f"Предупреждение: обнаружен цикл с участием пакета {node}."
                  f" Порядок может быть неточным.",
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


def generate_plantuml(graph: dict) -> str:
    """Генерирует текстовое представление графа для PlantUML"""
    lines = ["@startuml", "skinparam defaultFontName Monospaced"]
    for node, dependencies in graph.items():
        if not dependencies:
            lines.append(f'package "{node}"')
        else:
            for dep in dependencies:
                lines.append(f'"{node}" --> "{dep}"')
    lines.append("@enduml")
    return "\n".join(lines)


def print_ascii_tree(graph: dict, node: str,
                     prefix: str = "", is_last: bool = True,
                     visited: set = None, is_root: bool = True):
    """Рекурсивно печатает ASCII-дерево зависимостей"""
    if visited is None:
        visited = set()

    if node in visited:
        print(f"{prefix}{'`-- ' if is_last else '|-- '}{node} (цикл)")
        return

    visited.add(node)

    if is_root:
        print(node)
    else:
        connector = "`-- " if is_last else "|-- "
        print(f"{prefix}{connector}{node}")

    if is_root:
        child_prefix = ""
    else:
        child_prefix = prefix + ("    " if is_last else "│   ")

    dependencies = graph.get(node, [])
    for i, dep in enumerate(dependencies):
        is_last_child = (i == len(dependencies) - 1)
        print_ascii_tree(graph, dep, child_prefix, is_last_child,
                         visited, is_root=False)


def parse_args(argv):
    """Настраивает и парсит аргументы коммандной строки"""
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей для npm-пакетов.",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("--package", "-p", required=True,
                        type=validate_package_name,
                        help="Имя анализируемого пакета")

    parser.add_argument("--repo", "-r", required=True, type=validate_repo,
                        help="URL реестра npm или путь к файлу тестового графа")

    parser.add_argument("--mode", "-m", choices=["real", "test"],
                        default="real",
                        help="Режим работы: real (через интернет) "
                             "или test (локальный файл)")

    parser.add_argument("--version", "-v", default="latest",
                        help="Версия пакета")

    parser.add_argument("--ascii", "-a", action="store_true",
                        help="Вывести зависимости в виде ASCII-дерева")

    parser.add_argument("--depth", "-d", type=validate_depth,
                        default=3, help="Максимальная глубина анализа "
                                        "зависимостей (по умолчанию: 3)")

    parser.add_argument("--filter", "-f", default="",
                        help="Подстрока для исключения пакетов из анализа")

    parser.add_argument("--order", "-o", action="store_true",
                        help="Вывести порядок загрузки зависимостей")

    return parser.parse_args(argv)


def main(argv=None):
    """Главная функция программы"""
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
            print(f"Ошибка: для тестового режима требуется существующий файл, "
                  f"получено: {args.repo}", file=sys.stderr)
            return 1
    graph = build_graph_bfs(
        package_name=args.package, repo_url=args.repo,
        mode=args.mode, max_depth=args.depth,
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
    print("\nВизуализация в формате PlantUML")
    print(generate_plantuml(graph))
    if args.ascii:
        print("\nASCII-дерево зависимостей")
        print_ascii_tree(graph, args.package, is_last=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
