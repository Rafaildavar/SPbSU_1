#!/usr/bin/env python3
"""
Программа для подсчета количества уникальных IPv6 адресов в большом файле.

Использует алгоритм внешней сортировки для обработки файлов, которые не помещаются
в оперативную память. Алгоритм работает в несколько этапов:
1. Разбиение файла на чанки, которые помещаются в память
2. Нормализация и сортировка каждого чанка
3. K-way merge отсортированных чанков
4. Подсчет уникальных адресов за один проход

Использование:
    python count_unique_ipv6.py input.txt output.txt
"""

import sys
import os
import tempfile
import heapq
from typing import List, Iterator, Tuple
from ipv6_normalizer import normalize_ipv6


# Максимальный размер чанка в байтах (примерно 100 МБ для работы в пределах 1 ГБ памяти)
CHUNK_SIZE = 100 * 1024 * 1024


def read_chunk(file_handle, chunk_size: int) -> Iterator[str]:
    """
    Читает чанк данных из файла построчно.
    
    Args:
        file_handle: Файловый дескриптор
        chunk_size: Максимальный размер чанка в байтах
    
    Yields:
        Строки из файла
    """
    current_size = 0
    buffer = []
    
    for line in file_handle:
        line_size = len(line.encode('utf-8'))
        if current_size + line_size > chunk_size and buffer:
            yield buffer
            buffer = []
            current_size = 0
        
        buffer.append(line.rstrip('\n\r'))
        current_size += line_size
    
    if buffer:
        yield buffer


def process_chunk(lines: List[str], chunk_id: int, temp_dir: str) -> str:
    """
    Обрабатывает чанк строк: нормализует IPv6 адреса и сортирует.
    
    Args:
        lines: Список строк с IPv6 адресами
        chunk_id: Уникальный идентификатор чанка
        temp_dir: Директория для временных файлов
    
    Returns:
        Путь к временному файлу с отсортированными нормализованными адресами
    """
    # Нормализуем все адреса
    normalized_addresses = []
    for line in lines:
        if line.strip():  # Пропускаем пустые строки
            try:
                normalized = normalize_ipv6(line)
                normalized_addresses.append(normalized)
            except Exception as e:
                # В случае ошибки нормализации пропускаем строку
                # (по условию задачи все адреса валидны, но на всякий случай)
                print(f"Warning: Failed to normalize '{line}': {e}", file=sys.stderr)
    
    # Сортируем и удаляем дубликаты внутри чанка
    normalized_addresses = sorted(set(normalized_addresses))
    
    # Сохраняем во временный файл
    temp_file = os.path.join(temp_dir, f'chunk_{chunk_id}.txt')
    with open(temp_file, 'w', encoding='utf-8') as f:
        for addr in normalized_addresses:
            f.write(addr + '\n')
    
    return temp_file


def merge_sorted_files(temp_files: List[str], output_file: str) -> int:
    """
    Выполняет k-way merge отсортированных файлов и подсчитывает уникальные адреса.
    
    Args:
        temp_files: Список путей к временным отсортированным файлам
        output_file: Путь к выходному файлу с результатом
    
    Returns:
        Количество уникальных IPv6 адресов
    """
    # Открываем все временные файлы
    file_handles = []
    heap = []
    
    try:
        # Инициализируем кучу первыми строками из каждого файла
        for i, temp_file in enumerate(temp_files):
            try:
                f = open(temp_file, 'r', encoding='utf-8')
                file_handles.append(f)
                line = f.readline().strip()
                if line:
                    heapq.heappush(heap, (line, i))
            except Exception as e:
                print(f"Warning: Failed to open {temp_file}: {e}", file=sys.stderr)
        
        # Выполняем merge и подсчитываем уникальные адреса
        unique_count = 0
        prev_addr = None
        
        while heap:
            current_addr, file_idx = heapq.heappop(heap)
            
            # Если это новый уникальный адрес, увеличиваем счетчик
            if current_addr != prev_addr:
                unique_count += 1
                prev_addr = current_addr
            
            # Читаем следующую строку из того же файла
            next_line = file_handles[file_idx].readline().strip()
            if next_line:
                heapq.heappush(heap, (next_line, file_idx))
        
        return unique_count
    
    finally:
        # Закрываем все файлы
        for f in file_handles:
            f.close()


def count_unique_ipv6(input_file: str, output_file: str):
    """
    Основная функция для подсчета уникальных IPv6 адресов.
    
    Args:
        input_file: Путь к входному файлу
        output_file: Путь к выходному файлу с результатом
    """
    # Создаем временную директорию для чанков
    temp_dir = tempfile.mkdtemp(prefix='ipv6_count_')
    temp_files = []
    
    try:
        print(f"Processing file: {input_file}", file=sys.stderr)
        print(f"Using temporary directory: {temp_dir}", file=sys.stderr)
        
        # Этап 1: Разбиваем файл на чанки и обрабатываем каждый
        chunk_id = 0
        with open(input_file, 'r', encoding='utf-8') as f:
            for chunk_lines in read_chunk(f, CHUNK_SIZE):
                print(f"Processing chunk {chunk_id} ({len(chunk_lines)} lines)...", file=sys.stderr)
                temp_file = process_chunk(chunk_lines, chunk_id, temp_dir)
                temp_files.append(temp_file)
                chunk_id += 1
        
        print(f"Created {len(temp_files)} sorted chunks", file=sys.stderr)
        
        # Этап 2: Выполняем k-way merge и подсчитываем уникальные адреса
        print("Merging chunks and counting unique addresses...", file=sys.stderr)
        unique_count = merge_sorted_files(temp_files, output_file)
        
        # Сохраняем результат
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(str(unique_count) + '\n')
        
        print(f"Found {unique_count} unique IPv6 addresses", file=sys.stderr)
        print(f"Result saved to: {output_file}", file=sys.stderr)
    
    finally:
        # Удаляем временные файлы
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except Exception:
                pass
        try:
            os.rmdir(temp_dir)
        except Exception:
            pass


def main():
    """Точка входа в программу"""
    if len(sys.argv) != 3:
        print("Usage: python count_unique_ipv6.py <input_file> <output_file>", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    try:
        count_unique_ipv6(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
