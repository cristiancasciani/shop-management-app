"""Italian / English interface texts. Templates call t('key', **vars)."""
from flask import request, session

LANGS = ('it', 'en')

TEXTS = {
    'it': {
        'app.name': 'Circuito', 'app.tagline': 'Gestionale negozio',
        'nav.dashboard': 'Dashboard', 'nav.products': 'Prodotti', 'nav.movements': 'Movimenti', 'nav.new': 'Nuovo prodotto',
        'nav.logout': 'Esci', 'nav.reset': 'Ripristina dati demo', 'nav.reset_confirm': 'Ripristinare tutti i dati demo? Le modifiche andranno perse.',
        'demo.banner': 'Demo: negozio immaginario, dati di esempio. Puoi modificare tutto liberamente.',
        'login.title': 'Accedi', 'login.user': 'Utente', 'login.password': 'Password', 'login.submit': 'Entra',
        'login.hint': 'Credenziali demo', 'login.error': 'Utente o password non corretti.',
        'dash.title': 'Dashboard', 'dash.products': 'Prodotti', 'dash.units': 'Pezzi in magazzino',
        'dash.value_cost': 'Valore magazzino (costo)', 'dash.value_retail': 'Valore di vendita',
        'dash.low': 'Sotto scorta', 'dash.out': 'Esauriti',
        'dash.by_category': 'Valore magazzino per categoria', 'dash.by_category_sub': 'A prezzo di costo, in euro',
        'dash.flow': 'Pezzi entrati e usciti', 'dash.flow_sub': 'Ultimi 30 giorni, per giorno',
        'dash.in': 'Entrati', 'dash.out_units': 'Usciti', 'dash.table': 'Vedi come tabella',
        'dash.alerts': 'Da riordinare', 'dash.alerts_empty': 'Nessun prodotto sotto scorta.',
        'dash.recent': 'Ultimi movimenti', 'dash.all_movements': 'Tutti i movimenti',
        'dash.day': 'Giorno', 'dash.category': 'Categoria', 'dash.value': 'Valore',
        'products.title': 'Prodotti', 'products.search': 'Cerca nome, codice o marca…',
        'products.category': 'Categoria', 'products.brand': 'Marca', 'products.stock': 'Scorte',
        'products.all': 'Tutte', 'products.all_brands': 'Tutte le marche',
        'products.stock_all': 'Tutte', 'products.stock_low': 'Sotto scorta', 'products.stock_out': 'Esauriti', 'products.stock_ok': 'Disponibili',
        'products.count': '{n} prodotti', 'products.count_one': '1 prodotto', 'products.empty': 'Nessun prodotto trovato.',
        'products.clear': 'Azzera filtri', 'products.export': 'Esporta',
        'col.sku': 'Codice', 'col.name': 'Prodotto', 'col.brand': 'Marca', 'col.category': 'Categoria',
        'col.cost': 'Costo', 'col.price': 'Prezzo', 'col.qty': 'Q.tà', 'col.min': 'Scorta min.', 'col.value': 'Valore',
        'col.status': 'Stato', 'col.updated': 'Aggiornato', 'col.date': 'Data', 'col.kind': 'Tipo', 'col.reason': 'Causale',
        'col.user': 'Utente', 'col.note': 'Nota', 'col.margin': 'Margine', 'col.actions': 'Azioni',
        'status.ok': 'Disponibile', 'status.low': 'Sotto scorta', 'status.out': 'Esaurito',
        'form.new': 'Nuovo prodotto', 'form.edit': 'Modifica prodotto', 'form.save': 'Salva', 'form.cancel': 'Annulla',
        'form.qty_help': 'Quantità iniziale. In seguito si cambia con carichi e scarichi.',
        'form.min_help': 'Sotto questa quantità il prodotto compare tra quelli da riordinare.',
        'err.required': 'Campo obbligatorio.', 'err.number': 'Inserisci un numero valido (≥ 0).',
        'err.integer': 'Inserisci un numero intero (≥ 0).', 'err.sku_taken': 'Codice già usato da un altro prodotto.',
        'err.price_below_cost': 'Il prezzo è inferiore al costo.', 'err.qty_negative': 'Non ci sono abbastanza pezzi in magazzino.',
        'err.qty_zero': 'La quantità deve essere diversa da zero.', 'err.csrf': 'Sessione scaduta, riprova.',
        'flash.created': 'Prodotto “{name}” creato.', 'flash.updated': 'Prodotto “{name}” aggiornato.',
        'flash.deleted': 'Prodotto “{name}” eliminato.', 'flash.moved': 'Movimento registrato: {qty} pz, giacenza ora {stock}.',
        'flash.reset': 'Dati demo ripristinati.',
        'detail.edit': 'Modifica', 'detail.delete': 'Elimina', 'detail.delete_confirm': 'Eliminare questo prodotto e il suo storico?',
        'detail.history': 'Storico movimenti', 'detail.move': 'Registra movimento', 'detail.no_moves': 'Nessun movimento.',
        'detail.stock': 'Giacenza', 'detail.value': 'Valore a costo', 'detail.margin': 'Margine unitario',
        'move.kind': 'Tipo', 'move.qty': 'Quantità', 'move.reason': 'Causale', 'move.note': 'Nota (facoltativa)', 'move.submit': 'Registra',
        'move.adjust_help': 'Rettifica: scrivi la differenza, anche negativa (es. -2).',
        'kind.in': 'Carico', 'kind.out': 'Scarico', 'kind.adjust': 'Rettifica',
        'reason.initial': 'Giacenza iniziale', 'reason.purchase': 'Acquisto da fornitore', 'reason.sale': 'Vendita',
        'reason.return': 'Reso cliente', 'reason.damaged': 'Danneggiato', 'reason.count': 'Inventario', 'reason.other': 'Altro',
        'movements.title': 'Movimenti', 'movements.all': 'Tutti', 'movements.from': 'Dal', 'movements.to': 'Al',
        'movements.filter': 'Filtra', 'movements.summary': 'Entrati {inn} · usciti {out} · {n} movimenti',
        'page.prev': 'Precedente', 'page.next': 'Successiva', 'page.of': 'Pagina {p} di {n}',
        'lang.switch': 'English', 'footer.demo': 'Progetto dimostrativo di',
    },
    'en': {
        'app.name': 'Circuito', 'app.tagline': 'Shop management',
        'nav.dashboard': 'Dashboard', 'nav.products': 'Products', 'nav.movements': 'Stock movements', 'nav.new': 'New product',
        'nav.logout': 'Log out', 'nav.reset': 'Reset demo data', 'nav.reset_confirm': 'Reset all demo data? Your changes will be lost.',
        'demo.banner': 'Demo: imaginary shop, sample data. Feel free to change anything.',
        'login.title': 'Sign in', 'login.user': 'Username', 'login.password': 'Password', 'login.submit': 'Sign in',
        'login.hint': 'Demo credentials', 'login.error': 'Wrong username or password.',
        'dash.title': 'Dashboard', 'dash.products': 'Products', 'dash.units': 'Units in stock',
        'dash.value_cost': 'Stock value (cost)', 'dash.value_retail': 'Retail value',
        'dash.low': 'Low stock', 'dash.out': 'Out of stock',
        'dash.by_category': 'Stock value by category', 'dash.by_category_sub': 'At cost price, in euros',
        'dash.flow': 'Units in and out', 'dash.flow_sub': 'Last 30 days, per day',
        'dash.in': 'In', 'dash.out_units': 'Out', 'dash.table': 'View as table',
        'dash.alerts': 'To reorder', 'dash.alerts_empty': 'No product is below minimum stock.',
        'dash.recent': 'Latest movements', 'dash.all_movements': 'All movements',
        'dash.day': 'Day', 'dash.category': 'Category', 'dash.value': 'Value',
        'products.title': 'Products', 'products.search': 'Search name, SKU or brand…',
        'products.category': 'Category', 'products.brand': 'Brand', 'products.stock': 'Stock',
        'products.all': 'All', 'products.all_brands': 'All brands',
        'products.stock_all': 'All', 'products.stock_low': 'Low stock', 'products.stock_out': 'Out of stock', 'products.stock_ok': 'In stock',
        'products.count': '{n} products', 'products.count_one': '1 product', 'products.empty': 'No products found.',
        'products.clear': 'Clear filters', 'products.export': 'Export',
        'col.sku': 'SKU', 'col.name': 'Product', 'col.brand': 'Brand', 'col.category': 'Category',
        'col.cost': 'Cost', 'col.price': 'Price', 'col.qty': 'Qty', 'col.min': 'Min. stock', 'col.value': 'Value',
        'col.status': 'Status', 'col.updated': 'Updated', 'col.date': 'Date', 'col.kind': 'Type', 'col.reason': 'Reason',
        'col.user': 'User', 'col.note': 'Note', 'col.margin': 'Margin', 'col.actions': 'Actions',
        'status.ok': 'In stock', 'status.low': 'Low stock', 'status.out': 'Out of stock',
        'form.new': 'New product', 'form.edit': 'Edit product', 'form.save': 'Save', 'form.cancel': 'Cancel',
        'form.qty_help': 'Starting quantity. Later it changes through stock movements.',
        'form.min_help': 'Below this quantity the product shows up in the reorder list.',
        'err.required': 'Required.', 'err.number': 'Enter a valid number (≥ 0).',
        'err.integer': 'Enter a whole number (≥ 0).', 'err.sku_taken': 'SKU already used by another product.',
        'err.price_below_cost': 'Price is lower than cost.', 'err.qty_negative': 'Not enough units in stock.',
        'err.qty_zero': 'Quantity must not be zero.', 'err.csrf': 'Session expired, please try again.',
        'flash.created': 'Product “{name}” created.', 'flash.updated': 'Product “{name}” updated.',
        'flash.deleted': 'Product “{name}” deleted.', 'flash.moved': 'Movement saved: {qty} units, stock is now {stock}.',
        'flash.reset': 'Demo data reset.',
        'detail.edit': 'Edit', 'detail.delete': 'Delete', 'detail.delete_confirm': 'Delete this product and its history?',
        'detail.history': 'Movement history', 'detail.move': 'Record a movement', 'detail.no_moves': 'No movements.',
        'detail.stock': 'In stock', 'detail.value': 'Value at cost', 'detail.margin': 'Unit margin',
        'move.kind': 'Type', 'move.qty': 'Quantity', 'move.reason': 'Reason', 'move.note': 'Note (optional)', 'move.submit': 'Save',
        'move.adjust_help': 'Adjustment: enter the difference, negative allowed (e.g. -2).',
        'kind.in': 'Stock in', 'kind.out': 'Stock out', 'kind.adjust': 'Adjustment',
        'reason.initial': 'Opening stock', 'reason.purchase': 'Supplier purchase', 'reason.sale': 'Sale',
        'reason.return': 'Customer return', 'reason.damaged': 'Damaged', 'reason.count': 'Stock count', 'reason.other': 'Other',
        'movements.title': 'Stock movements', 'movements.all': 'All', 'movements.from': 'From', 'movements.to': 'To',
        'movements.filter': 'Filter', 'movements.summary': 'In {inn} · out {out} · {n} movements',
        'page.prev': 'Previous', 'page.next': 'Next', 'page.of': 'Page {p} of {n}',
        'lang.switch': 'Italiano', 'footer.demo': 'Demo project by',
    },
}

CATEGORY_NAMES = {
    'it': {'smartphones': 'Smartphone', 'laptops': 'Portatili', 'tablets': 'Tablet', 'audio': 'Audio',
           'wearables': 'Indossabili', 'gaming': 'Gaming', 'smart_home': 'Casa smart', 'accessories': 'Accessori'},
    'en': {'smartphones': 'Smartphones', 'laptops': 'Laptops', 'tablets': 'Tablets', 'audio': 'Audio',
           'wearables': 'Wearables', 'gaming': 'Gaming', 'smart_home': 'Smart home', 'accessories': 'Accessories'},
}


def get_lang() -> str:
    lang = session.get('lang')
    if lang in LANGS:
        return lang
    return request.accept_languages.best_match(LANGS) or 'it'


def t(key: str, **kw) -> str:
    text = TEXTS[get_lang()].get(key, key)
    return text.format(**kw) if kw else text


def category_name(key: str) -> str:
    return CATEGORY_NAMES[get_lang()].get(key, key)
