#!/bin/bash
# Тест: --vfs и --script с упешным сценарием
cd "$(dirname "$0")"
python shell.py --vfs my_vfs.json --script test_ok.scr