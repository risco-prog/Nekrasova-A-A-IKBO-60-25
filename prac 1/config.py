# Настройка параметров командной строки.

import argparse


def parse_args():
    # Разбирает аргументы, переданные при запуске программы
    parser = argparse.ArgumentParser(description="Эмулятор shell. Этап 2.")
    parser.add_argument(
        "--vfs",
        default="vfs.json",
        help="Путь к файлу виртуальной файловой системы (VFS)"
    )
    parser.add_argument(
        "--script",
        default=None,
        help="Путь к стартовому скрипту для выполнения"
    )
    return parser.parse_args()
