"""오답노트 원본(source.html)을 A4 낱장 책(output.html)으로 나눈다.
사용: python3 paginate.py source.html output.html [fonts_dir]
되돌리기: python3 paginate.py --unpack output.html source.html  (게시된 책 → 편집용 원본)
fonts_dir: npm i @fontsource/patrick-hand @fontsource/gowun-dodum @fontsource/nanum-pen-script 한 node_modules/@fontsource
(실제 글꼴로 재야 넘침이 없음). 결과물은 스크립트 없는 정적 HTML."""
import sys, pathlib, re
from playwright.sync_api import sync_playwright

UNPACK = sys.argv[1] == "--unpack"
if UNPACK: sys.argv.pop(1)
src, out = sys.argv[1], sys.argv[2]
fonts = pathlib.Path(sys.argv[3] if len(sys.argv) > 3 else "node_modules/@fontsource").resolve()
html = pathlib.Path(src).read_text(encoding="utf-8")

local_css = "".join(
    f'<link rel="stylesheet" href="file://{fonts}/{n}/400.css">'
    for n in ["patrick-hand", "gowun-dodum", "nanum-pen-script"])
local_css += f'<link rel="stylesheet" href="file://{fonts}/gowun-dodum/korean-400.css">' if (fonts/"gowun-dodum/korean-400.css").exists() else ""
measure_html = re.sub(r'<link id="gfonts"[^>]*>', lambda m: local_css + m.group(0).replace('<link', '<link disabled'), html)

JS = r"""
async () => {
  await Promise.race([document.fonts.ready, new Promise(r=>setTimeout(r,5000))]);
  const SAFE = 22;                       // 글꼴 렌더 차이 여유(px)
  const book = document.getElementById('book');
  const src = document.getElementById('src');
  const chapters = [...src.querySelectorAll(':scope > .chapter')];
  const sheets = [];
  const KWN = 'h2, h3, .lead, .ch-h, .ch-lead';
  let body, ch, SPLIT = 0;
  function newSheet(c){
    const s = document.createElement('article');
    s.className = 'sheet c-' + c.dataset.c;
    s.innerHTML = '<header class="run"><b></b><span></span></header><div class="body"></div><nav class="tabs"></nav><footer class="foot"></footer>';
    s.querySelector('.run b').textContent = c.dataset.title;
    book.appendChild(s);
    sheets.push({s, c});
    const b = s.querySelector('.body');
    b.style.height = (b.clientHeight - SAFE) + 'px';
    b.style.overflow = 'hidden';
    return b;
  }
  const fits = () => body.scrollHeight <= body.clientHeight + 1;
  function carryHeadings(){
    const carry = [];
    while (body.lastElementChild && body.lastElementChild.matches(KWN)) { const e = body.lastElementChild; e.remove(); carry.unshift(e); }
    return carry;
  }
  function breakPage(){
    const carry = carryHeadings();
    body = newSheet(ch);
    carry.forEach(e => body.appendChild(e));
  }
  function placeTable(t){
    const rows = [...t.querySelectorAll(':scope table > tbody > tr')];
    const make = () => { const c = t.cloneNode(true); c.querySelector('tbody').innerHTML = ''; body.appendChild(c); return c.querySelector('tbody'); };
    const k = 't' + (++SPLIT); t.dataset.split = k;
    let tb = make(), fresh = false;
    while (rows.length){
      const r = rows.shift();
      tb.appendChild(r);
      if (fits()) { fresh = false; continue; }
      if (fresh && tb.children.length === 1) { fresh = false; continue; }  // 한 줄이 페이지보다 큼: 그냥 둠
      tb.removeChild(r);
      const back = [r];
      while (tb.lastElementChild && tb.lastElementChild.classList.contains('grp')) { back.unshift(tb.lastElementChild); tb.lastElementChild.remove(); }
      if (tb.children.length === 0) tb.closest('.tbl').remove();
      breakPage();
      rows.unshift(...back);
      tb = make(); fresh = true;
    }
  }
  function place(el){
    body.appendChild(el);
    if (fits()) return;
    el.remove();
    if (el.matches('.tbl')){ placeTable(el); return; }
    const before = body.children.length;
    breakPage();
    body.appendChild(el);
    if (!fits() && el.matches('.box') && el.querySelector('ol,ul')) {
      // 긴 목록 박스 쪼개기
      el.remove();
      el.dataset.split = 'b' + (++SPLIT);
      const list = el.querySelector('ol,ul'); const items = [...list.children];
      const make = () => { const c = el.cloneNode(true); c.querySelector('ol,ul').innerHTML=''; body.appendChild(c); return c.querySelector('ol,ul'); };
      let l = make();
      for (const it of items){ l.appendChild(it); if (!fits()){ it.remove(); breakPage(); l = make(); l.appendChild(it); } }
    }
  }
  for (const c of chapters){
    ch = c; body = newSheet(c);
    const firstSheet = sheets[sheets.length-1].s;
    firstSheet.id = c.id;
    for (const el of [...c.children]) place(el);
  }
  // 빈 페이지 제거
  for (let i = sheets.length-1; i >= 0; i--) if (!sheets[i].s.querySelector('.body').children.length){ sheets[i].s.remove(); sheets.splice(i,1); }
  const N = sheets.length;
  const firstPage = {};
  sheets.forEach((o,i) => { if (!o.s.id) o.s.id = 'p' + (i+1); if (!(o.c.id in firstPage)) firstPage[o.c.id] = i+1; });
  sheets.forEach((o,i) => {
    const b = o.s.querySelector('.body'); b.style.height = ''; b.style.overflow = '';
    o.s.querySelector('.run span').textContent = (i+1) + ' / ' + N;
    const prev = sheets[i-1], next = sheets[i+1];
    o.s.querySelector('.foot').innerHTML =
      `<a href="#${prev ? prev.s.id : ''}" class="${prev ? '' : 'off'}" aria-label="이전 페이지">‹ 이전</a><span>${i+1}</span><a href="#${next ? next.s.id : ''}" class="${next ? '' : 'off'}" aria-label="다음 페이지">다음 ›</a>`;
    o.s.querySelector('.tabs').innerHTML = chapters.map(c =>
      `<a href="#${c.id}" class="c-${c.dataset.c}${c === o.c ? ' on' : ''}">${c.dataset.tab}</a>`).join('');
    o.s.setAttribute('aria-label', o.c.dataset.title + ' ' + (i+1) + '쪽');
  });
  document.querySelectorAll('[data-pg]').forEach(e => { e.textContent = firstPage[e.dataset.pg] + '쪽'; });
  src.remove();
  return N;
}
"""

UNPACK_JS = r"""
() => {
  // 책(output)을 원본(source)으로 되돌림: 장별로 본문을 이어 붙이고 쪼갠 표·목록을 합침
  const sheets = [...document.querySelectorAll('#book > .sheet')];
  const src = document.createElement('div'); src.id = 'src';
  const tabs = [...sheets[0].querySelectorAll('.tabs a')];
  const chap = {};
  tabs.forEach(a => {
    const id = a.getAttribute('href').slice(1);
    const sec = document.createElement('section');
    sec.className = 'chapter'; sec.id = id;
    sec.dataset.c = [...a.classList].find(c => c.startsWith('c-')).slice(2);
    sec.dataset.tab = a.textContent;
    chap[id] = sec; src.appendChild(sec);
  });
  sheets.forEach(s => {
    const id = s.querySelector('.tabs a.on').getAttribute('href').slice(1);
    const sec = chap[id];
    if (!sec.dataset.title) sec.dataset.title = s.querySelector('.run b').textContent;
    for (const el of [...s.querySelector('.body').children]) {
      const last = sec.lastElementChild;
      if (el.dataset.split && last && last.dataset.split === el.dataset.split) {
        const from = el.querySelector('tbody') || el.querySelector('ol,ul');
        const to = last.querySelector('tbody') || last.querySelector('ol,ul');
        [...from.children].forEach(c => to.appendChild(c));
      } else sec.appendChild(el);
    }
  });
  src.querySelectorAll('[data-split]').forEach(e => e.removeAttribute('data-split'));
  src.querySelectorAll('[data-pg]').forEach(e => e.textContent = '');
  document.getElementById('book').innerHTML = '';
  document.body.appendChild(src);
}
"""

if UNPACK:
    with sync_playwright() as p:
        br = p.chromium.launch(); pg = br.new_page()
        pg.set_content(html, wait_until="domcontentloaded")
        pg.evaluate(UNPACK_JS)
        pathlib.Path(out).write_text("<!DOCTYPE html>\n" + pg.evaluate("document.documentElement.outerHTML"), encoding="utf-8")
        br.close()
    print("unpacked"); sys.exit()

with sync_playwright() as p:
    br = p.chromium.launch()
    pg = br.new_page(viewport={"width": 2600, "height": 1600})
    tmp = pathlib.Path(out).with_suffix(".measure.html")
    tmp.write_text(measure_html, encoding="utf-8")
    pg.goto(tmp.resolve().as_uri(), wait_until='domcontentloaded'); pg.wait_for_timeout(1500)
    n = pg.evaluate(JS)
    res = pg.content()
    br.close()
    tmp.unlink()

res = re.sub(r'<link rel="stylesheet" href="file://[^"]+">', "", res)
res = res.replace('<link disabled="" id="gfonts"', '<link id="gfonts"')
pathlib.Path(out).write_text(res, encoding="utf-8")
print("pages:", n)
