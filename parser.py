'''Разбор строки команды на слова с учетом кавычек'''


import shlex


def parse(line):
    '''Разбить строку на токены'''
    return shlex.split(line, posix=True)