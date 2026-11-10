"""Genera casos/<slug>.html y js/en/<slug>.js a partir de _build/casos/<slug>.py
Cada texto traducible es una tupla (es, en). Uso: python3 _build/build_case.py voltbank"""
import sys, json, html, importlib.util, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARR = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>'
EN = {}; CNT = [0]; SLUG = ''

def t(v, tag='p', cls='', attrs=''):
    """Texto con i18n. v = str o (es, en)."""
    if v is None: return ''
    if isinstance(v, tuple):
        CNT[0] += 1; k = f'{SLUG}.{CNT[0]:03d}'; EN[k] = v[1]
        return f'<{tag}{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} data-i18n="{k}"{attrs}>{v[0]}</{tag}>'
    return f'<{tag}{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}{attrs}>{v}</{tag}>'
def es(v): return v[0] if isinstance(v, tuple) else v
def alt(v):
    if isinstance(v, tuple):
        CNT[0] += 1; k = f'{SLUG}.{CNT[0]:03d}'; EN[k] = v[1]
        return f'alt="{html.escape(v[0])}" data-i18n-attr="alt:{k}"'
    return f'alt="{html.escape(v or "")}"'
def img(src, a='', cls='', extra=''):
    return f'<img src="../assets/img/{src}.webp" {alt(a)} loading="lazy" onerror="this.style.display=\'none\'"{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}{extra}>'

def title(num, txt):
    return f'<div class="c-title reveal"><p class="t-et-l">{num}</p>{t(txt,"h2","t-h1")}</div>'

# ---------- bloques ----------
def b_contexto(b):
    return f'''<div class="contexto reveal"><div class="contexto__l">{t(b["label"],"p","c-label c-label--l")}{t(b["titulo"],"p","t-sub1")}</div>
<div class="contexto__r">{"".join(t(p,"p","t-c18 "+("c-gris" if i==0 else "")) for i,p in enumerate(b["parrafos"]))}</div></div>'''
def b_cifras(b):
    items = ''.join(f'<div class="cifra">{t(n,"p","t-display-s"+(" c-cian" if hl else " c-blanco"),f" data-count={chr(34)}{es(n)}{chr(34)}")}{t(d,"p","t-c16")}</div>' for n,d,hl in b["items"])
    return f'<div class="cifras reveal">{t(b["label"],"p","t-et-m c-cian")}<div class="cifras__row" data-stagger=".1">{items}</div></div>'
def b_tags(b):
    return f'<div class="c-stack reveal" style="gap:12px">{t(b["label"],"p","c-label c-label--l")}<div class="tags-row" data-stagger=".05">{"".join(t(x,"span","tag") for x in b["items"])}</div></div>'
def b_hipotesis(b):
    cards = ''.join(f'<div class="card">{t(k,"p","num")}{t(h,"h3","t-sub2")}{t(d,"p","t-c16 c-gris")}</div>' for k,h,d in b["items"])
    return f'''<div class="c-stack">{t(b["label"],"p","c-label reveal")}<div class="principal reveal">{t(b["principal_label"],"p","t-et-s c-gris")}{t(b["principal"],"p","t-sub1")}</div>
<div class="g3" data-stagger=".1">{cards}</div></div>'''
def b_benchmark(b):
    refs = ''
    for r in b["refs"]:
        ims = ''.join(img(s, r.get("alt",""), "") for s in r["imgs"])
        refs += f'''<div class="card ref"><div class="ref__head">{t(r["nombre"],"h3","t-sub1")}{t(r["sub"],"p","t-et-s c-gris")}</div>
<div class="ref__imgs">{ims}</div>
<div class="ref__b">{t(("✓  "+es(b["ok_label"]),"✓  "+b["ok_label"][1]),"p","t-et-m ok")}{t(r["ok"],"p","t-c16 c-gris")}</div>
<div class="ref__b">{t(("!  "+es(b["ko_label"]),"!  "+b["ko_label"][1]),"p","t-et-m ko")}{t(r["ko"],"p","t-c16 c-gris")}</div>
<div class="ref__take">{t(("→  "+es(b["take_label"]),"→  "+b["take_label"][1]),"p","t-et-m")}{t(r["take"],"p","t-c16b")}</div></div>'''
    head = ''.join(t(h,"th","",' scope="col"') for h in b["tabla"][0])
    rows = ''.join('<tr>'+''.join(t(c,"td") for c in row)+'</tr>' for row in b["tabla"][1:])
    return f'''<div class="c-stack">{t(b["label"],"p","c-label c-label--l reveal")}{t(b["intro"],"p","t-c18 c-gris reveal")}
<div class="g3" data-stagger=".1">{refs}</div>
<div class="tabla reveal"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div></div>'''
def b_dolor(b):
    return f'<div class="dolor reveal">{t(b["label"],"p","t-et-m c-cian")}<div class="dolor__list" data-stagger=".08">{"".join(t(x,"p","t-c16") for x in b["items"])}</div></div>'
def b_persona(b):
    return f'''<div class="persona reveal"><div class="persona__card" role="button" tabindex="0" aria-pressed="false" aria-label="{es(("Ver la otra cara de la persona",""))}" onclick="this.classList.toggle('is-flip');this.setAttribute('aria-pressed',this.classList.contains('is-flip'))" onkeydown="if(event.key==='Enter'||event.key===' '){{event.preventDefault();this.click()}}">{img(b["front"],b.get("alt_back",("Mapa de recorrido de la persona","Persona journey map")),"persona__back")}{img(b["back"],b["alt"],"persona__front")}</div>
<div class="persona__txt">{t(("↻  Toca la ficha para ver la otra cara","↻  Tap the card to see the other side"),"p","persona__hint")}<div>{t(("Persona","Persona"),"p","t-et-m")}{t(b["nombre"],"h3","t-h3")}</div>{t(b["txt"],"p","t-c16 c-gris")}</div></div>'''
def b_objetivos(b):
    cards = ''.join(f'<div class="card" style="padding:24px 32px;gap:8px">{t(k,"p","num num--cian")}{t(h,"h3","t-sub2")}{t(d,"p","t-c16 c-gris")}</div>' for k,h,d in b["items"])
    return f'''<div class="c-stack">{t(b["label"],"p","c-label reveal")}
<div class="card {"card--dark" if b.get("oscuro") else "card--cian"} reveal" style="padding:32px 40px;gap:8px">{t(b["main_label"],"p","t-et-m"+(" c-cian" if b.get("oscuro") else ""))}{t(b["main"],"p","t-sub1")}</div>
<div class="g3" data-stagger=".1">{cards}</div></div>'''
def b_estrategia(b):
    nc = "num" if b.get("num_rojo") else "num num--cian"; cc = "card card--gris" if b.get("gris") else "card"
    cards = ''.join(f'<div class="{cc}">{t(k,"p",nc)}{t(h,"h3","t-sub2")}{t(d,"p","t-c16 c-gris")}</div>' for k,h,d in b["principios"])
    p2s = ''
    if b.get("p2s"):
        rows = ''.join(f'<div class="p2s__row">{t(a,"span","t-c14")}{t(("→  "+es(c),"→  "+c[1]) if isinstance(c,tuple) else "→  "+c,"span","t-c14b")}</div>' for a,c in b["p2s"]["rows"])
        p2s = f'<div class="p2s">{t(b["p2s"]["label"],"p","t-et-m c-cian")}<div style="height:12px"></div>{rows}</div>'
    return f'''<div class="c-stack">{t(b["label"],"p","c-label reveal")}<div class="idea reveal">{t(b["idea"],"p","t-sub1")}</div>
<div class="principios-c" data-stagger=".08">{cards}{p2s}</div></div>'''
def b_decisiones(b):
    m = b["main"]
    ims = ''.join(img(s, m["alt"]) for s in m["imgs"])
    cols = ''.join(f'<div class="deci">{t(k,"p","t-et-m")}{t(h,"h3","t-sub1")}{t(("Por qué","Why"),"p","t-et-m c-gris")}{t(d,"p","t-c18")}</div>' for k,h,d in b["cols"])
    return f'''{t(b["label"],"p","c-label reveal")}
<div class="deci-main reveal{" deci-main--fondo" + (" deci-main--sr" if m.get("sr") else "") if m.get("fondo") else (" deci-main--one" if len(m["imgs"])==1 else "")}"><div class="deci-main__imgs" data-stagger=".1">{ims}</div>
<div class="deci-main__txt">{t(m["k"],"p","t-et-m",' style="color:var(--gris-300)"')}{t(m["h"],"h3","t-sub1")}{t(("Por qué","Why"),"p","t-et-m",' style="color:var(--cian-100)"')}{t(m["d"],"p","t-c18")}</div></div>
<div class="deci-cols" data-stagger=".1">{cols}</div>'''
def b_val_imgs(b):
    def fig(s_, c):
        if isinstance(s_, list): return f'<figure><div class="img img--multi">{"".join(img(x,c) for x in s_)}</div>{t(c,"figcaption","t-et-m c-gris")}</figure>'
        return f'<figure><div class="img">{img(s_,c)}</div>{t(c,"figcaption","t-et-m c-gris")}</figure>'
    return '<div class="val-imgs reveal" data-stagger=".1">'+''.join(fig(s_,c) for s_,c in b["items"])+'</div>'
def b_rondas(b):
    out = ''
    for r in b["rondas"]:
        rows = ''.join(f'<div class="ronda__row">{t(h,"p","t-sub3")}<span class="arrow" aria-hidden="true">→</span>{t(c,"p","t-c18")}</div>' for h,c in r["rows"])
        out += f'''<div class="ronda reveal">{t(r["tag"],"p","ronda__tag")}<div class="ronda__head">{t(("Hallazgo","Finding"),"p","t-et-m c-gris")}<span></span>{t(("Cambio en el diseño","Design change"),"p","t-et-m")}</div>{rows}</div>'''
    return out
def b_solucion(b):
    vid = ''
    if b.get("videos"):
        vs = ''
        for v in b["videos"]:
            if v.get("src"): vs += f'<video src="../assets/video/{v["src"]}.mp4" poster="../assets/video/{v["src"]}-poster.jpg" autoplay muted loop playsinline preload="metadata" aria-label="{html.escape(es(v["alt"]))}" class="ph--{v["k"]}"></video>'
            else: vs += f'<div class="ph ph--{v["k"]}">{es(v["alt"])}</div>'
        vid = f'<div class="sol-video reveal">{vs}</div>'
        if b.get("poster") and not any(v.get("src") for v in b["videos"]):
            vid = f'<div class="sol-video sol-video--poster reveal">{img(b["poster"], b["videos"][0]["alt"])}</div>'
    feats = ''.join(f'<div class="feat reveal"><div class="feat__img">{img(s,h)}</div><div class="feat__txt">{t(k,"p","t-et-m")}{t(h,"h3","t-sub1")}{t(d,"p","t-c18 c-gris")}</div></div>' for k,s,h,d in b["feats"])
    g = b["guia"]
    return f'''{vid}<div class="zig">{feats}</div>
<div class="guia reveal">{img(g["img"],g["alt"])}<div class="c-stack" style="gap:12px">{t(("Design system","Design system"),"p","t-et-m",' style="color:var(--gris-300)"')}{t(g["h"],"h3","t-sub1")}{t(g["d"],"p","t-c16")}</div></div>'''
def b_resultados(b):
    ok = ''.join(t(("✓  "+es(x),"✓  "+x[1]),"p","t-c16") for x in b["ok"])
    mets = ''.join(f'<div>{t(("→  "+es(h),"→  "+h[1]),"p","t-c16b")}{t(d,"p","t-c14")}</div>' for h,d in b["metricas"])
    pasos = ''.join(f'<div class="card">{t(h,"h3","t-sub3b")}{t(d,"p","t-c18 c-gris")}</div>' for h,d in b["pasos"])
    return f'''<div class="res-bento"><div class="card reveal">{t(b["ok_label"],"p","t-et-m")}{ok}</div>
<div class="card card--cian reveal" style="--d:.1s">{t(("Cómo lo mediría","How I would measure it"),"p","t-et-m")}<div class="metricas">{mets}</div></div></div>
<div class="aprendi reveal">{t(("Qué aprendí","What I learned"),"p","t-et-m")}<div class="aprendi__band">{t(b["aprendi"],"p","t-cita")}</div></div>
<div class="c-stack" style="gap:16px;padding-top:40px">{t(("Próximos pasos","Next steps"),"p","t-et-m reveal")}<div class="pasos" data-stagger=".1">{pasos}</div></div>'''

def b_bento(b):
    cls={"rojo":"card card--rojo-line","cian":"card card--cian","dark":"card card--dark"}
    return '<div class="bento3" data-stagger=".1">'+''.join(f'<div class="{cls[k]}">{t(h,"h3","t-sub1")}{t(d,"p","t-c16")}</div>' for k,h,d in b["items"])+'</div>'
def b_intro(b):
    return t(b["txt"],"p","t-c18 c-gris reveal")

def b_preguntas(b):
    cards = ''.join(f'<div class="card" style="padding:24px 32px;gap:8px">{t(k,"p","num")}{t(h,"h3","t-sub2")}{t(d,"p","t-c16 c-gris")}</div>' for k,h,d in b["items"])
    return f"""<div class="c-stack">{t(b["label"],"p","c-label c-label--l reveal")}<div class="principal reveal">{t(b["principal_label"],"p","t-et-s c-gris")}{t(b["principal"],"p","t-sub1")}</div>
<div class="g4" data-stagger=".1">{cards}</div></div>"""
def b_insights(b):
    cards = ''.join(f'<div class="card" style="padding:24px 32px">{t(k,"p","t-et-m")}{t(h,"h3","t-sub1")}{t(d,"p","t-c16 c-gris")}</div>' for k,h,d in b["items"])
    voces = ''
    if b.get("voces"):
        voces = '<div class="g4 voces" data-stagger=".08">'+''.join(f'<blockquote class="voz">{t(q,"p","t-c16b")}{t(w,"p","t-et-s c-gris")}</blockquote>' for q,w in b["voces"])+'</div>'
    return f'<div class="c-stack">{t(b["label"],"p","c-label c-label--l reveal")}<div class="g3" data-stagger=".1">{cards}</div>{voces}</div>'
def b_auditoria(b):
    refs = ''
    for r in b["refs"]:
        ims = f'<div class="ref__imgs">{"".join(img(s_, r.get("alt","")) for s_ in r["imgs"])}</div>' if r.get("imgs") else ''
        refs += f"""<div class="card ref">{f'<div class="ref__head">{t(r["nombre"],"h3","t-sub2")}{t(r["sub"],"p","t-et-s c-gris")}</div>'}{ims}
<div class="ref__b">{t(("✓  "+es(b["ok_label"]),"✓  "+b["ok_label"][1]),"p","t-et-m ok")}{t(r["ok"],"p","t-c14 c-gris")}</div>
<div class="ref__b">{t(("!  "+es(b["ko_label"]),"!  "+b["ko_label"][1]),"p","t-et-m ko")}{t(r["ko"],"p","t-c14 c-gris")}</div>
<div class="ref__take">{t(("→  "+es(b["take_label"]),"→  "+b["take_label"][1]),"p","t-et-m")}{t(r["take"],"p","t-c16b")}</div></div>"""
    n = len(b["refs"]); grid = {3:"g3",4:"g4"}.get(n,"g3")
    head = ''.join(t(h,"th","",' scope="col"') for h in b["tabla"][0])
    rows = ''.join('<tr>'+''.join(t(c,"td") for c in row)+'</tr>' for row in b["tabla"][1:])
    op = f'<div class="card card--cian reveal" style="padding:32px 40px;gap:8px">{t(b["oportunidad_label"],"p","t-et-m")}{t(b["oportunidad"],"p","t-sub1")}</div>' if b.get("oportunidad") else ''
    return f"""<div class="c-stack">{t(b["label"],"p","c-label c-label--l reveal")}{t(b["intro"],"p","t-c18 c-gris reveal")}
<div class="{grid}" data-stagger=".1">{refs}{op.replace(" reveal","") if n==5 else ""}</div>
<div class="tabla reveal"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>{op if n!=5 else ""}</div>"""
def b_afinidad(b):
    cats = ''.join(f'<div class="card afin">{t(h,"p","t-et-l c-cian7")}{"".join(t(q,"p","t-c16") for q in qs)}</div>' for h,qs in b["items"])
    return f'<div class="c-stack">{t(b["label"],"p","c-label reveal")}<div class="g4" data-stagger=".1">{cats}</div></div>'
def b_conclusiones(b):
    cards = ''.join(f'<div class="card concl">{t(n,"p","t-h4 "+("ok" if good else "ko"))}{t(d,"p","t-c16 c-gris")}{t(("→  "+es(k),"→  "+k[1]),"p","t-c16b")}</div>' for n,d,k,good in b["items"])
    return f'<div class="c-stack">{t(b["label"],"p","c-label reveal")}<div class="g3" data-stagger=".08">{cards}</div></div>'
def b_tabla_dolor(b):
    rows = ''.join(f'<div class="tdol__row">{t(a,"p","t-c16 c-gris")}{t(c,"p","t-c16b")}</div>' for a,c in b["rows"])
    return f'<div class="tdol reveal"><div class="tdol__row tdol__head">{t(b["l1"],"p","t-et-m c-gris")}{t(b["l2"],"p","t-et-m c-gris")}</div>{rows}</div>'
def b_decisiones_lista(b):
    cells = ''
    for it in b["items"]:
        if it.get("imgs"):
            span = ' style="grid-row:span 2"' if it.get("span") else ''
            cells += f'<div class="dl__img{" dl__img--fila" if len(it["imgs"])>1 else ""} reveal"{span}>{"".join(img(x, it["alt"]) for x in it["imgs"])}</div>'
        cells += f'<div class="dl__txt reveal">{t(it["k"],"p","t-et-m")}{t(it["h"],"h3","t-sub1")}{t(("Por qué","Why"),"p","t-et-m c-gris")}{t(it["d"],"p","t-c18")}</div>'
    return f'{t(b["label"],"p","c-label reveal")}<div class="dl">{cells}</div>'
def b_label(b):
    return t(b["txt"],"p","c-label reveal")
def b_resultados3(b):
    ok = ''.join(t(("✓  "+es(x),"✓  "+x[1]),"p","t-c16") for x in b["ok"])
    voz = ''.join(t(q,"p","t-sub3") for q in b["voz"])
    med = ''.join(t(("→  "+es(x),"→  "+x[1]),"p","t-c16") for x in b["medir"])
    pasos = ''.join(f'<div class="card">{t(h,"h3","t-sub3b")}{t(d,"p","t-c18 c-gris")}</div>' for h,d in b["pasos"])
    np_ = len(b["pasos"])
    return f"""<div class="bento3"><div class="card reveal">{t(b["ok_label"],"p","t-et-m")}{ok}</div>
<div class="card card--dark reveal" style="--d:.1s">{t(("Voz de los usuarios","Users’ voices"),"p","t-et-m c-cian")}{voz}</div>
<div class="card card--cian reveal" style="--d:.2s">{t(("Cómo lo mediría","How I would measure it"),"p","t-et-m")}{med}</div></div>
<div class="aprendi reveal">{t(("Qué aprendí","What I learned"),"p","t-et-m")}<div class="aprendi__band">{t(b["aprendi"],"p","t-cita")}</div></div>
<div class="c-stack" style="gap:16px;padding-top:40px">{t(("Próximos pasos","Next steps"),"p","t-et-m reveal")}<div class="pasos pasos--{np_}" data-stagger=".1">{pasos}</div></div>"""
def media(m, a):
    """imagen o video (dict con src video y poster)"""
    if isinstance(m, dict):
        if m.get("video"): return f'<video src="../assets/video/{m["video"]}.mp4" poster="../assets/video/{m["video"]}-poster.jpg" autoplay muted loop playsinline preload="metadata" aria-label="{html.escape(es(a))}"></video>'
        return f'<div class="ph">{es(m.get("ph",""))}</div>'
    return img(m, a)
def b_feats_grid(b):
    """Benz: filas de 2 (video+texto | texto+video) y fila central texto | video | texto"""
    out = ''
    for row in b["filas"]:
        if row["tipo"] == "solo":
            k,m,h,d = row["items"]
            md = f'<div class="fg__media">{media(m,h)}</div>'; tx = f'<div class="fg__txt">{t(k,"p","t-et-m")}{t(h,"h3","t-sub1")}{t(d,"p","t-c18 c-gris")}</div>'
            out += f'<div class="fg fg--solo{" fg--der" if row.get("der") else ""} reveal">{tx+md if row.get("der") else md+tx}</div>'
            continue
        if row["tipo"] == "ancho":
            k,m,h,d = row["items"]
            out += f'<div class="fg fg--ancho reveal"><div class="fg__media">{media(m,h)}</div><div class="fg__txt">{t(k,"p","t-et-m")}{t(h,"h3","t-sub1")}{t(d,"p","t-c18 c-gris")}</div></div>'
            continue
        if row["tipo"] == "par":
            cells = ''
            for i,(k,m,h,d) in enumerate(row["items"]):
                tx = f'<div class="fg__txt">{t(k,"p","t-et-m")}{t(h,"h3","t-sub1")}{t(d,"p","t-c18 c-gris")}</div>'
                md = f'<div class="fg__media">{media(m,h)}</div>'
                cells += f'<div class="fg__cell reveal">{md+tx if i==0 else tx+md}</div>'
            out += f'<div class="fg fg--par{" fg--escalon" if row.get("escalon") else ""}">{cells}</div>'
        else:
            (k1,h1,d1),(m,a),(k2,h2,d2) = row["items"]
            out += f'<div class="fg fg--trio reveal"><div class="fg__txt">{t(k1,"p","t-et-m")}{t(h1,"h3","t-sub1")}{t(d1,"p","t-c18 c-gris")}</div><div class="fg__media">{media(m,a)}</div><div class="fg__txt">{t(k2,"p","t-et-m")}{t(h2,"h3","t-sub1")}{t(d2,"p","t-c18 c-gris")}</div></div>'
    g = b["guia"]
    return f"""<div class="zig zig--grid">{out}</div>
<div class="guia guia--light{" guia--borde" if g.get("borde") else ""} reveal">{img(g["img"],g["alt"])}<div class="c-stack" style="gap:12px">{t(("Design system","Design system"),"p","t-et-m c-gris")}{t(g["h"],"h3","t-sub1")}{t(g["d"],"p","t-c16")}</div></div>"""

BLOCKS = {k[2:]: v for k, v in globals().items() if k.startswith('b_')}

def build(slug):
    global SLUG; SLUG = slug
    spec = importlib.util.spec_from_file_location(slug, os.path.join(ROOT,'_build','casos',slug+'.py')); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); C = m.CASO
    secs = ''
    for s in C["secciones"]:
        inner = title(s["num"], s["titulo"]) + ''.join(BLOCKS[b["tipo"]](b) for b in s["bloques"])
        secs += f'<section id="{s["id"]}" class="c-sec{" c-sec--white" if s.get("blanca") else ""}"><div class="cw">{inner}</div></section>\n'
        if s.get("finales"):
            f = s["finales"]; crit = ''.join(f'<div class="crit">{t(h,"p","t-sub3b")}{t(d,"p","t-c16")}</div>' for h,d in f["crit"])
            if f.get("horneado"):
                crit3 = ''.join(f'<li>{t(h,"span")}: {t(d,"span")}</li>' for h,d in f["crit"])
                secs += f'<div class="finales-ancho">{img(f["img"],f["alt"],"reveal")}<div class="sr-only">{t(("Accesibilidad","Accessibility"),"p")}<ul>{crit3}</ul></div></div>\n'
                continue
            if f.get("ancho"):
                crit3 = ''.join(f'<div class="crit">{t(h,"p","t-sub3b")}{t(d,"p","t-c16 c-gris")}</div>' for h,d in f["crit"])
                secs += f'<div class="finales-ancho">{img(f["img"],f["alt"],"reveal")}<div class="cw">{t(("Accesibilidad","Accessibility"),"p","t-et-m")}<div class="g3" data-stagger=".1">{crit3}</div></div></div>\n'
                continue
            secs += f'<div class="finales"><div class="cw">{img(f["img"],f["alt"],"reveal")}<div class="c-stack" style="gap:16px" data-stagger=".1">{t(("Accesibilidad","Accessibility"),"p","t-et-m")}{crit}</div></div></div>\n'
    h = C["hero"]
    ficha = ''.join(f'<div>{t(k,"p","t-et-m c-gris")}{t(v,"p","t-c16b")}</div>' for k,v in h["ficha"])
    idx = ''.join(f'<a class="tag" href="#{s["id"]}">{es(s["indice"])}</a>' if not isinstance(s["indice"],tuple) else t(s["indice"],"a","tag",f' href="#{s["id"]}"') for s in C["secciones"])
    nx = C["siguiente"]
    page = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{es(C["meta_title"])}</title>
<meta name="description" content="{html.escape(es(h["lead"]))}">
<link rel="canonical" href="https://alejoogmz.github.io/casos/{slug}.html">
<meta property="og:type" content="article"><meta property="og:site_name" content="Alejandro Gómez · UX/UI"><meta property="og:locale" content="es_CO"><meta property="og:locale:alternate" content="en_US">
<meta property="og:url" content="https://alejoogmz.github.io/casos/{slug}.html"><meta property="og:title" content="{es(C["meta_title"])}"><meta property="og:description" content="{html.escape(es(h["lead"]))}">
<meta property="og:image" content="https://alejoogmz.github.io/assets/img/og-{slug}.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{html.escape(es(h["cover_alt"]))}">
<meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#0E1F26">
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Raleway:wght@400;500;600;700;800&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../css/tokens.css"><link rel="stylesheet" href="../css/main.css"><link rel="stylesheet" href="../css/caso.css">
</head>
<body data-page="caso-{slug}" data-root="../">
<main id="main">
<header class="c-hero"><div class="cw">
{t(h["kicker"],"p","t-et-m c-gris reveal")}
<h1 class="split">{h["titulo"]}</h1>
{t(h["lead"],"p","t-sub1 lead reveal",' style="--d:.4s"')}
{t(h["nota"],"p","t-c14 c-gris reveal",' style="--d:.5s"')}
<div class="ficha" data-stagger=".08">{ficha}</div>
</div></header>
<div class="c-cover"><div class="c-cover__band"></div><div class="c-cover__img reveal">{img(h["cover"],h["cover_alt"],"",' fetchpriority="high"').replace(' loading="lazy"','')}</div>
<div class="indice reveal">{t(("En este caso","In this case"),"p","c-label c-label--l")}<nav aria-label="Secciones del caso">{idx}</nav></div></div>
{secs}
<div class="next"><a href="{nx["href"]}"><div class="img">{img(nx["img"],nx["alt"])}</div>
<div class="next__txt"><div class="c-stack" style="gap:8px">{t(("Siguiente caso","Next case"),"p","t-et-m")}<h2 class="t-h2">{nx["titulo"]}</h2>{t(nx["txt"],"p","t-c18")}</div><span class="icon-btn icon-btn--dark" style="align-self:flex-end">{ARR}</span></div></a></div>
</main>
<script>
// índice: resalta la sección visible
(() => {{ const links=[...document.querySelectorAll('.indice a')]; const io=new IntersectionObserver(es=>es.forEach(e=>{{ if(e.isIntersecting) links.forEach(l=>l.classList.toggle('is-active',l.getAttribute('href')==='#'+e.target.id)); }}),{{rootMargin:'-40% 0px -55% 0px'}});
document.querySelectorAll('main section[id]').forEach(s=>io.observe(s)); }})();
</script>
<script src="../js/i18n-en.js"></script>
<script src="../js/en/{slug}.js"></script>
<script src="../js/main.js"></script>
</body>
</html>'''
    open(os.path.join(ROOT,'casos',slug+'.html'),'w').write(page)
    EN['meta.title.caso-'+slug] = C["meta_title"][1]
    open(os.path.join(ROOT,'js','en',slug+'.js'),'w').write('/* Textos en inglés del caso (generado). */\nObject.assign(window.I18N_EN = window.I18N_EN || {}, '+json.dumps(EN, ensure_ascii=False, indent=1)+');\n')
    print(slug, 'ok ·', CNT[0], 'textos traducibles')

if __name__ == '__main__': build(sys.argv[1])
