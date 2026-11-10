(() => {
  const root = document.body.dataset.root || '';
  const page = document.body.dataset.page || '';
  const ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>';
  window.ARROW = ARROW;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Nav y footer compartidos ---------- */
  const nav = document.createElement('header');
  nav.className = 'nav';
  nav.innerHTML = `
  <a class="skip" href="#main" data-i18n="skip">Saltar al contenido</a>
  <div class="wrap nav__in">
    <a class="logo" href="${root}index.html" aria-label="Alejandro Gómez, inicio">ALEJANDRO <b>GÓMEZ</b></a>
    <button class="menu-btn" aria-expanded="false" aria-controls="nav-links" aria-label="Abrir menú" data-i18n-attr="aria-label:menu"><span></span><span></span></button>
    <nav class="nav__links" id="nav-links" aria-label="Principal">
      <a class="nav__link" href="${root}proyectos.html" ${page==='proyectos'?'aria-current="page"':''} data-i18n="nav.proyectos">Proyectos</a>
      <a class="nav__link" href="${root}experiencia.html" ${page==='experiencia'?'aria-current="page"':''} data-i18n="nav.experiencia">Experiencia</a>
      <div class="lang" role="group" aria-label="Idioma">
        <button type="button" data-lang="es" aria-pressed="true">ES</button>
        <button type="button" data-lang="en" aria-pressed="false">EN</button>
      </div>
      <a class="btn btn--solid" href="${root}sobre-mi.html" ${page==='sobre'?'aria-current="page"':''}><span data-i18n="nav.sobre">Sobre mí</span>${ARROW}</a>
    </nav>
  </div>`;
  document.body.prepend(nav);

  const footer = document.createElement('footer');
  footer.className = 'footer';
  footer.innerHTML = `
  <div class="wrap footer__in">
    <div class="footer__brand">
      <span class="logo">ALEJANDRO <b>GÓMEZ</b></span>
      <div class="footer__links">
        <a href="https://www.linkedin.com/in/UnAlejoGomez" target="_blank" rel="noopener">LinkedIn</a>
        <a href="https://github.com/AlejooGMZ" target="_blank" rel="noopener">GitHub</a>
        <a href="mailto:alejogoto@gmail.com" data-i18n="footer.correo">Correo</a>
      </div>
      <p class="footer__copy"><span data-i18n="footer.copy">Diseñado y construido por Alejandro Gómez</span> © ${new Date().getFullYear()}</p>
    </div>
  </div>
  <img class="footer__mark" src="${root}assets/img/p1-agmzrecurso-18-1.webp" alt="" loading="lazy" onerror="this.remove()">`;
  document.body.append(footer);

  const cover = document.createElement('div');
  cover.className = 'page-cover'; cover.innerHTML = '<i></i><i></i>';
  document.body.append(cover);

  /* ---------- Menú móvil ---------- */
  const mb = nav.querySelector('.menu-btn');
  mb.addEventListener('click', () => {
    const open = document.documentElement.classList.toggle('menu-open');
    mb.setAttribute('aria-expanded', open);
    document.body.style.overflow = open ? 'hidden' : '';
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && document.documentElement.classList.contains('menu-open')) { mb.click(); mb.focus(); }
  });

  /* ---------- Nav al hacer scroll ---------- */
  let lastY = 0;
  addEventListener('scroll', () => {
    const y = scrollY;
    nav.classList.toggle('is-scrolled', y > 40);
    nav.classList.toggle('is-hidden', y > 400 && y > lastY && !document.documentElement.classList.contains('menu-open'));
    lastY = y;
  }, { passive: true });

  /* ---------- Idioma ---------- */
  const store = { get(k){ try{return localStorage.getItem(k)}catch(e){return null} }, set(k,v){ try{localStorage.setItem(k,v)}catch(e){} } };
  function applyLang(lang){
    const dict = lang === 'en' ? (window.I18N_EN || {}) : null;
    document.documentElement.lang = lang;
    document.querySelectorAll('[data-i18n]').forEach(el => {
      if (el.dataset.es === undefined) el.dataset.es = el.innerHTML;
      const k = el.dataset.i18n;
      el.innerHTML = dict && dict[k] !== undefined ? dict[k] : el.dataset.es;
      if (el.classList.contains('split')) splitText(el, true);
    });
    document.querySelectorAll('[data-i18n-attr]').forEach(el => {
      el.dataset.i18nAttr.split(';').forEach(pair => {
        const [attr, k] = pair.split(':');
        const store = 'es' + attr.replace(/[^a-z]/gi,'');
        if (el.dataset[store] === undefined) el.dataset[store] = el.getAttribute(attr) || '';
        el.setAttribute(attr, dict && dict[k] !== undefined ? dict[k] : el.dataset[store]);
      });
    });
    document.querySelectorAll('[data-cv]').forEach(a => a.href = `${root}assets/cv/CV-Alejandro-Gomez-UXUI-${lang.toUpperCase()}.pdf`);
    document.querySelectorAll('.lang button').forEach(b => b.setAttribute('aria-pressed', b.dataset.lang === lang));
    if (dict && dict['meta.title.' + page]) document.title = dict['meta.title.' + page];
    else if (!dict && document.body.dataset.titleEs) document.title = document.body.dataset.titleEs;
    store.set('lang', lang);
  }
  document.body.dataset.titleEs = document.title;
  document.addEventListener('click', e => { const b = e.target.closest('.lang button'); if (b) applyLang(b.dataset.lang); });

  /* ---------- Texto que aparece letra por letra ---------- */
  function splitText(el, keepIn){
    const txt = el.innerHTML;
    const tmp = document.createElement('div'); tmp.innerHTML = txt;
    let i = 0;
    const walk = node => [...node.childNodes].map(n => {
      if (n.nodeType === 3) return n.textContent.split(/(\s+)/).map(w => /^\s+$/.test(w) ? (w.includes('\n') ? '<br>' : ' ') : w ? `<span class="w">${[...w].map(c => `<span class="ch" style="transition-delay:${(i++)*0.035}s">${c}</span>`).join('')}</span>` : '').join('');
      if (n.nodeName === 'BR') return '<br>';
      return `<${n.nodeName.toLowerCase()}${n.className?` class="${n.className}"`:''}>${walk(n)}</${n.nodeName.toLowerCase()}>`;
    }).join('');
    el.innerHTML = walk(tmp);
    el.setAttribute('aria-label', tmp.textContent.replace(/\s+/g,' ').trim());
    if (keepIn) requestAnimationFrame(() => el.classList.add('is-in'));
  }
  document.querySelectorAll('.split').forEach(el => { el.dataset.es = el.innerHTML; splitText(el); });

  const initial = store.get('lang') || 'es';
  applyLang(initial === 'en' ? 'en' : 'es');

  /* ---------- Revelado al hacer scroll ---------- */
  document.querySelectorAll('[data-stagger]').forEach(g => {
    [...g.children].forEach((c, i) => { c.classList.add('reveal'); c.style.setProperty('--d', (i * (+g.dataset.stagger || .08)) + 's'); });
  });
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting){ e.target.classList.add('is-in'); io.unobserve(e.target); if (e.target.dataset.count) countUp(e.target); }
  }), { rootMargin: '0px 0px -10% 0px', threshold: .08 });
  document.querySelectorAll('.reveal,.reveal-x,.wipe,.split,.line-grow,[data-count]').forEach(el => io.observe(el));

  /* ---------- Contadores ---------- */
  function countUp(el){
    const raw = el.dataset.count; const m = raw.match(/^([^\d−-]*)([−-]?)(\d+)(.*)$/);
    if (!m || reduce){ el.textContent = raw; return; }
    const [, pre, sign, num, post] = m; const end = +num; const pad = num.length; const t0 = performance.now(); const dur = 1400;
    const tick = t => { const p = Math.min(1, (t - t0) / dur); const v = Math.round(end * (1 - Math.pow(1 - p, 3)));
      el.textContent = pre + sign + String(v).padStart(pad, '0') + post; if (p < 1) requestAnimationFrame(tick); };
    requestAnimationFrame(tick);
  }

  /* ---------- Videos: respetar movimiento reducido ---------- */
  if (reduce) document.querySelectorAll('video[autoplay]').forEach(v => { v.removeAttribute('autoplay'); v.pause(); v.controls = true; });

  /* ---------- Parallax ---------- */
  const px = [...document.querySelectorAll('[data-parallax]')];
  if (px.length && !reduce){
    const run = () => { const h = innerHeight; px.forEach(el => { const r = el.getBoundingClientRect(); if (r.bottom < 0 || r.top > h) return;
      const k = +el.dataset.parallax || .1; el.style.transform = `translate3d(0,${((r.top + r.height/2) - h/2) * -k}px,0)`; }); };
    addEventListener('scroll', () => requestAnimationFrame(run), { passive: true }); run();
  }

  /* ---------- Cursor ---------- */
  if (!reduce && matchMedia('(hover:hover) and (pointer:fine)').matches){
    const c = document.createElement('div'); c.className = 'cursor'; document.body.append(c);
    let x = 0, y = 0, cx = 0, cy = 0;
    addEventListener('mousemove', e => { x = e.clientX; y = e.clientY; c.classList.add('is-on'); });
    document.addEventListener('mouseover', e => c.classList.toggle('is-link', !!e.target.closest('a,button')));
    (function loop(){ cx += (x - cx) * .2; cy += (y - cy) * .2; c.style.transform = `translate(${cx}px,${cy}px) translate(-50%,-50%)`; requestAnimationFrame(loop); })();
  }

  /* ---------- Transición entre páginas ---------- */
  if (!reduce){
    if (sessionStorage.getItem('pt')){ cover.classList.add('is-entering'); requestAnimationFrame(() => requestAnimationFrame(() => cover.classList.add('go'))); sessionStorage.removeItem('pt'); setTimeout(()=>cover.className='page-cover',800); }
    document.addEventListener('click', e => {
      const a = e.target.closest('a'); if (!a || a.target || e.metaKey || e.ctrlKey || e.shiftKey) return;
      const url = new URL(a.href, location.href);
      if (url.origin !== location.origin || url.pathname === location.pathname || /\.(pdf|webp|png)$/i.test(url.pathname)) return;
      e.preventDefault(); try{sessionStorage.setItem('pt','1')}catch(_){}
      cover.classList.add('is-leaving'); setTimeout(() => location.href = a.href, 520);
    });
    addEventListener('pageshow', e => { if (e.persisted) cover.className = 'page-cover'; });
  }
})();
