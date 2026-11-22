"""Login / logout and the login_required guard."""
from functools import wraps

from flask import Blueprint, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .db import DEMO_USER, get_db
from .i18n import t

bp = Blueprint('auth', __name__)


@bp.before_app_request
def load_user():
    uid = session.get('user_id')
    g.user = get_db().execute('SELECT id, username, name FROM users WHERE id = ?', (uid,)).fetchone() if uid else None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login', next=request.full_path))
        return view(*args, **kwargs)
    return wrapped


@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = get_db().execute('SELECT * FROM users WHERE username = ?', (request.form.get('username', '').strip(),)).fetchone()
        if user and check_password_hash(user['password_hash'], request.form.get('password', '')):
            lang, csrf = session.get('lang'), session.get('_csrf')
            session.clear()
            session.update(user_id=user['id'], _csrf=csrf)
            if lang:
                session['lang'] = lang
            nxt = request.args.get('next', '')
            return redirect(nxt if nxt.startswith('/') and not nxt.startswith('//') else url_for('views.dashboard'))
        error = t('login.error')
    return render_template('login.html', error=error, demo=DEMO_USER)


@bp.post('/logout')
def logout():
    lang = session.get('lang')
    session.clear()
    if lang:
        session['lang'] = lang
    return redirect(url_for('auth.login'))
