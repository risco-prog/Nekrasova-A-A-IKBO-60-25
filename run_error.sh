#!/bin/bash
# Тест: скрипт должен остановиться на bad_command
cd "$(dirname "$0")"
python shell.py --vfs my_vfs.json --script test_error.scr