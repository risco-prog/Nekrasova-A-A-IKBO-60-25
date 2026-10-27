'''Команды этапа 2 — пока заглушки.'''


def cmd_ls(state, args):
    '''Заглушка ls: печатает имя и аргументы.'''
    print(f"ls: called with args: {args}")
    return 0


def cmd_cd(state, args):
    '''Заглушка cd: печатает имя и аргументы.'''
    print(f"cd: called with args: {args}")
    return 0


def cmd_exit(state, args):
    '''Выход: С аргументами - ошибка'''
    if args:
        raise ValueError("exit takes no arguments")
    state["running"] = False
    return 0


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit
}