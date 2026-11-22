// Circuito dashboard charts: hand-made SVG, no library.
//  - Flow: two lines (units in / out per day) with crosshair + tooltip and direct end labels.
//  - Categories: horizontal bars (stock value), value labels, per-bar tooltip.
(() => {
  const D = window.DASH;
  if (!D) return;
  const NS = 'http://www.w3.org/2000/svg';
  const locale = D.lang === 'it' ? 'it-IT' : 'en-GB';
  const fmtInt = new Intl.NumberFormat(locale);
  const fmtEur = new Intl.NumberFormat(locale, { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 });
  const fmtEurShort = new Intl.NumberFormat(locale, { style: 'currency', currency: 'EUR', notation: 'compact', maximumFractionDigits: 1 });
  const fmtDay = new Intl.DateTimeFormat(locale, { day: 'numeric', month: 'short' });
  const fmtDayLong = new Intl.DateTimeFormat(locale, { weekday: 'short', day: 'numeric', month: 'long' });

  const el = (tag, attrs = {}, parent) => {
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    if (parent) parent.appendChild(n);
    return n;
  };
  const niceMax = (v) => {
    if (v <= 0) return 1;
    const p = 10 ** Math.floor(Math.log10(v));
    const n = v / p;
    return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10) * p;
  };

  function tooltip(host) {
    const tip = document.createElement('div');
    tip.className = 'viz-tip';
    tip.hidden = true;
    host.appendChild(tip);
    return {
      show(html, x, y) {
        tip.innerHTML = html;
        tip.hidden = false;
        const w = tip.offsetWidth, hostW = host.clientWidth;
        tip.style.left = Math.min(Math.max(x - w / 2, 0), hostW - w) + 'px';
        tip.style.top = Math.max(y - tip.offsetHeight - 12, 0) + 'px';
      },
      hide() { tip.hidden = true; },
    };
  }

  /* ---------------- Flow: line chart ---------------- */
  function drawFlow(host) {
    host.querySelectorAll('svg').forEach((s) => s.remove());
    const data = D.flow.map((d) => ({ ...d, date: new Date(d.day + 'T12:00') }));
    const W = host.clientWidth, H = 260;
    const m = { t: 14, r: 46, b: 28, l: 34 };
    const iw = W - m.l - m.r, ih = H - m.t - m.b;
    const max = niceMax(Math.max(...data.map((d) => Math.max(d.in, d.out))));
    const x = (i) => m.l + (i / (data.length - 1)) * iw;
    const y = (v) => m.t + ih - (v / max) * ih;

    const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H, class: 'viz' });
    // Grid + y labels (recessive).
    for (let i = 0; i <= 4; i++) {
      const v = (max / 4) * i, yy = y(v);
      el('line', { x1: m.l, x2: m.l + iw, y1: yy, y2: yy, class: i ? 'grid' : 'axis' }, svg);
      el('text', { x: m.l - 8, y: yy + 4, 'text-anchor': 'end', class: 'tick' }, svg).textContent = fmtInt.format(v);
    }
    // X labels: every 7th day.
    data.forEach((d, i) => {
      if ((i % 7 === 0 && data.length - 1 - i > 3) || i === data.length - 1) {
        el('text', { x: x(i), y: H - 8, 'text-anchor': i === data.length - 1 ? 'end' : 'middle', class: 'tick' }, svg).textContent = fmtDay.format(d.date);
      }
    });
    // Lines.
    const series = [
      { key: 'in', cls: 's1', label: D.labels.in },
      { key: 'out', cls: 's2', label: D.labels.out },
    ];
    for (const s of series) {
      const dpath = data.map((d, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(d[s.key]).toFixed(1)}`).join('');
      el('path', { d: dpath, class: `line ${s.cls}` }, svg);
    }
    // Direct end labels, nudged apart if they collide.
    const last = data[data.length - 1];
    let ly = series.map((s) => y(last[s.key]));
    if (Math.abs(ly[0] - ly[1]) < 14) {
      const mid = (ly[0] + ly[1]) / 2, up = ly[0] <= ly[1] ? 0 : 1;
      ly[up] = mid - 7; ly[1 - up] = mid + 7;
    }
    series.forEach((s, i) => {
      el('text', { x: m.l + iw + 6, y: ly[i] + 4, class: 'end-label' }, svg).textContent = s.label;
    });

    // Crosshair + markers + tooltip.
    const cross = el('line', { y1: m.t, y2: m.t + ih, class: 'cross', visibility: 'hidden' }, svg);
    const dots = series.map((s) => el('circle', { r: 4.5, class: `dot ${s.cls}`, visibility: 'hidden' }, svg));
    const hit = el('rect', { x: m.l, y: m.t, width: iw, height: ih, fill: 'transparent' }, svg);
    host.appendChild(svg);
    const tip = tooltip(host);

    const show = (i) => {
      const d = data[i], xx = x(i);
      cross.setAttribute('x1', xx); cross.setAttribute('x2', xx); cross.setAttribute('visibility', 'visible');
      series.forEach((s, k) => { dots[k].setAttribute('cx', xx); dots[k].setAttribute('cy', y(d[s.key])); dots[k].setAttribute('visibility', 'visible'); });
      tip.show(`<strong>${fmtDayLong.format(d.date)}</strong>` +
        series.map((s) => `<span><i class="sw sw-${s.cls.slice(1)}"></i>${s.label}<b>${fmtInt.format(d[s.key])}</b></span>`).join(''),
        xx, Math.min(y(d.in), y(d.out)));
    };
    const hide = () => { cross.setAttribute('visibility', 'hidden'); dots.forEach((d) => d.setAttribute('visibility', 'hidden')); tip.hide(); };
    const indexAt = (clientX) => {
      const r = svg.getBoundingClientRect();
      return Math.max(0, Math.min(data.length - 1, Math.round(((clientX - r.left - m.l) / iw) * (data.length - 1))));
    };
    hit.addEventListener('pointermove', (e) => show(indexAt(e.clientX)));
    hit.addEventListener('pointerleave', hide);
    // Keyboard: focus the chart, arrows move the crosshair.
    host.tabIndex = 0;
    let ki = data.length - 1;
    host.onkeydown = (e) => {
      if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
      e.preventDefault();
      ki = Math.max(0, Math.min(data.length - 1, ki + (e.key === 'ArrowRight' ? 1 : -1)));
      show(ki);
    };
    host.onblur = hide;
  }

  /* ---------------- Categories: horizontal bars ---------------- */
  function drawCategories(host) {
    host.querySelectorAll('svg').forEach((s) => s.remove());
    const data = D.categories;
    const W = host.clientWidth;
    const bar = 18, gap = 12;
    const labelW = Math.min(120, W * 0.32);
    const m = { t: 4, r: 70, b: 4, l: labelW };
    const H = m.t + m.b + data.length * (bar + gap) - gap;
    const iw = W - m.l - m.r;
    const max = Math.max(...data.map((d) => d.value)) || 1;
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H, class: 'viz' });
    el('line', { x1: m.l, x2: m.l, y1: 0, y2: H, class: 'axis' }, svg);
    const tip = tooltip(host);
    const total = data.reduce((a, d) => a + d.value, 0);

    data.forEach((d, i) => {
      const yy = m.t + i * (bar + gap);
      const w = Math.max(2, (d.value / max) * iw);
      const r = Math.min(4, w / 2);
      // Square at the baseline, 4px rounded at the data end.
      const x0 = m.l + 1, x1 = x0 + w;
      const path = `M${x0},${yy}H${x1 - r}Q${x1},${yy} ${x1},${yy + r}V${yy + bar - r}Q${x1},${yy + bar} ${x1 - r},${yy + bar}H${x0}Z`;
      const g = el('g', { class: 'bar-g' }, svg);
      el('rect', { x: 0, y: yy - gap / 2, width: W, height: bar + gap, fill: 'transparent' }, g); // big hit target
      el('path', { d: path, class: 'bar s1' }, g);
      el('text', { x: m.l - 10, y: yy + bar / 2 + 4, 'text-anchor': 'end', class: 'cat-label' }, g).textContent = d.label;
      el('text', { x: x1 + 8, y: yy + bar / 2 + 4, class: 'val-label' }, g).textContent = fmtEurShort.format(d.value);
      g.addEventListener('pointerenter', () => {
        g.classList.add('on');
        tip.show(`<strong>${d.label}</strong><span>${fmtEur.format(d.value)}<b>${Math.round((d.value / total) * 100)}%</b></span>`, x1, yy);
      });
      g.addEventListener('pointerleave', () => { g.classList.remove('on'); tip.hide(); });
    });
    host.appendChild(svg);
  }

  const flowHost = document.getElementById('flow-chart');
  const catHost = document.getElementById('cat-chart');
  const draw = () => { drawFlow(flowHost); drawCategories(catHost); };
  draw();
  let raf;
  new ResizeObserver(() => { cancelAnimationFrame(raf); raf = requestAnimationFrame(draw); }).observe(flowHost);
})();
