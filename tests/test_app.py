import re

import pytest

from app import create_app
from app.db import get_db


@pytest.fixture()
def app(tmp_path):
    return create_app({'TESTING': True, 'DATABASE': str(tmp_path / 'test.db'), 'SECRET_KEY': 'test'})


@pytest.fixture()
def client(app):
    return app.test_client()


def csrf(client, path='/login'):
    html = client.get(path).get_data(as_text=True)
    return re.search(r'name="_csrf" value="([^"]+)"', html).group(1)


def login(client, password='demo123'):
    token = csrf(client)
    return client.post('/login', data={'username': 'demo', 'password': password, '_csrf': token})


def test_requires_login(client):
    r = client.get('/')
    assert r.status_code == 302 and '/login' in r.headers['Location']


def test_bad_password(client):
    r = login(client, 'nope')
    assert r.status_code == 200 and b'login' in r.data.lower()
    assert client.get('/').status_code == 302


def test_post_without_csrf_rejected(client):
    assert client.post('/login', data={'username': 'demo', 'password': 'demo123'}).status_code == 400


def test_seed_history_matches_stock(app):
    with app.app_context():
        db = get_db()
        rows = db.execute('SELECT p.quantity, COALESCE(SUM(m.qty), 0) AS s FROM products p'
                          ' LEFT JOIN movements m ON m.product_id = p.id GROUP BY p.id').fetchall()
        assert rows and all(r['quantity'] == r['s'] for r in rows)
        assert all(r['quantity'] >= 0 for r in rows)


def test_pages_render(client):
    login(client)
    for path in ['/', '/products', '/products?q=iphone', '/products?stock=low&sort=qty&dir=desc', '/products?partial=1',
                 '/movements', '/movements?kind=out', '/products/new', '/products/1', '/products/1/edit', '/lang/en']:
        r = client.get(path, follow_redirects=True)
        assert r.status_code == 200, path


def test_search_filters(client):
    login(client)
    html = client.get('/products?q=galaxy&partial=1').get_data(as_text=True)
    assert 'Galaxy S26' in html and 'iPhone' not in html


def test_create_product_and_validation(client):
    login(client)
    token = csrf(client, '/products/new')
    bad = client.post('/products/new', data={'_csrf': token, 'sku': 'SPH-001', 'name': '', 'brand': 'X', 'category': 'audio',
                                             'cost': '10', 'price': '5', 'quantity': '-1', 'min_stock': '1'})
    text = bad.get_data(as_text=True)
    assert bad.status_code == 200 and 'aria-invalid' in text
    ok = client.post('/products/new', data={'_csrf': token, 'sku': 'tst-1', 'name': 'Test cable', 'brand': 'Acme',
                                            'category': 'accessories', 'cost': '2,50', 'price': '9.90', 'quantity': '5',
                                            'min_stock': '2'})
    assert ok.status_code == 302
    detail = client.get(ok.headers['Location']).get_data(as_text=True)
    assert 'TST-1' in detail and 'Test cable' in detail


def test_stock_movement_rules(client, app):
    login(client)
    token = csrf(client, '/products/1')
    with app.app_context():
        before = get_db().execute('SELECT quantity FROM products WHERE id = 1').fetchone()[0]
    r = client.post('/products/1/move', data={'_csrf': token, 'kind': 'in', 'qty': '4', 'reason': 'purchase'})
    assert r.status_code == 302
    too_many = client.post('/products/1/move', data={'_csrf': token, 'kind': 'out', 'qty': str(before + 999), 'reason': 'sale'})
    assert too_many.status_code == 422
    r = client.post('/products/1/move', data={'_csrf': token, 'kind': 'adjust', 'qty': '-1', 'reason': 'count'})
    assert r.status_code == 302
    with app.app_context():
        assert get_db().execute('SELECT quantity FROM products WHERE id = 1').fetchone()[0] == before + 3


def test_exports(client):
    login(client)
    csv = client.get('/export/products.csv?category=audio')
    assert csv.status_code == 200 and 'WH-1000XM6' in csv.get_data(as_text=True) and 'iPhone' not in csv.get_data(as_text=True)
    xlsx = client.get('/export/products.xlsx')
    assert xlsx.status_code == 200 and xlsx.data[:2] == b'PK'


def test_delete_and_reset(client):
    login(client)
    token = csrf(client, '/products/2')
    assert client.post('/products/2/delete', data={'_csrf': token}).status_code == 302
    assert client.get('/products/2').status_code == 404
    assert client.post('/reset-demo', data={'_csrf': token}).status_code == 302
    assert client.get('/products/2').status_code == 200
