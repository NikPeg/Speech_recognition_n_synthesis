#!/usr/bin/env python3
"""Тестовый скрипт для обработки только lec1.docx"""

import sys
sys.path.insert(0, '.')

from convert_docx_to_txt import convert_docx_to_txt

if __name__ == '__main__':
    convert_docx_to_txt('lec1.docx', 'lec1.txt')
    print("\nТест завершен! Проверьте файл lec1.txt")

