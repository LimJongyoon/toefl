#!/bin/sh
# 오답노트 갱신: build/source.html → ../index.html(체크 책) + ../practice.html(연습문제)
# 준비: npm i @fontsource/patrick-hand @fontsource/gowun-dodum @fontsource/nanum-pen-script (FONTS 경로)
set -e
cd "$(dirname "$0")"
FONTS=${FONTS:-node_modules/@fontsource}
python3 add_checks.py source.html /tmp/ck.html
python3 paginate.py /tmp/ck.html /tmp/book.html "$FONTS"
python3 inject_script.py /tmp/book.html ../index.html
python3 make_practice.py source.html ../practice.html
