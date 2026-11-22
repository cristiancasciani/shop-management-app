"""Dashboard, products, stock movements and exports."""
import csv
import io
import math
from datetime import date, datetime, timedelta

from flask import (Blueprint, Response, abort, flash, g, redirect, render_template, request, send_file, url_for)

from .auth import login_required
from .db import get_db, init_db, now
from .i18n import category_name, t
from .seed_data import CATEGORIES

bp = Blueprint('views', __name__)

PAGE_SIZE = 15
SORTS = {
    'name': 'name COLLATE NOCASE', 'sku': 'sku', 'brand': 'brand COLLATE NOCASE', 'qty': 'quantity',
    'price': 'price', 'value': 'quantity * cost', 'updated': 'updated_at',
}
REASONS = {'in': ['purchase', 'return', 'other'], 'out': ['sale', 'damaged', 'other'], 'adjust': ['count', 'other']}


# ---------------------------------------------------------------- dashboard
@bp.get('/')
@login_required
def dashboard():
    db = get_db()
    k = db.execute(
        'SELECT COUNT(*) AS products, COALESCE(SUM(quantity), 0) AS units,'
        ' COALESCE(SUM(quantity * cost), 0) AS value_cost, COALESCE(SUM(quantity * price), 0) AS value_retail,'
        ' SUM(quantity > 0 AND quantity <= min_stock) AS low, SUM(quantity = 0) AS out FROM products').fetchone()

    by_cat = db.execute('SELECT category, SUM(quantity * cost) AS value FROM products GROUP BY category ORDER BY value DESC').fetchall()
    categories = [{'key': r['category'], 'label': category_name(r['category']), 'value': round(r['value'], 2)} for r in by_cat]

    start = date.today() - timedelta(days=29)
    rows = db.execute(
        "SELECT substr(created_at, 1, 10) AS day, SUM(CASE WHEN qty > 0 THEN qty ELSE 0 END) AS inn,"
        " SUM(CASE WHEN qty < 0 THEN -qty ELSE 0 END) AS out FROM movements"
        " WHERE created_at >= ? AND reason != 'initial' GROUP BY day", (start.isoformat(),)).fetchall()
    per_day = {r['day']: r for r in rows}
    flow = []
    for i in range(30):
        d = (start + timedelta(days=i)).isoformat()
        r = per_day.get(d)
        flow.append({'day': d, 'in': r['inn'] if r else 0, 'out': r['out'] if r else 0})

    alerts = db.execute(
        'SELECT * FROM products WHERE quantity <= min_stock ORDER BY quantity = 0 DESC, quantity * 1.0 / MAX(min_stock, 1) LIMIT 8').fetchall()
    recent = db.execute(
        'SELECT m.*, p.name, p.sku FROM movements m JOIN products p ON p.id = m.product_id'
        " WHERE m.reason != 'initial' ORDER BY m.created_at DESC, m.id DESC LIMIT 8").fetchall()
    return render_template('dashboard.html', k=k, categories=categories, flow=flow, alerts=alerts, recent=recent)


# ----------------------------------------------------------------- products
def product_query(args):
    """Build the WHERE clause shared by the list and the exports."""
    where, params = [], []
    q = args.get('q', '').strip()
    if q:
        where.append('(name LIKE ? OR sku LIKE ? OR brand LIKE ?)')
        params += [f'%{q}%'] * 3
    if args.get('category') in CATEGORIES:
        where.append('category = ?')
        params.append(args['category'])
    if args.get('brand'):
        where.append('brand = ?')
        params.append(args['brand'])
    stock = args.get('stock')
    if stock == 'low':
        where.append('quantity > 0 AND quantity <= min_stock')
    elif stock == 'out':
        where.append('quantity = 0')
    elif stock == 'ok':
        where.append('quantity > min_stock')
    sort = args.get('sort') if args.get('sort') in SORTS else 'name'
    direction = 'DESC' if args.get('dir') == 'desc' else 'ASC'
    clause = (' WHERE ' + ' AND '.join(where)) if where else ''
    return clause, params, f' ORDER BY {SORTS[sort]} {direction}, id', sort, direction.lower()


@bp.get('/products')
@login_required
def products():
    db = get_db()
    clause, params, order, sort, direction = product_query(request.args)
    total = db.execute(f'SELECT COUNT(*) FROM products{clause}', params).fetchone()[0]
    pages = max(1, math.ceil(total / PAGE_SIZE))
    page = min(max(request.args.get('page', 1, type=int), 1), pages)
    rows = db.execute(f'SELECT * FROM products{clause}{order} LIMIT ? OFFSET ?', [*params, PAGE_SIZE, (page - 1) * PAGE_SIZE]).fetchall()
    brands = [r[0] for r in db.execute('SELECT DISTINCT brand FROM products ORDER BY brand COLLATE NOCASE')]
    ctx = dict(rows=rows, total=total, page=page, pages=pages, sort=sort, direction=direction,
               args=request.args, categories=CATEGORIES, brands=brands)
    # JS asks for just the results block when filters change.
    if request.args.get('partial'):
        return render_template('_products_results.html', **ctx)
    return render_template('products.html', **ctx)


def parse_product(form, product_id=None):
    data, errors = {}, {}
    for f in ('sku', 'name', 'brand', 'category'):
        data[f] = form.get(f, '').strip()
        if not data[f]:
            errors[f] = t('err.required')
    data['sku'] = data['sku'].upper()
    if data['category'] and data['category'] not in CATEGORIES:
        errors['category'] = t('err.required')
    for f in ('cost', 'price'):
        try:
            data[f] = round(float(form.get(f, '').replace(',', '.')), 2)
            if data[f] < 0 or not math.isfinite(data[f]):
                raise ValueError
        except ValueError:
            errors[f] = t('err.number')
    fields = ('min_stock',) if product_id else ('quantity', 'min_stock')
    for f in fields:
        try:
            data[f] = int(form.get(f, ''))
            if data[f] < 0:
                raise ValueError
        except ValueError:
            errors[f] = t('err.integer')
    if 'cost' in data and 'price' in data and 'cost' not in errors and 'price' not in errors and data['price'] < data['cost']:
        errors['price'] = t('err.price_below_cost')
    if data['sku'] and 'sku' not in errors:
        clash = get_db().execute('SELECT id FROM products WHERE sku = ? AND id != ?', (data['sku'], product_id or 0)).fetchone()
        if clash:
            errors['sku'] = t('err.sku_taken')
    return data, errors


def get_product(pid):
    p = get_db().execute('SELECT * FROM products WHERE id = ?', (pid,)).fetchone()
    if p is None:
        abort(404)
    return p


@bp.route('/products/new', methods=['GET', 'POST'])
@login_required
def product_new():
    data, errors = {'quantity': 0, 'min_stock': 3}, {}
    if request.method == 'POST':
        data, errors = parse_product(request.form)
        if not errors:
            db, stamp = get_db(), now()
            cur = db.execute(
                'INSERT INTO products (sku, name, brand, category, cost, price, quantity, min_stock, created_at, updated_at)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (data['sku'], data['name'], data['brand'], data['category'], data['cost'], data['price'],
                 data['quantity'], data['min_stock'], stamp, stamp))
            if data['quantity']:
                db.execute("INSERT INTO movements (product_id, kind, qty, reason, user_id, created_at) VALUES (?, 'in', ?, 'initial', ?, ?)",
                           (cur.lastrowid, data['quantity'], g.user['id'], stamp))
            db.commit()
            flash(t('flash.created', name=data['name']), 'ok')
            return redirect(url_for('views.product_detail', pid=cur.lastrowid))
    return render_template('product_form.html', data=data, errors=errors, product=None, categories=CATEGORIES)


@bp.route('/products/<int:pid>/edit', methods=['GET', 'POST'])
@login_required
def product_edit(pid):
    product = get_product(pid)
    data, errors = dict(product), {}
    if request.method == 'POST':
        data, errors = parse_product(request.form, product_id=pid)
        if not errors:
            db = get_db()
            db.execute('UPDATE products SET sku=?, name=?, brand=?, category=?, cost=?, price=?, min_stock=?, updated_at=? WHERE id=?',
                       (data['sku'], data['name'], data['brand'], data['category'], data['cost'], data['price'],
                        data['min_stock'], now(), pid))
            db.commit()
            flash(t('flash.updated', name=data['name']), 'ok')
            return redirect(url_for('views.product_detail', pid=pid))
        data['quantity'] = product['quantity']
    return render_template('product_form.html', data=data, errors=errors, product=product, categories=CATEGORIES)


@bp.get('/products/<int:pid>')
@login_required
def product_detail(pid):
    product = get_product(pid)
    moves = get_db().execute(
        'SELECT m.*, u.name AS user FROM movements m LEFT JOIN users u ON u.id = m.user_id'
        ' WHERE product_id = ? ORDER BY created_at DESC, m.id DESC LIMIT 100', (pid,)).fetchall()
    return render_template('product_detail.html', p=product, moves=moves, reasons=REASONS, errors={}, form={})


@bp.post('/products/<int:pid>/delete')
@login_required
def product_delete(pid):
    product = get_product(pid)
    db = get_db()
    db.execute('DELETE FROM products WHERE id = ?', (pid,))
    db.commit()
    flash(t('flash.deleted', name=product['name']), 'ok')
    return redirect(url_for('views.products'))


@bp.post('/products/<int:pid>/move')
@login_required
def product_move(pid):
    product = get_product(pid)
    kind = request.form.get('kind')
    reason = request.form.get('reason')
    note = request.form.get('note', '').strip()[:200]
    errors = {}
    if kind not in REASONS:
        abort(400)
    if reason not in REASONS[kind]:
        reason = REASONS[kind][0]
    try:
        qty = int(request.form.get('qty', ''))
    except ValueError:
        qty = None
        errors['qty'] = t('err.integer')
    if qty is not None:
        if kind in ('in', 'out') and qty <= 0:
            errors['qty'] = t('err.integer') if qty < 0 else t('err.qty_zero')
        elif kind == 'adjust' and qty == 0:
            errors['qty'] = t('err.qty_zero')
    if not errors:
        delta = -qty if kind == 'out' else qty
        if product['quantity'] + delta < 0:
            errors['qty'] = t('err.qty_negative')
    if errors:
        moves = get_db().execute(
            'SELECT m.*, u.name AS user FROM movements m LEFT JOIN users u ON u.id = m.user_id'
            ' WHERE product_id = ? ORDER BY created_at DESC, m.id DESC LIMIT 100', (pid,)).fetchall()
        return render_template('product_detail.html', p=product, moves=moves, reasons=REASONS,
                               errors=errors, form=request.form), 422
    db, stamp = get_db(), now()
    db.execute('INSERT INTO movements (product_id, kind, qty, reason, note, user_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
               (pid, kind, delta, reason, note, g.user['id'], stamp))
    db.execute('UPDATE products SET quantity = quantity + ?, updated_at = ? WHERE id = ?', (delta, stamp, pid))
    db.commit()
    flash(t('flash.moved', qty=f'{delta:+d}', stock=product['quantity'] + delta), 'ok')
    return redirect(url_for('views.product_detail', pid=pid))


# ---------------------------------------------------------------- movements
@bp.get('/movements')
@login_required
def movements():
    db = get_db()
    where, params = ["m.reason != 'initial'"], []
    kind = request.args.get('kind')
    if kind in REASONS:
        where.append('m.kind = ?')
        params.append(kind)
    for arg, op in (('from', '>='), ('to', '<')):
        val = request.args.get(arg, '')
        try:
            d = date.fromisoformat(val)
        except ValueError:
            continue
        where.append(f'm.created_at {op} ?')
        params.append((d + timedelta(days=1 if arg == 'to' else 0)).isoformat())
    q = request.args.get('q', '').strip()
    if q:
        where.append('(p.name LIKE ? OR p.sku LIKE ?)')
        params += [f'%{q}%'] * 2
    clause = ' WHERE ' + ' AND '.join(where)
    base = f' FROM movements m JOIN products p ON p.id = m.product_id LEFT JOIN users u ON u.id = m.user_id{clause}'
    s = db.execute('SELECT COUNT(*) AS n, COALESCE(SUM(CASE WHEN m.qty > 0 THEN m.qty END), 0) AS inn,'
                   ' COALESCE(-SUM(CASE WHEN m.qty < 0 THEN m.qty END), 0) AS out' + base, params).fetchone()
    pages = max(1, math.ceil(s['n'] / 25))
    page = min(max(request.args.get('page', 1, type=int), 1), pages)
    rows = db.execute('SELECT m.*, p.name, p.sku, u.name AS user' + base + ' ORDER BY m.created_at DESC, m.id DESC LIMIT 25 OFFSET ?',
                      [*params, (page - 1) * 25]).fetchall()
    return render_template('movements.html', rows=rows, s=s, page=page, pages=pages, args=request.args)


# ------------------------------------------------------------------ exports
EXPORT_COLS = ['sku', 'name', 'brand', 'category', 'cost', 'price', 'quantity', 'min_stock', 'value', 'status', 'updated_at']


def export_rows():
    clause, params, order, *_ = product_query(request.args)
    for p in get_db().execute(f'SELECT * FROM products{clause}{order}', params):
        status = 'out' if p['quantity'] == 0 else 'low' if p['quantity'] <= p['min_stock'] else 'ok'
        yield [p['sku'], p['name'], p['brand'], category_name(p['category']), p['cost'], p['price'], p['quantity'],
               p['min_stock'], round(p['quantity'] * p['cost'], 2), t(f'status.{status}'), p['updated_at'].replace('T', ' ')]


def export_headers():
    keys = ['col.sku', 'col.name', 'col.brand', 'col.category', 'col.cost', 'col.price', 'col.qty', 'col.min', 'col.value',
            'col.status', 'col.updated']
    return [t(k) for k in keys]


def export_name(ext):
    return f"circuito-inventory-{datetime.now():%Y-%m-%d}.{ext}"


@bp.get('/export/products.csv')
@login_required
def export_csv():
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=';')  # ';' opens correctly in Italian Excel
    w.writerow(export_headers())
    w.writerows(export_rows())
    return Response('﻿' + buf.getvalue(), mimetype='text/csv; charset=utf-8',
                    headers={'Content-Disposition': f'attachment; filename="{export_name("csv")}"'})


@bp.get('/export/products.xlsx')
@login_required
def export_xlsx():
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = 'Inventory'
    ws.append(export_headers())
    for row in export_rows():
        ws.append(row)
    head = PatternFill('solid', fgColor='1F2937')
    for c in ws[1]:
        c.font, c.fill, c.alignment = Font(bold=True, color='FFFFFF'), head, Alignment(vertical='center')
    for col in ('E', 'F', 'I'):
        for c in ws[col][1:]:
            c.number_format = '#,##0.00 [$€-x-euro2]'
    widths = [11, 30, 12, 14, 11, 11, 8, 11, 13, 14, 18]
    for i, wdt in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = wdt
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=export_name('xlsx'),
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# --------------------------------------------------------------- demo reset
@bp.post('/reset-demo')
@login_required
def reset_demo():
    init_db()
    from flask import session
    lang, csrf = session.get('lang'), session.get('_csrf')
    session.clear()
    session.update(user_id=1, _csrf=csrf)
    if lang:
        session['lang'] = lang
    flash(t('flash.reset'), 'ok')
    return redirect(url_for('views.dashboard'))
