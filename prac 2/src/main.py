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
    if args.mode == "real":
        package_data = fetch_package_data(args.repo, args.package)
        deps, exact_version = get_direct_dependencies(package_data, args.version)

        if not deps:
            print(f"У пакета {args.package} (версия {exact_version}) нет прямых зависимостей.")
        else:
            print(f"Прямые зависимости пакета {args.package} (версия {exact_version}):")
            for dep_name, dep_version in deps.items():
                print(f"{dep_name} (требуется версия: {dep_version})")
    return 0


if __name__ == "__main__":
    sys.exit(main())