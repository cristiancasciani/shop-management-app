"""Circuito — shop management demo (Flask + SQLite)."""
import os
import secrets
from datetime import datetime
from pathlib import Path

from flask import Flask, abort, redirect, request, session, url_for

from . import db
from .i18n import LANGS, category_name, get_lang, t


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY') or secrets.token_hex(32),
        DATABASE=os.environ.get('DATABASE') or str(Path(app.instance_path) / 'shop.db'),
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_HTTPONLY=True,
    )
    if test_config:
        app.config.update(test_config)

    app.teardown_appcontext(db.close_db)
    db.ensure_db(app)

    # ---- Template helpers -------------------------------------------------
    def money(value: float) -> str:
        s = f'{value:,.2f}'
        if get_lang() == 'it':
            s = s.replace(',', ' ').replace('.', ',')
            return f'{s} €'
        return f'€{s}'

    def number(value: int) -> str:
        s = f'{value:,}'
        return s.replace(',', '.') if get_lang() == 'it' else s

    def datefmt(value: str, with_time: bool = True) -> str:
        d = datetime.fromisoformat(value)
        if get_lang() == 'it':
            return d.strftime('%d/%m/%Y %H:%M' if with_time else '%d/%m/%Y')
        return d.strftime('%d %b %Y, %H:%M' if with_time else '%d %b %Y')

    def stock_status(p) -> str:
        if p['quantity'] == 0:
            return 'out'
        return 'low' if p['quantity'] <= p['min_stock'] else 'ok'

    app.jinja_env.globals.update(t=t, lang=get_lang, category_name=category_name, stock_status=stock_status)
    app.jinja_env.filters.update(money=money, number=number, datefmt=datefmt)

    # ---- CSRF: one token per session, checked on every POST ----------------
    def csrf_token() -> str:
        if '_csrf' not in session:
            session['_csrf'] = secrets.token_urlsafe(32)
        return session['_csrf']

    app.jinja_env.globals['csrf_token'] = csrf_token

    @app.before_request
    def check_csrf():
        if request.method == 'POST' and not app.config.get('TESTING_NO_CSRF'):
            sent = request.form.get('_csrf') or request.headers.get('X-CSRF')
            if not sent or sent != session.get('_csrf'):
                abort(400, t('err.csrf'))

    # ---- Language switch -------------------------------------------------
    @app.get('/lang/<code>')
    def set_lang(code):
        if code in LANGS:
            session['lang'] = code
        nxt = request.args.get('next', '')
        return redirect(nxt if nxt.startswith('/') and not nxt.startswith('//') else url_for('views.dashboard'))

    from .auth import bp as auth_bp
    from .views import bp as views_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(views_bp)
    return app
