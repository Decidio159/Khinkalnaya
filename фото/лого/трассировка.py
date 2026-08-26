# -*- coding: utf-8 -*-
"""Растровый значок → SVG-путь.

    python фото/лого/трассировка.py вход.png выход.svg [--высота 24]

Зачем: логотип пришёл картинкой 512×512, а в шапке и в фавиконке он должен
краситься темой и не мылиться. Готовые трассировщики на этой сборке Python
падают, поэтому обводим контуры сами: порог → cv2.findContours → упрощение
Дугласа–Пекера → сглаживание Катмулла–Рома в кубические кривые.

На выходе один путь с fill-rule="evenodd": внутренние контуры становятся
дырками, и заливка currentColor даёт ровно ту же линейную графику.
"""
import argparse, pathlib
import numpy as np, cv2
from PIL import Image, ImageOps


def подготовить(путь, увеличение=4, порог=128):
    im = Image.open(путь).convert("RGBA")
    фон = Image.new("RGBA", im.size, (255, 255, 255, 255))
    фон.alpha_composite(im)
    im = фон.convert("L")
    рамка = ImageOps.invert(im).point(lambda v: 255 if v > 55 else 0).getbbox()
    im = im.crop(рамка)
    im = im.resize((im.width * увеличение, im.height * увеличение), Image.LANCZOS)
    маска = (np.array(im) < порог).astype(np.uint8) * 255
    return маска


def сгладить(точки, знаков=1, замкнуть=True):
    """Катмулл–Ром через вершины → цепочка кубических кривых."""
    n = len(точки)
    ф = "%%.%df" % знаков
    М = "M" + ф + " " + ф
    К = "C" + " ".join([ф] * 6)
    d = [М % tuple(точки[0])]
    предел = n if замкнуть else n - 1
    for i in range(предел):
        p0 = точки[(i - 1) % n]; p1 = точки[i]
        p2 = точки[(i + 1) % n]; p3 = точки[(i + 2) % n]
        c1 = p1 + (p2 - p0) / 6.0
        c2 = p2 - (p3 - p1) / 6.0
        d.append(К % (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1]))
    d.append("Z")
    return "".join(d)


def обвести(маска, epsilon=1.1, мусор=40):
    контуры, _ = cv2.findContours(маска, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    куски = []
    for к in контуры:
        if cv2.contourArea(к) < мусор:
            continue
        упр = cv2.approxPolyDP(к, epsilon, True).reshape(-1, 2).astype(float)
        if len(упр) < 3:
            continue
        куски.append(упр)
    return куски


def main():
    p = argparse.ArgumentParser()
    p.add_argument("вход"); p.add_argument("выход")
    p.add_argument("--высота", type=float, default=24.0)
    p.add_argument("--epsilon", type=float, default=1.1)
    p.add_argument("--знаков", type=int, default=1)
    a = p.parse_args()

    маска = подготовить(a.вход)
    куски = обвести(маска, a.epsilon)
    h, w = маска.shape
    k = a.высота / h
    d = "".join(сгладить(к * k, a.знаков) for к in куски)
    ш = round(w * k, 2); в = round(a.высота, 2)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s">'
           '<path fill="currentColor" fill-rule="evenodd" d="%s"/></svg>' % (ш, в, d))
    pathlib.Path(a.выход).write_text(svg, encoding="utf-8")
    print("контуров: %d, viewBox 0 0 %s %s, вес %.1f КБ"
          % (len(куски), ш, в, len(svg) / 1024))


if __name__ == "__main__":
    main()
