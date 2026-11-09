#!/usr/bin/env python3
"""Make a preview copy of public_html with relative links (for a claude.ai artifact).
    python3 tools/make_preview.py <out_dir>
Forms and chat show a "preview only" note there."""
import os, re, shutil, sys
SRC='/home/user/Roofers/public_html'; OUT=sys.argv[1]
SKIP_EXT=('.php','.md','.csv','.xml','.txt','.json','.htaccess')
files=[]
for root,_,fs in os.walk(SRC):
    for f in fs:
        rel=os.path.relpath(os.path.join(root,f),SRC)
        if rel.endswith(SKIP_EXT) or f.startswith('.') or rel=='styleguide.html': continue
        if rel.endswith('og-default.jpg'): continue
        files.append(rel)
def fix_url(u, prefix):
    if u.startswith('//') or not u.startswith('/'): return u
    path, _, frag = u[1:].partition('#')
    if path=='' : path='index.html'
    elif path.endswith('/'): path+='index.html'
    return prefix+path+(('#'+frag) if frag else '')
for rel in files:
    s_path=os.path.join(SRC,rel); d_path=os.path.join(OUT,rel)
    os.makedirs(os.path.dirname(d_path),exist_ok=True)
    if not rel.endswith('.html'):
        shutil.copyfile(s_path,d_path); continue
    depth=rel.count('/'); prefix='../'*depth
    h=open(s_path,encoding='utf-8').read()
    h=re.sub(r'\b(href|src|action|poster)="(/[^"]*)"', lambda m: f'{m.group(1)}="{fix_url(m.group(2),prefix)}"', h)
    h=re.sub(r'\b(srcset|imagesrcset)="([^"]*)"', lambda m: m.group(1)+'="'+re.sub(r'(^|,\s*)/', lambda n: n.group(1)+prefix, m.group(2))+'"', h)
    h=re.sub(r'url\(/', 'url('+prefix, h)
    h=h.replace('window.SITE={', 'window.SITE={"preview":true,"root":"'+prefix+'",')
    if rel=='index.html':
        # artifact page: strip document skeleton tags, keep head content + body content
        cls=re.search(r'<html[^>]*class="([^"]*)"',h).group(1)
        head=re.search(r'<head>(.*?)</head>',h,re.S).group(1)
        body=re.search(r'<body[^>]*>(.*)</body>',h,re.S).group(1)
        head=re.sub(r'<meta charset="utf-8">\s*|<meta name="viewport"[^>]*>\s*','',head)
        head=re.sub(r'<title>.*?</title>','<title>Roof Web Studio Website</title>',head)
        h=head.replace('<title>Roof Web Studio Website</title>','<title>Roof Web Studio Website</title>\n<script>document.documentElement.className+=" '+cls+'"</script>',1)+'\n'+body
    open(d_path,'w',encoding='utf-8').write(h)
# patch JS for preview
mj=os.path.join(OUT,'assets/js/main.js'); s=open(mj).read()
s=s.replace('"/assets/img/icons.svg#"','(cfg.root||"/")+"assets/img/icons.svg#"')
s=s.replace('s.src = "/assets/js/chat.js"','s.src = (cfg.root||"/")+"assets/js/chat.js"')
s=s.replace('      var btn = form.querySelector("[type=submit]"), label = btn.innerHTML;','''      if (cfg.preview) { if (status) { status.textContent = "Preview only: this form sends leads once the site is live on your hosting."; status.setAttribute("data-show", "true"); status.style.borderLeftColor = "#F26B1D"; status.style.background = "#FFF1E6"; status.style.color = "#6B2A05"; } return; }
      var btn = form.querySelector("[type=submit]"), label = btn.innerHTML;''')
open(mj,'w').write(s)
cj=os.path.join(OUT,'assets/js/chat.js'); s=open(cj).read()
s=s.replace('el.innerHTML = html;','el.innerHTML = String(html).replace(/href="\\/([^"#]*?)(#[^"]*)?"/g, function (m, p, f) { return \'href="\' + (cfg.root || "") + (p ? (p.slice(-1) === "/" ? p + "index.html" : p) : "index.html") + (f || "") + \'"\'; });')
s=s.replace('    typing(true);\n    fetch("/send.php"','    if (cfg.preview) { input.disabled = false; lead = null; botSay("Preview only: in the live site your details are sent to the team here. Nothing was sent."); setChips(CHIPS); return; }\n    typing(true);\n    fetch("/send.php"')
open(cj,'w').write(s)
print(len(files))
