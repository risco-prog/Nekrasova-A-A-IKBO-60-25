# Команды этапа 1 — пока заглушки.


def cmd_ls(args):
    # Заглушка ls: печатает имя и аргументы.
    print(f"ls: called with args: {args}")
    return True


def cmd_cd(args):
    # Заглушка cd: печатает имя и аргументы.
    print(f"cd: called with args: {args}")
    return True


def cmd_exit(args):
    # Выход: С аргументами - ошибка
    if args:
        raise ValueError("exit takes no arguments")
    return False


COMMANDS = {
    "ls" : cmd_ls,
    "cd" : cmd_cd,
    "exit" : cmd_exit
}