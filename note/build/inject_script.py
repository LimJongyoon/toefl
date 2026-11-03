"""페이지 나눈 책(book.html)에 체크 저장 스크립트를 넣는다.
사용: python3 inject_script.py book.html ../index.html
체크 상태는 그 기기 브라우저(localStorage)에 저장된다."""
import sys, pathlib

src, out = sys.argv[1], sys.argv[2]
html = pathlib.Path(src).read_text(encoding="utf-8")

CSS = """<style id="ck-style">
.ck{width:19px;height:19px;margin:0 7px 0 0;vertical-align:-3px;accent-color:var(--area,#2c6bd1);cursor:pointer;flex:none}
.done{opacity:.42}
.done .ck{opacity:1}
.progress{margin:6px 0 14px}
.progress .pbar{height:10px;border:1.4px solid #8a7f6a;border-radius:6px;overflow:hidden;background:#fffdf6}
.progress .pbar i{display:block;height:100%;width:0;background:#1f7a3f;transition:width .3s}
.progress p{margin:6px 0 0;font-size:17px}
.progress a{color:#1f4b8f}
.plink a{display:inline-block;margin-top:4px;padding:4px 14px;border:1.6px solid #1f4b8f;border-radius:8px;text-decoration:none;font-size:18px}
.progress button{font:inherit;font-size:14px;background:none;border:1px solid #b9ae98;border-radius:6px;padding:1px 8px;color:#8a7f6a;cursor:pointer}
</style>"""

JS = r"""<script id="ck-script">
(function(){
  var KEY='toefl-note-checks-v1', PAGE='toefl-note-page-v1', st={};
  try{ st=JSON.parse(localStorage.getItem(KEY)||'{}'); }catch(e){ st={}; }
  function save(){ try{ localStorage.setItem(KEY, JSON.stringify(st)); }catch(e){} }
  var boxes=[].slice.call(document.querySelectorAll('input.ck'));
  var keys={}; boxes.forEach(function(b){ keys[b.dataset.k]=1; });
  var total=Object.keys(keys).length;
  function host(b){ return b.closest('.card,.prob,li,tr'); }
  function paint(){
    var done=0;
    boxes.forEach(function(b){ var on=!!st[b.dataset.k]; b.checked=on; var h=host(b); if(h) h.classList.toggle('done',on); });
    Object.keys(keys).forEach(function(k){ if(st[k]) done++; });
    var d=document.querySelector('.pdone'), t=document.querySelector('.ptotal'), bar=document.querySelector('.pbar i');
    if(d) d.textContent=done; if(t) t.textContent=total;
    if(bar) bar.style.width=(total? done/total*100:0)+'%';
  }
  boxes.forEach(function(b){ b.addEventListener('change',function(){
    if(b.checked) st[b.dataset.k]=1; else delete st[b.dataset.k];
    save(); paint();
  }); });
  var reset=document.querySelector('.preset');
  if(reset) reset.addEventListener('click',function(){ if(confirm('체크를 모두 지울까요?')){ st={}; save(); paint(); } });
  // 마지막으로 본 쪽 기억
  var sheets=[].slice.call(document.querySelectorAll('.sheet')), resume=document.querySelector('.resume');
  function setResume(){
    var id=null; try{ id=localStorage.getItem(PAGE); }catch(e){}
    var s=id && document.getElementById(id);
    if(resume && s && s.id!=='cover'){ resume.href='#'+id; resume.textContent='이어서 보기 ('+(sheets.indexOf(s)+1)+'쪽)'; }
    else if(resume){ resume.textContent='처음부터 보기'; resume.href='#'+(sheets[1]?sheets[1].id:'cover'); }
  }
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){ es.forEach(function(e){
      if(e.isIntersecting && e.target.id && e.target.id!=='cover'){ try{ localStorage.setItem(PAGE,e.target.id); }catch(x){} }
    }); },{threshold:.6});
    sheets.forEach(function(s){ io.observe(s); });
  }
  setResume(); paint();
})();
</script>"""

html = html.replace("</head>", CSS + "</head>", 1)
html = html.replace("</body>", JS + "</body>", 1)
# 2장 외울 것: 템플릿마다 따라쓰기(타이핑 채점) 창
TYPE_CSS = """<style id="ty-style">
.ty-open{font:inherit;font-size:15px;color:var(--area);background:var(--paper);border:1.4px solid var(--area);border-radius:7px;padding:0 9px;cursor:pointer;white-space:nowrap;align-self:center}
.prob .h small + .ty-open{margin-left:0}
#ty{position:fixed;inset:0;z-index:100;background:rgba(40,36,28,.55);display:none;overflow:auto;-webkit-overflow-scrolling:touch}
#ty.on{display:block}
#ty .win{max-width:880px;margin:18px auto;background:#fffef8;border-radius:14px;padding:16px 18px 22px;font-family:var(--hand);color:var(--ink);box-shadow:0 10px 40px rgba(0,0,0,.3)}
#ty .top{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
#ty .top h3{margin:0 auto 0 0;font-size:22px}
#ty .top h3 b{color:#2a8a7a;margin-right:6px}
#ty button{font:inherit;font-size:17px;border-radius:9px;padding:4px 14px;cursor:pointer;border:1.4px solid #b9ae98;background:#fff;color:var(--ink)}
#ty button.main{background:#2856b3;border-color:#2856b3;color:#fff;padding:6px 22px}
#ty button.on{background:var(--ink);color:#fff;border-color:var(--ink)}
#ty .lab{margin:14px 0 4px;color:var(--pencil);font-size:16px}
#ty .tpltxt{border:1.4px solid var(--soft);border-radius:10px;padding:8px 12px;background:#fff;font-size:19px;line-height:1.6;transition:filter .2s}
#ty .tpltxt.hide{filter:blur(7px);user-select:none}
#ty .tpltxt p{margin:2px 0}
#ty .qtxt{border-left:3px solid #2a8a7a;background:#f4f1e6;border-radius:0 8px 8px 0;padding:6px 12px;font-size:18px;line-height:1.5}
#ty .qtxt p{margin:0}
#ty .tpltxt .fx{font-weight:700;color:var(--ink)} #ty .tpltxt .fl{color:#9a9da6}
#ty textarea{display:block;width:100%;box-sizing:border-box;min-height:300px;resize:vertical;border:1.4px solid #f0e2a0;border-radius:10px;outline:none;
  font-family:var(--hand);font-size:20px;line-height:32px;padding:0 12px;color:var(--ink);
  background:repeating-linear-gradient(#fffbe6 0 31px,#f1e3a8 31px 32px);background-attachment:local}
#ty .bar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:10px}
#ty .bar label{margin-left:auto;color:var(--pencil);font-size:16px;display:flex;gap:4px;align-items:center}
#ty .res{display:none;margin-top:16px;border-top:1.6px dashed var(--soft);padding-top:10px}
#ty .score{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
#ty .score .big{font-size:44px;line-height:1}
#ty .score span{color:var(--pencil);font-size:16px}
#ty .lg{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:15px;color:var(--pencil);margin:6px 0}
#ty .view{white-space:pre-wrap;word-break:break-word;font-size:19px;line-height:1.75;background:#fff;border:1.4px solid var(--soft);border-radius:10px;padding:8px 12px}
#ty .ok{color:#16803d}
#ty .bad{color:#c62828;background:rgba(255,90,90,.22);text-decoration:line-through;border-radius:3px}
#ty .miss{color:#a35a00;background:rgba(255,200,60,.35);border-bottom:2px solid #d08a00;border-radius:3px}
#ty .rest{color:#c4c4c4}
#ty .k{display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:-1px;margin-right:4px}
</style>"""

TYPE_JS = r"""<script id="ty-script">
(function(){
  var probs=[].slice.call(document.querySelectorAll('.prob.tpl'));
  if(!probs.length) return;
  var MEMO='toefl-type-memo-v1', memos={};
  try{ memos=JSON.parse(localStorage.getItem(MEMO)||'{}'); }catch(e){ memos={}; }
  function saveMemo(){ try{ localStorage.setItem(MEMO, JSON.stringify(memos)); }catch(e){} }
  var ov=document.createElement('div'); ov.id='ty';
  ov.innerHTML='<div class="win"><div class="top"><h3></h3><button class="hide">가리기</button><button class="close">닫기 ✕</button></div>'+
    '<div class="qbox"></div><p class="lab">템플릿</p><div class="tpltxt"></div>'+
    '<p class="lab">메모지 — 여기에 따라 쓰기 (띄어쓰기·줄바꿈은 채점 안 함)</p><textarea spellcheck="false" autocapitalize="off" autocorrect="off" autocomplete="off"></textarea>'+
    '<div class="bar"><button class="main grade">채점</button><button class="clear">지우기</button><label><input type="checkbox" class="ci"> 대소문자 무시</label></div>'+
    '<div class="res"><div class="score"><span class="big"></span><span class="cnt"></span></div>'+
    '<div class="lg"><span><i class="k" style="background:rgba(70,215,110,.3);border:1px solid #16803d"></i>맞음</span><span><i class="k" style="background:rgba(255,90,90,.22);border:1px solid #c62828"></i>틀림·더 씀</span><span><i class="k" style="background:rgba(255,200,60,.35);border:1px solid #d08a00"></i>빠짐</span><span><i class="k" style="background:#f3f3f3;border:1px solid #c4c4c4"></i>아직 안 쓴 부분</span></div>'+
    '<p class="lab">내가 쓴 글</p><div class="view vu"></div><p class="lab">템플릿 (빠뜨린 글자 표시)</p><div class="view vt"></div></div></div>';
  document.body.appendChild(ov);
  var q=function(s){ return ov.querySelector(s); };
  var ta=q('textarea'), tplBox=q('.tpltxt'), cur=null, tplText='';
  function open(pr){
    var h=pr.querySelector('.h');
    cur=(h.querySelector('b')||{}).textContent||'T';
    q('h3').innerHTML='<b>'+cur+'</b>'+((h.querySelector('span')||{}).textContent||'');
    var ans=pr.querySelector('.ans');
    var qq=pr.querySelector('.q'); q('.qbox').innerHTML=qq?'<p class="lab">문제</p><div class="qtxt">'+qq.innerHTML+'</div>':'';
    tplBox.innerHTML=ans.innerHTML;
    tplText=[].slice.call(ans.querySelectorAll('p')).map(function(p){ return p.textContent; }).join('\n');
    ta.value=memos[cur]||''; q('.res').style.display='none';
    ov.classList.add('on'); document.body.style.overflow='hidden'; ov.scrollTop=0;
  }
  function close(){ ov.classList.remove('on'); document.body.style.overflow=''; }
  probs.forEach(function(pr){
    var b=document.createElement('button'); b.className='ty-open'; b.type='button'; b.textContent='✍ 따라쓰기';
    b.addEventListener('click',function(e){ e.preventDefault(); open(pr); });
    pr.querySelector('.h').appendChild(b);
  });
  q('.close').onclick=close;
  ov.addEventListener('click',function(e){ if(e.target===ov) close(); });
  document.addEventListener('keydown',function(e){ if(e.key==='Escape' && ov.classList.contains('on')) close(); });
  q('.hide').onclick=function(){ var on=tplBox.classList.toggle('hide'); this.classList.toggle('on',on); this.textContent=on?'보이기':'가리기'; };
  ta.addEventListener('input',function(){ memos[cur]=ta.value; saveMemo(); });
  q('.clear').onclick=function(){ ta.value=''; memos[cur]=''; saveMemo(); q('.res').style.display='none'; ta.focus(); };

  var isWS=function(c){ return /\s/.test(c); };
  function norm(c,ci){ c=c.replace(/[‘’`´]/g,"'").replace(/[“”]/g,'"').replace(/[–—]/g,'-'); return ci?c.toLowerCase():c; }
  function esc(s){ return s.replace(/[&<>]/g,function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c]; }); }
  q('.grade').onclick=function(){
    var ci=q('.ci').checked, A=Array.from(tplText), B=Array.from(ta.value), a=[], ai=[], b=[];
    A.forEach(function(c,i){ if(!isWS(c)){ a.push(norm(c,ci)); ai.push(i); } });
    B.forEach(function(c){ if(!isWS(c)) b.push(norm(c,ci)); });
    var n=a.length, m=b.length, W=m+1, F=new Uint16Array((n+1)*(m+1)), i, j;
    for(i=1;i<=n;i++) for(j=1;j<=m;j++)
      F[i*W+j]= a[i-1]===b[j-1] ? F[(i-1)*W+j-1]+1 : Math.max(F[(i-1)*W+j],F[i*W+j-1]);
    // 어디까지 썼는지: (맞음 - 빠짐)이 가장 큰 지점 → 중간까지만 써도 그 부분만 채점
    var end=0, best=-1e9;
    for(i=0;i<=n;i++){ var sc=2*F[i*W+m]-i; if(sc>=best){ best=sc; end=i; } }
    var tOk=[], uOk=[], miss=[]; for(j=0;j<=m;j++) miss.push('');
    i=end; j=m;
    while(i>0||j>0){
      if(i>0&&j>0&&a[i-1]===b[j-1]&&F[i*W+j]===F[(i-1)*W+j-1]+1){ tOk[i-1]=uOk[j-1]=true; i--; j--; }
      else if(i>0&&(j===0||F[(i-1)*W+j]>=F[i*W+j-1])){ miss[j]=A[ai[i-1]]+miss[j]; i--; }
      else j--;
    }
    var h='', k=0;
    B.forEach(function(c){
      if(isWS(c)){ h+=esc(c); return; }
      if(miss[k]) h+='<span class="miss">'+esc(miss[k])+'</span>';
      h+='<span class="'+(uOk[k]?'ok':'bad')+'">'+esc(c)+'</span>'; k++;
    });
    if(miss[m]) h+='<span class="miss">'+esc(miss[m])+'</span>';
    q('.vu').innerHTML=h||'<span class="rest">(비어 있음)</span>';
    var t=''; k=0;
    A.forEach(function(c){
      if(isWS(c)){ t+=esc(c); return; }
      t+= k>=end ? '<span class="rest">'+esc(c)+'</span>' : tOk[k] ? esc(c) : '<span class="miss">'+esc(c)+'</span>'; k++;
    });
    q('.vt').innerHTML=t;
    var ok=F[end*W+m], ex=m-ok;
    var pct=end?Math.max(0,Math.round((ok-ex)/end*1000)/10):0;
    q('.big').textContent=pct+'%';
    q('.cnt').textContent='맞음 '+ok+' · 빠짐 '+(end-ok)+' · 틀림·더 씀 '+ex+' · 쓴 범위 '+end+'/'+n+'자'+(end<n?' (나머지는 채점 안 함)':'');
    q('.res').style.display='block';
    q('.res').scrollIntoView({behavior:'smooth',block:'start'});
  };
})();
</script>"""

html = html.replace("</head>", TYPE_CSS + "</head>", 1)
html = html.replace("</body>", TYPE_JS + "</body>", 1)
# 마우스 휠로 쪽 넘기기 (세로 휠 → 다음/이전 쪽)
WHEEL_JS = r"""<script id="wheel-script">
(function(){
  var book=document.querySelector('.book'); if(!book) return;
  var sheets=[].slice.call(book.querySelectorAll('.sheet')), lock=false, acc=0, t=null;
  function cur(){
    var r=book.getBoundingClientRect(), mid=r.left+r.width/2, best=0, d=1e9;
    sheets.forEach(function(s,i){ var b=s.getBoundingClientRect(), x=Math.abs(b.left+b.width/2-mid); if(x<d){d=x;best=i;} });
    return best;
  }
  function go(i){
    i=Math.max(0,Math.min(sheets.length-1,i));
    sheets[i].scrollIntoView({behavior:'smooth',block:'nearest',inline:'start'});
  }
  book.addEventListener('wheel',function(e){
    if(e.ctrlKey) return;                                   // 확대/축소는 그대로
    if(Math.abs(e.deltaX)>Math.abs(e.deltaY)) return;       // 트랙패드 가로 밀기는 그대로
    var el=e.target;                                        // 안쪽 스크롤 칸(textarea 등)은 그대로
    while(el && el!==book){ if(el.scrollHeight>el.clientHeight+1 && /(auto|scroll)/.test(getComputedStyle(el).overflowY)) return; el=el.parentElement; }
    e.preventDefault();
    if(lock) return;
    acc+=e.deltaMode===1 ? e.deltaY*30 : e.deltaY;
    clearTimeout(t); t=setTimeout(function(){ acc=0; },200);
    if(Math.abs(acc)<40) return;
    go(cur()+(acc>0?1:-1)); acc=0; lock=true;
    setTimeout(function(){ lock=false; },550);
  },{passive:false});
})();
</script>"""
html = html.replace("</body>", WHEEL_JS + "</body>", 1)
pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
pathlib.Path(out).write_text(html, encoding="utf-8")
print("written", out)
