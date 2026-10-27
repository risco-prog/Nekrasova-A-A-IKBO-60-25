#!/bin/bash
# Тест: передан только --vfs, запускается REPL
cd "$(dirname "$0")"
printf 'ls\ncd /tmp\nexit\n' | python shell.py --vfs my_vfs.json