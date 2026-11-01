"""오답노트 원본(source.html)에 공부 체크 칸을 넣는다 (페이지 나누기 전에 실행).
사용: python3 add_checks.py source.html source_ck.html
순서: add_checks.py → 05_페이지나누기.py → inject_script.py
체크 칸마다 내용으로 만든 고정 키(data-k)를 달아, 노트를 갱신해도 이미 한 체크가 유지된다."""
import sys, hashlib, pathlib
from bs4 import BeautifulSoup

src, out = sys.argv[1], sys.argv[2]
soup = BeautifulSoup(pathlib.Path(src).read_text(encoding="utf-8"), "html.parser")

def key(el):
    t = " ".join(el.get_text(" ").split())
    return hashlib.sha1(t.encode()).hexdigest()[:10]

def box(el):
    cb = soup.new_tag("input", type="checkbox", attrs={"class": "ck", "data-k": key(el), "aria-label": "공부 완료"})
    return cb

root = soup.find(id="src")
n = 0
for sec in root.select(":scope > section.chapter"):
    if sec.get("id") == "cover":
        continue
    for el in sec.select(".card"):
        el.select_one(".q").insert(0, box(el)); n += 1
    for el in sec.select(".prob"):
        el.select_one(".h").insert(0, box(el)); n += 1
    for el in sec.select("ol.lines > li, ul.lines > li"):
        tgt = el.find("span") or el
        tgt.insert(0, box(el)); n += 1
    for tr in sec.select(".tbl tbody > tr"):
        if "grp" in (tr.get("class") or []):
            continue
        td = tr.find("td")
        if td: td.insert(0, box(tr)); n += 1

# 표지: 진행률 + 이어 보기 자리
cover = root.select_one("#cover .cover")
if cover and not cover.select_one(".progress"):
    p = BeautifulSoup('<div class="progress"><div class="pbar"><i></i></div>'
                      '<p><b class="pdone">0</b> / <span class="ptotal">0</span> 완료 · '
                      '<a class="resume" href="#cover">이어서 보기</a> · '
                      '<button class="preset" type="button">체크 모두 지우기</button></p>'
                      '<p class="plink"><a href="practice.html">✎ 틀린 문제 다시 풀기 (연습문제)</a></p></div>', "html.parser")
    date = cover.select_one(".date")
    (date or cover.h1).insert_after(p)

pathlib.Path(out).write_text(str(soup), encoding="utf-8")
print("checkboxes:", n)
