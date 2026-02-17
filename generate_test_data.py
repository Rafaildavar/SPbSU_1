#!/usr/bin/env python3
"""
Генератор тестовых данных для задачи подсчета уникальных IPv6 адресов.

Использование:
    python generate_test_data.py <output_file> [num_lines]
    
Примеры:
    python generate_test_data.py test_input.txt 1000
    python generate_test_data.py large_input.txt 100000000
"""

import sys
import random


def generate_random_ipv6() -> str:
    """
    Генерирует случайный IPv6 адрес в различных форматах записи.
    
    Returns:
        IPv6 адрес в случайном формате (может содержать ::, ведущие нули, разный регистр)
    """
    # Генерируем 8 групп по 4 hex цифры
    groups = []
    for _ in range(8):
        value = random.randint(0, 0xFFFF)
        # Иногда используем сокращенную форму (без ведущих нулей)
        if random.random() < 0.3:
            groups.append(f'{value:x}')
        else:
            groups.append(f'{value:04x}')
    
    # Выбираем случайный формат записи
    format_type = random.choice(['standard', 'compressed', 'mixed_case', 'leading_zeros'])
    
    if format_type == 'compressed':
        # Используем :: для сжатия нулей
        # Находим последовательность нулевых групп
        zero_start = random.randint(0, 6)
        zero_end = random.randint(zero_start + 1, 8)
        if zero_end - zero_start >= 2:
            result = ':'.join(groups[:zero_start])
            if zero_start > 0:
                result += '::'
            else:
                result += '::'
            if zero_end < 8:
                result += ':'.join(groups[zero_end:])
            return result
    
    elif format_type == 'mixed_case':
        # Смешанный регистр
        result = ':'.join(groups)
        # Случайно меняем регистр некоторых символов
        result_list = list(result)
        for i in range(len(result_list)):
            if result_list[i].isalpha() and random.random() < 0.5:
                result_list[i] = result_list[i].upper()
        return ''.join(result_list)
    
    elif format_type == 'leading_zeros':
        # С ведущими нулями (уже есть в groups)
        return ':'.join(groups)
    
    else:  # standard
        return ':'.join(groups)


def generate_test_file(output_file: str, num_lines: int):
    """
    Генерирует тестовый файл с IPv6 адресами.
    
    Args:
        output_file: Путь к выходному файлу
        num_lines: Количество строк для генерации
    """
    print(f"Generating {num_lines} IPv6 addresses...", file=sys.stderr)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i in range(num_lines):
            if (i + 1) % 100000 == 0:
                print(f"Generated {i + 1} lines...", file=sys.stderr)
            ipv6 = generate_random_ipv6()
            f.write(ipv6 + '\n')
    
    print(f"Test file generated: {output_file}", file=sys.stderr)


def generate_example_file():
    """Генерирует пример из условия задачи"""
    example_addresses = [
        '2001:0DB0:0000:123A:0000:0000:0000:0030',
        '2001:db0:0:123a::30',
        'CD10:9A90:F9BB:E5B6:F714:86E7:F1BB:BDFC',
        'DF96:A23D:8BA9:BAA0:A807:FB50:F9CD:B266',
        '9D64:9DB4:B0FE:B3C2:F09F:8DE1:EC59:987D',
    ]
    
    with open('input.txt', 'w', encoding='utf-8') as f:
        for addr in example_addresses:
            f.write(addr + '\n')
    
    print("Example file 'input.txt' generated", file=sys.stderr)


def main():
    """Точка входа"""
    if len(sys.argv) < 2:
        print("Usage: python generate_test_data.py <output_file> [num_lines]", file=sys.stderr)
        print("       python generate_test_data.py example  # Generate example from task", file=sys.stderr)
        sys.exit(1)
    
    output_file = sys.argv[1]
    
    if output_file == 'example':
        generate_example_file()
    else:
        num_lines = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
        generate_test_file(output_file, num_lines)


if __name__ == '__main__':
    main()
