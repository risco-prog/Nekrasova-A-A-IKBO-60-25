import argparse
import sys
import os
from urllib.parse import urlparse

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

# Блок 2: настройка argparse

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


# Блок 3: Главная функция программы

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
    return 0


if __name__ == "__main__":
    sys.exit(main())