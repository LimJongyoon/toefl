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
pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
pathlib.Path(out).write_text(html, encoding="utf-8")
print("written", out)
