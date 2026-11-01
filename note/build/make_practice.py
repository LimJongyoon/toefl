"""오답노트 원본(source.html)에서 틀린 문제를 꺼내 토플식 연습문제 페이지(practice.html)를 만든다.
사용: python3 make_practice.py source.html ../practice.html
- R Complete the Words 카드 → 빈칸 채우기 (앞 철자 고정, 나머지 입력)
- R/L 객관식 카드 → 내 오답 vs 정답 2지선다
- W 단어배열 카드 → 단어 타일 배열 (내 오답에만 있던 단어는 함정 보기)
- W 이메일·디스커션, S 인터뷰 표 → 틀린 표현 고쳐 쓰기 (모범 표현과 비교)
- S 따라말하기 표 → 듣고 따라 말하기 (기기 음성으로 읽어 줌)
결과는 기기 브라우저(localStorage)에 저장. 원본에 오답이 추가되면 다시 만들기만 하면 됨."""
import sys, re, json, hashlib, pathlib, html as H
from bs4 import BeautifulSoup

src, out = sys.argv[1], sys.argv[2]
soup = BeautifulSoup(pathlib.Path(src).read_text(encoding="utf-8"), "html.parser")
T = lambda el: " ".join(el.get_text(" ").split()) if el else ""
def clean(t): return re.sub(r"\s+([.,?!])", r"\1", t).strip()
def hid(*a): return hashlib.sha1("|".join(a).encode()).hexdigest()[:10]

items = []
def prev_label(el, sel):
    p = el.find_previous(sel)
    return T(p) if p else ""

# ---------- 리딩 / 리스닝 카드 ----------
for ch, area in (("r", "R"), ("l", "L")):
    sec = soup.select_one("#" + ch)
    if not sec: continue
    for c in sec.select(".card"):
        q = c.select_one(".q")
        if not q: continue
        qq = BeautifulSoup(str(q), "html.parser")
        for t in qq.select("b, .tag, input"): t.decompose()
        qtext = clean(T(qq))
        tag = T(q.select_one(".tag"))
        mine, ans = c.select_one(".row.mine"), c.select_one(".row.ans")
        tips = [T(r.select("span")[-1]) for r in c.select(".row.k")]
        if not ans: continue
        ans_txt = clean(T(ans.select("span")[1])) if len(ans.select("span")) > 1 else ""
        if "___" in qtext and ans.select_one(".f"):
            word = ans_txt.replace(" ", "")
            m = re.search(r"(\S*?)___", qtext)
            pre = m.group(1) if m else ""
            if not word.lower().startswith(pre.lower()): continue
            items.append(dict(id=hid("cw", qtext), type="cw", area=area, group=prev_label(c, "h3"),
                              before=qtext[:m.start()], pre=pre, rest=word[len(pre):], after=qtext[m.end():],
                              tip=" / ".join(tips)))
        elif mine and mine.select_one(".x") and ans.select_one(".f"):
            items.append(dict(id=hid("mc", qtext), type="mc", area=area, group=tag or prev_label(c, "h3"),
                              q=qtext, right=clean(T(ans.select_one(".f"))), wrong=clean(T(mine.select_one(".x"))),
                              tip=" / ".join(tips)))

# ---------- 라이팅 ----------
w = soup.select_one("#w")
if w:
    for c in w.select(".card"):
        sec = c.find_previous("h2")
        if not sec or "단어배열" not in T(sec): continue
        q = BeautifulSoup(str(c.select_one(".q")), "html.parser")
        for t in q.select("b, input"): t.decompose()
        ans = c.select_one(".row.ans"); mine = c.select_one(".row.mine")
        if not ans: continue
        sent = clean(T(ans.select("span")[1]))
        m = re.match(r"^(.*?)([.?!])?$", sent)
        body, punct = m.group(1), m.group(2) or "."
        words = body.split()
        my = clean(T(mine.select("span")[1])) if mine else ""
        aset = {x.lower().strip(",.?!") for x in words}
        extra = []
        for x in my.split():
            k = x.lower().strip(",.?!")
            if k and k not in aset and k not in [e.lower() for e in extra] and "빈칸" not in k:
                extra.append(x.strip(",.?!"))
        items.append(dict(id=hid("bs", sent), type="bs", area="W", group=prev_label(c, "h3"),
                          say=clean(T(q)), words=words, punct=punct, extra=extra[:2],
                          tip=T(c.select_one(".pt"))))
    for tr in w.select(".tbl tbody tr"):
        bad = tr.select_one("td.bad")
        tds = tr.find_all("td")
        if not bad or len(tds) < 3: continue
        h2 = tr.find_previous("h2")
        items.append(dict(id=hid("fx", T(bad)), type="fx", area="W", group=(T(h2)[1:].strip() if h2 else "") + " · " + prev_label(tr, "tr.grp"),
                          wrong=clean(T(bad)), right=clean(T(tds[1])), tip=T(tds[2])))

# ---------- 스피킹 ----------
s = soup.select_one("#s")
if s:
    for tr in s.select(".tbl tbody tr"):
        tds = tr.find_all("td")
        if "grp" in (tr.get("class") or []) or len(tds) < 3: continue
        h2 = T(tr.find_previous("h2"))
        grp = prev_label(tr, "tr.grp")
        if "따라" in h2:
            orig = clean(T(tds[0]))
            if len(orig.split()) < 4: continue
            items.append(dict(id=hid("lr", orig), type="lr", area="S", group=grp, text=orig,
                              said=clean(T(tds[1])), tip=T(tds[2])))
        elif "bad" in (tds[0].get("class") or []):
            items.append(dict(id=hid("fx", T(tds[0])), type="fx", area="S", group="인터뷰 · " + grp,
                              wrong=clean(T(tds[0])), right=clean(T(tds[1])), tip=T(tds[2])))

TYPES = [("cw", "R · Complete the Words"), ("mc", "R·L · 객관식"), ("bs", "W · Build a Sentence"),
         ("fx", "W·S · 고쳐 쓰기/말하기"), ("lr", "S · Listen and Repeat")]

PAGE = r"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>토플 오답 다시 풀기</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Nanum+Pen+Script&display=swap">
<style>
:root{--paper:#fffef8;--desk:#e6e0d2;--ink:#1d1f26;--pencil:#61646e;--soft:#d6d2c6;--red:#c62828;--green:#16803d;--blue:#2856b3;color-scheme:light}
*{box-sizing:border-box}
body{margin:0;background:var(--desk);color:var(--ink);font-family:"Gowun Dodum","Apple SD Gothic Neo",sans-serif;font-size:18px;line-height:1.55}
header{position:sticky;top:0;z-index:5;background:var(--paper);border-bottom:1.5px solid var(--soft);padding:10px 16px}
.top{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
h1{font-family:"Nanum Pen Script",cursive;font-weight:400;font-size:34px;margin:0}
.top a{color:var(--blue);font-size:15px}
.bar{height:9px;border:1.3px solid #8a7f6a;border-radius:6px;overflow:hidden;background:#fff;margin:8px 0 4px}
.bar i{display:block;height:100%;width:0;background:var(--green);transition:width .3s}
.stat{font-size:14px;color:var(--pencil)}
nav{display:flex;gap:6px;overflow-x:auto;padding:8px 0 2px}
nav button,.filters button{font:inherit;font-size:15px;white-space:nowrap;border:1.4px solid var(--soft);background:#fff;border-radius:18px;padding:4px 12px;cursor:pointer;color:var(--ink)}
nav button.on,.filters button.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.filters{display:flex;gap:6px;margin-top:6px;flex-wrap:wrap}
main{max-width:760px;margin:0 auto;padding:16px}
.it{background:var(--paper);border:1.6px solid #b9ae98;border-radius:8px 12px 9px 13px;padding:14px 16px;margin-bottom:14px}
.it.ok{border-color:var(--green)} .it.no{border-color:var(--red)}
.meta{font-size:13px;color:var(--pencil);margin-bottom:6px;display:flex;justify-content:space-between;gap:8px}
.badge{font-size:12px;border-radius:10px;padding:0 8px;border:1px solid}
.badge.ok{color:var(--green)} .badge.no{color:var(--red)}
.say{color:var(--pencil);margin:0 0 8px}
.cw input{font:inherit;letter-spacing:.12em;border:none;border-bottom:2px solid var(--blue);background:#f3f7ff;padding:0 4px;outline:none}
.opt{display:block;width:100%;text-align:left;font:inherit;background:#fff;border:1.4px solid var(--soft);border-radius:8px;padding:8px 12px;margin:6px 0;cursor:pointer;color:var(--ink)}
.opt.right{border-color:var(--green);background:#ecf8ef} .opt.wrongp{border-color:var(--red);background:#fdecec}
.slot{min-height:46px;border:1.6px dashed var(--soft);border-radius:8px;padding:6px;display:flex;flex-wrap:wrap;gap:6px;margin:6px 0;background:#fff}
.bank{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0}
.tile{font:inherit;font-size:17px;background:#fff;border:1.4px solid #8a7f6a;border-radius:6px;padding:3px 10px;cursor:pointer;color:var(--ink)}
.slot .tile{background:#eef3fb;border-color:var(--blue)}
.wrong-line{color:var(--red);text-decoration:line-through;text-decoration-thickness:1px}
textarea{font:inherit;width:100%;min-height:64px;border:1.4px solid var(--soft);border-radius:8px;padding:8px;background:#fff}
.row{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.btn{font:inherit;font-size:15px;border-radius:8px;padding:5px 14px;cursor:pointer;border:1.4px solid var(--ink);background:var(--ink);color:#fff}
.btn.ghost{background:#fff;color:var(--ink)}
.btn.g{background:var(--green);border-color:var(--green)} .btn.r{background:var(--red);border-color:var(--red)}
.fb{margin-top:10px;padding:8px 12px;border-radius:8px;background:#f6f3ea;font-size:16px;display:none}
.fb.show{display:block}
.fb b.ok{color:var(--green)} .fb b.no{color:var(--red)}
.hidden{filter:blur(6px);user-select:none}
.empty{text-align:center;color:var(--pencil);padding:40px 0}
</style></head><body>
<header><div class="top"><h1>오답 다시 풀기</h1><a href="./">← 오답노트</a></div>
<div class="bar"><i id="bar"></i></div><div class="stat" id="stat"></div>
<nav id="tabs"></nav>
<div class="filters" id="filters"></div></header>
<main id="list"></main>
<script>
const ITEMS=__ITEMS__, TYPES=__TYPES__;
const KEY='toefl-practice-v1';
let st={}; try{st=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}};
let tab=TYPES[0][0], filt='todo';
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const norm=s=>s.toLowerCase().replace(/[’']/g,"'").replace(/[^a-z0-9' ]/g,' ').replace(/\s+/g,' ').trim();
const shuffle=a=>{a=a.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a};
function mark(it,ok){const r=st[it.id]||{n:0,streak:0};r.n++;r.last=ok?1:0;r.streak=ok?(r.streak||0)+1:0;st[it.id]=r;save();head()}
function status(it){const r=st[it.id];if(!r)return'';return r.streak>=2?'done':r.last?'once':'miss'}
function head(){
  const n=ITEMS.length,d=ITEMS.filter(i=>status(i)==='done').length;
  document.getElementById('bar').style.width=(n?d/n*100:0)+'%';
  document.getElementById('stat').textContent=`완료 ${d} / ${n} · 연속 2번 맞히면 완료 · 기록은 이 기기에 저장`;
  document.getElementById('tabs').innerHTML=TYPES.map(([k,l])=>{const a=ITEMS.filter(i=>i.type===k);if(!a.length)return'';
    const dd=a.filter(i=>status(i)==='done').length;return `<button data-t="${k}" class="${k===tab?'on':''}">${l} ${dd}/${a.length}</button>`}).join('');
  document.querySelectorAll('#tabs button').forEach(b=>b.onclick=()=>{tab=b.dataset.t;render()});
  const F=[['todo','아직 안 끝난 것'],['miss','최근 틀린 것'],['all','전체']];
  document.getElementById('filters').innerHTML=F.map(([k,l])=>`<button data-f="${k}" class="${k===filt?'on':''}">${l}</button>`).join('')+'<button id="rs">기록 지우기</button>';
  document.querySelectorAll('#filters [data-f]').forEach(b=>b.onclick=()=>{filt=b.dataset.f;render()});
  document.getElementById('rs').onclick=()=>{if(confirm('이 기기의 풀이 기록을 모두 지울까요?')){st={};save();render()}};
}
function badge(it){const s=status(it);return s==='done'?'<span class="badge ok">완료</span>':s==='once'?'<span class="badge ok">1번 맞힘</span>':s==='miss'?'<span class="badge no">틀림</span>':''}
function render(){
  head();
  let a=ITEMS.filter(i=>i.type===tab);
  if(filt==='todo')a=a.filter(i=>status(i)!=='done');
  if(filt==='miss')a=a.filter(i=>status(i)==='miss');
  const L=document.getElementById('list');
  if(!a.length){L.innerHTML='<p class="empty">여기는 다 끝났습니다. 다른 유형이나 “전체”를 보십시오.</p>';return}
  L.innerHTML='';a.forEach((it,k)=>L.appendChild(card(it,k+1)));
}
function shell(it,no,inner){
  const d=document.createElement('div');d.className='it';
  d.innerHTML=`<div class="meta"><span>${no}. ${esc(it.group||'')}</span><span class="bd">${badge(it)}</span></div>${inner}<div class="fb"></div>`;return d}
function feedback(d,it,ok,html){
  d.classList.remove('ok','no');d.classList.add(ok?'ok':'no');
  const f=d.querySelector('.fb');f.classList.add('show');
  f.innerHTML=`<b class="${ok?'ok':'no'}">${ok?'정답':'오답'}</b> ${html}${it.tip?`<br><small>→ ${esc(it.tip)}</small>`:''}`;
  mark(it,ok);d.querySelector('.bd').innerHTML=badge(it);
}
function card(it,no){
  if(it.type==='cw'){
    const d=shell(it,no,`<p class="cw">${esc(it.before)}${esc(it.pre)}<input autocapitalize="off" autocomplete="off" spellcheck="false" aria-label="빈칸" maxlength="${it.rest.length+3}" placeholder="${'_ '.repeat(it.rest.length).trim()}" style="width:${Math.max(3,it.rest.length*1.15)}em">${esc(it.after)}</p><div class="row"><button class="btn">확인</button></div>`);
    const inp=d.querySelector('input'),go=()=>{const ok=inp.value.trim().toLowerCase()===it.rest.toLowerCase();
      feedback(d,it,ok,`${esc(it.pre)}<u>${esc(it.rest)}</u>${ok?'':` (내 답: ${esc(it.pre+inp.value)})`}`)};
    d.querySelector('.btn').onclick=go;inp.onkeydown=e=>{if(e.key==='Enter')go()};return d}
  if(it.type==='mc'){
    const ops=shuffle([it.right,it.wrong]);
    const d=shell(it,no,`<p>${esc(it.q)}</p>${ops.map(o=>`<button class="opt">${esc(o)}</button>`).join('')}`);
    d.querySelectorAll('.opt').forEach(b=>b.onclick=()=>{const ok=b.textContent===it.right;
      d.querySelectorAll('.opt').forEach(x=>{x.disabled=true;if(x.textContent===it.right)x.classList.add('right');else if(x===b)x.classList.add('wrongp')});
      feedback(d,it,ok,ok?'':'바꿔 말한 보기가 정답')});return d}
  if(it.type==='bs'){
    const tiles=shuffle(it.words.concat(it.extra));
    const d=shell(it,no,`<p class="say">${esc(it.say)}</p><div class="slot"></div><div class="bank">${tiles.map(t=>`<button class="tile">${esc(t)}</button>`).join('')}</div><div class="row"><button class="btn">확인</button><button class="btn ghost">다시</button></div>`);
    const slot=d.querySelector('.slot'),bank=d.querySelector('.bank');
    d.querySelectorAll('.tile').forEach(t=>t.onclick=()=>{(t.parentNode===bank?slot:bank).appendChild(t)});
    const [ck,rs]=d.querySelectorAll('.row .btn');
    rs.onclick=()=>{[...slot.children].forEach(t=>bank.appendChild(t))};
    ck.onclick=()=>{const mine=[...slot.children].map(t=>t.textContent).join(' ');const right=it.words.join(' ');
      const ok=norm(mine)===norm(right);feedback(d,it,ok,`${esc(right+it.punct)}${it.extra.length?`<br><small>함정: ${esc(it.extra.join(', '))}</small>`:''}`)};return d}
  if(it.type==='fx'){
    const d=shell(it,no,`<p class="wrong-line">${esc(it.wrong)}</p><textarea placeholder="바르게 고쳐 쓰거나 소리 내어 말해 보십시오"></textarea><div class="row"><button class="btn">모범 표현 보기</button></div>`);
    d.querySelector('.btn').onclick=e=>{const f=d.querySelector('.fb');f.classList.add('show');
      f.innerHTML=`<b>○</b> ${esc(it.right)}${it.tip?`<br><small>→ ${esc(it.tip)}</small>`:''}<div class="row"><button class="btn g">맞게 고쳤음</button><button class="btn r">못 고쳤음</button></div>`;
      const [g,r]=f.querySelectorAll('.btn');g.onclick=()=>{mark(it,1);d.querySelector('.bd').innerHTML=badge(it);d.classList.add('ok');d.classList.remove('no');g.parentNode.remove()};
      r.onclick=()=>{mark(it,0);d.querySelector('.bd').innerHTML=badge(it);d.classList.add('no');d.classList.remove('ok');r.parentNode.remove()};e.target.remove()};return d}
  if(it.type==='lr'){
    const d=shell(it,no,`<p class="hidden lrtext">${esc(it.text)}</p><div class="row"><button class="btn">▶ 듣기</button><button class="btn ghost">문장 보기</button></div>`);
    const [pl,sh]=d.querySelectorAll('.row .btn');
    pl.onclick=()=>{try{speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(it.text);u.lang='en-US';u.rate=.95;speechSynthesis.speak(u)}catch(e){alert('이 기기는 음성 읽기를 지원하지 않습니다')}};
    sh.onclick=()=>{d.querySelector('.lrtext').classList.remove('hidden');const f=d.querySelector('.fb');f.classList.add('show');
      f.innerHTML=`지난번: <span class="wrong-line">${esc(it.said)}</span>${it.tip?`<br><small>→ ${esc(it.tip)}</small>`:''}<div class="row"><button class="btn g">그대로 말했음</button><button class="btn r">틀렸음</button></div>`;
      const [g,r]=f.querySelectorAll('.btn');g.onclick=()=>{mark(it,1);d.querySelector('.bd').innerHTML=badge(it);d.classList.add('ok');g.parentNode.remove()};r.onclick=()=>{mark(it,0);d.querySelector('.bd').innerHTML=badge(it);d.classList.add('no');r.parentNode.remove()};sh.remove()};return d}
  return document.createElement('div');
}
render();
</script></body></html>"""

page = PAGE.replace("__ITEMS__", json.dumps(items, ensure_ascii=False)).replace("__TYPES__", json.dumps(TYPES, ensure_ascii=False))
pathlib.Path(out).write_text(page, encoding="utf-8")
from collections import Counter
print("items:", len(items), dict(Counter(i["type"] for i in items)))
