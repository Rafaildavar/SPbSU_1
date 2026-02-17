"""
Модуль для нормализации IPv6 адресов в каноническую форму.
Каноническая форма: 8 групп по 4 шестнадцатеричные цифры в нижнем регистре,
разделенные двоеточиями (например, 2001:0db0:0000:0000:0000:0000:0000:0030).
"""


def normalize_ipv6(ipv6_str: str) -> str:
    """
    Приводит IPv6 адрес к канонической форме.
    
    Args:
        ipv6_str: IPv6 адрес в произвольной форме (может содержать ::, 
                  ведущие нули, произвольный регистр)
    
    Returns:
        IPv6 адрес в канонической форме: 8 групп по 4 hex цифры в нижнем регистре
    """
    # Удаляем пробелы и приводим к нижнему регистру
    ipv6_str = ipv6_str.strip().lower()
    
    # Обрабатываем случай с :: (сжатие нулей)
    if '::' in ipv6_str:
        parts = ipv6_str.split('::')
        
        # Левая часть (до ::)
        left_parts = []
        if parts[0]:
            left_parts = parts[0].split(':')
        
        # Правая часть (после ::)
        right_parts = []
        if len(parts) > 1 and parts[1]:
            right_parts = parts[1].split(':')
        
        # Вычисляем количество пропущенных групп нулей
        total_parts = len(left_parts) + len(right_parts)
        missing_groups = 8 - total_parts
        
        # Формируем полный список групп
        all_parts = left_parts + ['0'] * missing_groups + right_parts
    else:
        # Нет сжатия, просто разбиваем по двоеточиям
        all_parts = ipv6_str.split(':')
    
    # Нормализуем каждую группу: дополняем до 4 hex цифр
    normalized_parts = []
    for part in all_parts:
        if not part:
            part = '0'
        # Убираем ведущие нули, но сохраняем минимум 1 цифру
        # Затем дополняем до 4 цифр слева нулями
        try:
            # Конвертируем в int и обратно для удаления ведущих нулей
            num = int(part, 16)
            normalized_part = f'{num:x}'.zfill(4)
        except ValueError:
            # Если не удалось распарсить, используем как есть
            normalized_part = part.zfill(4)
        normalized_parts.append(normalized_part)
    
    # Убеждаемся, что у нас ровно 8 групп
    while len(normalized_parts) < 8:
        normalized_parts.append('0000')
    
    # Возвращаем каноническую форму
    return ':'.join(normalized_parts[:8])


def test_normalize():
    """Тестирование функции нормализации"""
    test_cases = [
        ('2001:0DB0:0000:123A:0000:0000:0000:0030', '2001:0db0:0000:123a:0000:0000:0000:0030'),
        ('2001:db0:0:123a::30', '2001:0db0:0000:123a:0000:0000:0000:0030'),
        ('::1', '0000:0000:0000:0000:0000:0000:0000:0001'),
        ('2001::', '2001:0000:0000:0000:0000:0000:0000:0000'),
        ('::', '0000:0000:0000:0000:0000:0000:0000:0000'),
        ('CD10:9A90:F9BB:E5B6:F714:86E7:F1BB:BDFC', 'cd10:9a90:f9bb:e5b6:f714:86e7:f1bb:bdfc'),
    ]
    
    for input_addr, expected in test_cases:
        result = normalize_ipv6(input_addr)
        assert result == expected, f"Failed: {input_addr} -> {result}, expected {expected}"
        print(f"✓ {input_addr} -> {result}")


if __name__ == '__main__':
    test_normalize()
    print("All tests passed!")
