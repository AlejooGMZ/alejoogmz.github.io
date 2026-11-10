"""Genera _build/revision-traducciones.html: todos los textos ES/EN lado a lado. Uso: python3 _build/revision_traducciones.py"""
import json,re,html,subprocess,os
from bs4 import BeautifulSoup
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));os.chdir(ROOT)
EN=json.loads(subprocess.check_output(['node','-e',"global.window={};require('./js/i18n-en.js');for(const f of require('fs').readdirSync('js/en'))require('./js/en/'+f);process.stdout.write(JSON.stringify(window.I18N_EN))"]))
def clean(s):
    s=re.sub(r'<br\s*/?>','\n',s); s=BeautifulSoup(s,'html.parser').get_text(); return re.sub(r'[ \t]+',' ',s).strip()
pages=[('Navegación y pie (todas las páginas)','js/main.js'),('Inicio','index.html'),('Proyectos','proyectos.html'),('Sobre mí','sobre-mi.html'),('Experiencia','experiencia.html'),
 ('Caso · VoltBank AutoConvert','casos/voltbank.html'),('Caso · Benz Display','casos/benz-display.html'),('Caso · Petmatch','casos/petmatch.html'),('Caso · Park Planner','casos/park-planner.html'),('Página 404','404.html')]
seen=set();groups=[];total=0
for name,f in pages:
    src=open(f).read()
    if f.endswith('.js'):
        src=re.sub(r'\$\{[^}]*\}','',' '.join(re.findall(r'`(.*?)`',src,re.S)))
    soup=BeautifulSoup(src,'html.parser');rows=[]
    for el in soup.select('[data-i18n]'):
        k=el['data-i18n']
        if k in seen: continue
        seen.add(k); es=clean(el.decode_contents())
        if es: rows.append((k,es,clean(EN.get(k,'⚠ SIN TRADUCCIÓN'))))
    for el in soup.select('[data-i18n-attr]'):
        for pair in el['data-i18n-attr'].split(';'):
            a,k=pair.split(':')
            if k in seen: continue
            seen.add(k); rows.append((k,(el.get(a) or '')+('  [texto alternativo]' if a=='alt' else f'  [{a}]'),clean(EN.get(k,'⚠ SIN TRADUCCIÓN'))))
    groups.append((name,rows));total+=len(rows)
css='''body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;background:#F2F2F2;color:#0E1F26;margin:0;padding:40px 24px;font-size:15px;line-height:1.5}
.w{max-width:1200px;margin:0 auto}h1{font-size:40px;margin:0 0 8px}p.i{color:#4F5E63;max-width:760px}
nav{display:flex;flex-wrap:wrap;gap:8px;margin:24px 0}nav a{font-size:12px;letter-spacing:.08em;text-transform:uppercase;border:1px solid #0E1F26;padding:6px 10px;color:#0E1F26;text-decoration:none;border-radius:2px}
h2{font-size:24px;margin:48px 0 12px;padding-top:12px;border-top:3px solid #F93738}
table{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden}
th{text-align:left;font-size:12px;letter-spacing:.1em;text-transform:uppercase;padding:12px;background:#0E1F26;color:#fff}
td{vertical-align:top;padding:10px 12px;border-top:1px solid #D3D9DA;white-space:pre-line}
td.n{color:#4F5E63;font-size:12px;width:56px}td.es,td.en{width:46%}
tr:hover td{background:#E4F7FD}.k{display:block;color:#647074;font-size:10px;margin-top:4px;font-family:ui-monospace,monospace}
@media (max-width:700px){table,thead,tbody,tr,td{display:block}thead{display:none}td{border:0;padding:4px 12px}tr{border-top:1px solid #D3D9DA;padding:8px 0}td.es,td.en,td.n{width:auto}td.en{color:#1C333C;font-style:italic}}
@media print{body{background:#fff}nav{display:none}tr{break-inside:avoid}}'''
out=[f'<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Revisión de traducciones</title><style>{css}</style></head><body><div class="w">',
 '<h1>Revisión de traducciones</h1>',f'<p class="i">Todos los textos del portafolio en español e inglés, página por página ({total} textos). Para corregir algo, indica la página y el número (por ejemplo: «Inicio 12: …»). Los nombres propios, marcas y herramientas no se traducen y no aparecen aquí.</p>',
 '<nav>'+''.join(f'<a href="#g{i}">{html.escape(n)} · {len(r)}</a>' for i,(n,r) in enumerate(groups))+'</nav>']
for i,(n,rows) in enumerate(groups):
    out.append(f'<h2 id="g{i}">{html.escape(n)}</h2><table><thead><tr><th>#</th><th>Español</th><th>English</th></tr></thead><tbody>')
    out+= [f'<tr><td class="n">{j}</td><td class="es">{html.escape(es)}<span class="k">{html.escape(k)}</span></td><td class="en">{html.escape(en)}</td></tr>' for j,(k,es,en) in enumerate(rows,1)]
    out.append('</tbody></table>')
out.append('</div></body></html>')
open('_build/revision-traducciones.html','w').write('\n'.join(out))
print(total,'textos ·',sum(1 for n,r in groups for x in r if 'SIN TRADUCCIÓN' in x[2]),'sin traducción')
