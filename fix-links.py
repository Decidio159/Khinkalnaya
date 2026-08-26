# -*- coding: utf-8 -*-
"""Заменяет кириллические ссылки на латинские для GitHub Pages"""
import os
import re

# Замены
REPLACEMENTS = {
    'общее/': 'common/',
    'меню.html': 'menu.html',
    'бронь.html': 'booking.html',
    'контакты.html': 'contacts.html',
}

# Файлы для обработки
files_to_fix = ['index.html', 'menu.html', 'booking.html', 'contacts.html', '404.html', 'privacy.html']

for filename in files_to_fix:
    if not os.path.exists(filename):
        continue
    
    print(f'Обрабатываю {filename}...')
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Делаем замены
    for old, new in REPLACEMENTS.items():
        content = content.replace(old, new)
    
    # Сохраняем
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'  ✓ {filename} обновлён')

print('\nГотово! Все ссылки заменены на латинские.')
