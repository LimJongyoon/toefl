# 토플 오답노트 (체크 버전)

- 보기: `note/index.html` (GitHub Pages: /toefl/note/)
- 항목마다 체크 칸 → 그 기기 브라우저에 저장. 표지에 진행률과 "이어서 보기(마지막으로 본 쪽)".
- 갱신: `build/source.html` 수정 →
  `python3 build/add_checks.py build/source.html ck.html` →
  `python3 build/paginate.py ck.html book.html node_modules/@fontsource` →
  `python3 build/inject_script.py book.html index.html`
- 체크 키는 항목 내용으로 만들어서, 노트를 갱신해도 기존 체크가 유지됨(내용을 고친 항목만 초기화).
