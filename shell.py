# Эмулятор shell. Этап 1: REPL.


import sys


from commands import COMMANDS
from parser import parse


PROMT = "vfs$ "


def execute_line(line):
    # Выполнить одну строку. Вернуть True, если продолжаем.
    line = line.strip()
    if not line:
        return True


    try:
        tokens = parse(line)
    except ValueError as exc:
        print(f"parse error: {exc}", file=sys.stderr)
        return True

    if not tokens:
        return True

    name, *args = tokens
    handler = COMMANDS.get(name)
    if handler is None:
        print(f"{name}: command not found", file=sys.stderr)
        return True

    try:
        return handler(args)
    except ValueError as exc:
        print(f"{name}: {exc}", file=sys.stderr)
        return True



def repl():
    # Основной цикл
    running = True
    while running:
        try:
            line = input(PROMT)
        except (EOFError, KeyboardInterrupt):
            print()
            break
        running = execute_line(line)


if __name__ == "__main__":
    repl()