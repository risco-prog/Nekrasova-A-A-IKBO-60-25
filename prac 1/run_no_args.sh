#!/bin/bash
# Тест: ни одного параметра — используются значения по умолчанию
cd "$(dirname "$0")"
printf 'ls\nexit\n' | python shell.py