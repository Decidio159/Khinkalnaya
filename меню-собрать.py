# -*- coding: utf-8 -*-
"""Меню из меню.json → куски для сборщика.

    python меню-собрать.py

Пишет два файла, оба перезаписываются целиком:
    _шаблоны/куски/меню-полное.html — фильтры и все разделы (страница «Меню»)
    _шаблоны/куски/меню-хиты.html   — восемь позиций для главной

Правится меню.json, а не куски.
"""
import io, json, html, pathlib

ДАННЫЕ = json.load(io.open('меню.json', encoding='utf-8'))
КУСКИ = pathlib.Path('_шаблоны/куски')

# Что показываем на главной: по одной-две ярких позиции из ключевых разделов.
ХИТЫ = ['Хинкали классические', 'Хинкали с бараниной', 'Хачапури по-аджарски',
        'Хачапури по-мегрельски', 'Шашлык из свиной шеи', 'Люля-кебаб из баранины',
        'Суп харчо', 'Чкмерули']


def карточка(б, отложить=True):
    имя = html.escape(б['n'])
    цена = '{:,}'.format(б['p']).replace(',', ' ')
    if б.get('file'):
        верх = ('<img src="%s" alt="%s" width="400" height="300"%s />'
                % (б['file'], имя, ' loading="lazy" decoding="async"' if отложить else ''))
        класс = 'card dish'
    else:
        верх = ('<div class="dish__stub">Здесь будет ваше фото блюда —'
                ' пришлите снимок при дневном свете</div>')
        класс = 'card dish dish--nophoto'
    return ('      <article class="%s">\n'
            '        %s\n'
            '        <div class="dish__body">\n'
            '          <h4 class="dish__name">%s</h4>\n'
            '          <div class="dish__row"><span class="dish__weight">%s</span>'
            '<span class="dish__price">%s ₽</span></div>\n'
            '        </div>\n'
            '      </article>\n' % (класс, верх, имя, html.escape(б['w']), цена))


# ---------- полное меню ----------
кнопки = ['        <button type="button" class="is-active" data-tag="*">Всё меню</button>']
разделы = []
for c in ДАННЫЕ:
    кнопки.append('        <button type="button" data-tag="%s">%s</button>'
                  % (c['код'], html.escape(c['к'])))
    карточки = ''.join(карточка(б) for б in c['т'])
    разделы.append(
        '    <section class="dish-group catalog__item" data-tags="%s">\n'
        '      <h3 class="dish-group__title" id="%s">%s</h3>\n'
        '      <div class="dishes">\n%s      </div>\n'
        '    </section>\n' % (c['код'], c['код'], html.escape(c['к']), карточки))

полное = ('<div data-filters>\n'
          '  <div class="filters">\n%s\n  </div>\n\n%s</div>\n'
          % ('\n'.join(кнопки), ''.join(разделы)))
(КУСКИ / 'меню-полное.html').write_text(полное, encoding='utf-8')

# ---------- хиты на главную ----------
по_имени = {б['n']: б for c in ДАННЫЕ for б in c['т']}
пропали = [и for и in ХИТЫ if и not in по_имени]
хиты = ('<div class="dishes">\n%s</div>\n'
        % ''.join(карточка(по_имени[и]) for и in ХИТЫ if и in по_имени))
(КУСКИ / 'меню-хиты.html').write_text(хиты, encoding='utf-8')

всего = sum(len(c['т']) for c in ДАННЫЕ)
без_фото = [б['n'] for c in ДАННЫЕ for б in c['т'] if not б.get('file')]
print('Разделов: %d, позиций: %d' % (len(ДАННЫЕ), всего))
print('Без фото (%d): %s' % (len(без_фото), ', '.join(без_фото)))
if пропали:
    print('ВНИМАНИЕ, в хитах нет таких блюд: %s' % ', '.join(пропали))
