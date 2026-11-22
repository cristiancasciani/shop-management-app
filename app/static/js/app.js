// Circuito: small progressive enhancements. Every page also works without JavaScript.
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];

  // Flash messages: close button + auto-hide.
  $$('.flash').forEach((f) => {
    const close = () => f.remove();
    $('button', f)?.addEventListener('click', close);
    setTimeout(() => f.classList.add('fade'), 4500);
    setTimeout(close, 5200);
  });

  // Confirm before destructive forms.
  $$('form[data-confirm]').forEach((f) => f.addEventListener('submit', (e) => { if (!confirm(f.dataset.confirm)) e.preventDefault(); }));

  // Mobile sidebar.
  const menuBtn = $('.menu-btn');
  menuBtn?.addEventListener('click', () => {
    const open = document.body.classList.toggle('side-open');
    menuBtn.setAttribute('aria-expanded', String(open));
  });
  document.addEventListener('click', (e) => {
    if (document.body.classList.contains('side-open') && !e.target.closest('.side, .menu-btn')) {
      document.body.classList.remove('side-open');
      menuBtn?.setAttribute('aria-expanded', 'false');
    }
  });

  // Dropdowns.
  $$('.dropdown').forEach((d) => {
    const b = $('button', d);
    b.addEventListener('click', (e) => { e.stopPropagation(); const o = d.classList.toggle('open'); b.setAttribute('aria-expanded', String(o)); });
    document.addEventListener('click', () => { d.classList.remove('open'); b.setAttribute('aria-expanded', 'false'); });
  });

  // Login: fill demo credentials.
  $('[data-fill-demo]')?.addEventListener('click', (e) => {
    const [u, p] = e.currentTarget.dataset.fillDemo.split('|');
    $('[name=username]').value = u;
    $('[name=password]').value = p;
    $('.login form button[type=submit]').focus();
  });

  // Clickable table rows.
  document.addEventListener('click', (e) => {
    const tr = e.target.closest('tr[data-href]');
    if (tr && !e.target.closest('a, button')) location.href = tr.dataset.href;
  });

  // Products: live filters, sort and paging without reloading the page.
  const filters = $('#filters');
  const results = $('#results');
  if (filters && results) {
    let timer, ctrl;
    const load = async (page = 1) => {
      const params = new URLSearchParams(new FormData(filters));
      for (const [k, v] of [...params]) if (!v) params.delete(k);
      if (page > 1) params.set('page', page);
      const qs = params.toString();
      history.replaceState(null, '', qs ? `?${qs}` : location.pathname);
      $('#export-xlsx').href = `${$('#export-xlsx').pathname}${qs ? '?' + qs : ''}`;
      $('#export-csv').href = `${$('#export-csv').pathname}${qs ? '?' + qs : ''}`;
      ctrl?.abort();
      ctrl = new AbortController();
      results.classList.add('loading');
      try {
        const res = await fetch(`${filters.action}?${qs}${qs ? '&' : ''}partial=1`, { signal: ctrl.signal });
        results.innerHTML = await res.text();
      } catch (err) {
        if (err.name !== 'AbortError') filters.submit();
      } finally {
        results.classList.remove('loading');
      }
    };
    filters.addEventListener('input', (e) => {
      clearTimeout(timer);
      timer = setTimeout(load, e.target.type === 'search' ? 250 : 0);
    });
    filters.addEventListener('submit', (e) => { e.preventDefault(); load(); });
    results.addEventListener('click', (e) => {
      const s = e.target.closest('[data-sort]');
      if (s) {
        filters.elements.sort.value = s.dataset.sort;
        filters.elements.dir.value = s.dataset.dir; // form.dir is the text-direction attribute
        load();
      }
      const p = e.target.closest('[data-page]');
      if (p && !p.disabled) load(+p.dataset.page);
      const c = e.target.closest('[data-clear]');
      if (c) {
        e.preventDefault();
        filters.reset();
        filters.elements.q.value = '';
        $$('select', filters).forEach((s) => (s.value = ''));
        filters.querySelector('[name=stock][value=""]').checked = true;
        load();
      }
    });
  }

  // Stock movement form: reasons follow the selected type.
  const move = $('#move-form');
  if (move) {
    const sync = () => {
      const kind = move.kind.value;
      let first = null;
      $$('option', move.reason).forEach((o) => {
        const ok = o.dataset.kind === kind;
        o.hidden = !ok;
        o.disabled = !ok;
        if (ok && !first) first = o;
      });
      if (move.reason.selectedOptions[0]?.disabled) move.reason.value = first.value;
      const help = $('[data-adjust-help]', move);
      if (help) help.hidden = kind !== 'adjust';
      move.qty.min = kind === 'adjust' ? '' : '1';
    };
    $$('[name=kind]', move).forEach((r) => r.addEventListener('change', sync));
    sync();
  }

  // Product form: live margin preview.
  const cost = $('[name=cost]'), price = $('[name=price]'), out = $('#margin');
  if (cost && price && out) {
    const num = (v) => parseFloat(String(v).replace(',', '.'));
    const lang = document.documentElement.lang;
    const fmt = new Intl.NumberFormat(lang === 'it' ? 'it-IT' : 'en-GB', { style: 'currency', currency: 'EUR' });
    const upd = () => {
      const c = num(cost.value), p = num(price.value);
      if (!(c >= 0 && p > 0)) return (out.hidden = true);
      out.hidden = false;
      const m = p - c;
      out.className = 'margin-preview ' + (m < 0 ? 'neg' : 'pos');
      out.textContent = `${lang === 'it' ? 'Margine' : 'Margin'}: ${fmt.format(m)} (${Math.round((m / p) * 100)}%)`;
    };
    cost.addEventListener('input', upd);
    price.addEventListener('input', upd);
    upd();
  }
})();
