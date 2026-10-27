'''Эмулятор shell. Этап 1: REPL.'''


import os
import sys

from commands import COMMANDS
from config import parse_args
from parser import parse


def execute_line(state, line):
    '''Выполнить одну строку. Возвращает код ошибки (0 - успех).'''
    line = line.strip()
    if not line:
        return 0

    try:
        tokens = parse(line)
    except ValueError as exc:
        print(f"parse error: {exc}", file=sys.stderr)
        return 1

    if not tokens:
        return 0

    name, *args = tokens
    handler = COMMANDS.get(name)
    if handler is None:
        print(f"{name}: command not found", file=sys.stderr)
        return 1

    try:
        return handler(state, args)
    except ValueError as exc:
        print(f"{name}: {exc}", file=sys.stderr)
        return 1


def run_script(state, script_path):
    '''Выполняет стартовый скрипт. Останавливается при первой ошибке.'''
    try:
        with open(script_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except OSError as exc:
        print(f"Ошибка чтения скрипта: {exc}", file=sys.stderr)
        return

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        print(f"{state['prompt']}{line}")

        error_code = execute_line(state, line)

        if error_code != 0:
            print("Скрипт остановлен из-за ошибки.", file=sys.stderr)
            break


def repl(state):
    '''Основной цикл'''
    while state["running"]:
        try:
            line = input(state["prompt"])
        except (EOFError, KeyboardInterrupt):
            print()
            break
        execute_line(state, line)


def main():
    '''Точка входа'''
    args = parse_args()

    print("Отладка: параметры запуска")
    print(f"Путь к VFS: {args.vfs}")
    print(f"Путь к скрипту: {args.script}")

    vfs_name = os.path.basename(args.vfs).replace(".json", "")

    state = {
        "running": True,
        "promt": f"[{vfs_name}]$ "
    }

    if args.script:
        run_script(state, args.script)

    if state["running"]:
        repl(state)


if __name__ == "__main__":
    main()