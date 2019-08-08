from flask import Blueprint, abort, request, g, make_response
from flask_login import current_user
from newscrape.api import api_key_required
from newscrape.api.scraper import Scraper, GoogleSearch, BingSearch
from werkzeug.urls import url_unquote
import newscrape as ns

api = Blueprint('api', __name__)

@api.route('/')
def root():
    abort(400)

@api.route('/keywords', methods=['GET', 'POST'])
@api_key_required
def keywords():
    r = None

    if request.method == 'POST':
        # require action, keyword, and value as data fields
        if len(list(filter(lambda x: x in ['action','keyword','value'],\
        request.form))) < 3:
            abort(400)

        if request.form['action'] == 'update':
            kw = ns.models.Keyword.query.filter_by(uid=g.uid,
                                        keyword=request.form['keyword']).first()
            if kw is not None:
                kw.keyword = request.form['value']
                ns.db.session.commit()
            else:
                kw = ns.models.Keyword()
                kw.uid = g.uid
                kw.keyword = request.form['value']
                ns.db.session.add(kw)
                ns.db.session.commit()
            r = make_response({'status': 'OK', 'data': [],})
            r.mimetype = 'application/json'
        elif request.form['action'] == 'delete':
            kw = ns.models.Keyword.query.filter_by(uid=g.uid,
                                        keyword=request.form['keyword'])
            if not kw.count() >= 1:
                r = make_response({'status': 'FAIL', 'data': [],})
                r.mimetype = 'application/json'
            else:
                kw.delete()
                ns.db.session.commit()
                r = make_response({'status': 'OK', 'data': [],})
                r.mimetype = 'application/json'
    elif request.method == 'GET':
        user = ns.models.User.query.filter_by(id=g.uid).first()
        if user is None:
            r = make_response({'status': 'FAIL', 'data': [],})
            r.mimetype = 'application/json'
        else:
            r = make_response({'status': 'OK', 'data': user.get_keywords(),})
            r.mimetype = 'application/json'

    return r

@api.route('/stories')
@api_key_required
def stories():
    user = ns.models.User.query.filter_by(id=g.uid).first()
    r = None

    if user is None:
        r = make_response({'status': 'FAIL', 'data': [],})
        r.mimetype = 'application/json'
    else:
        scraper = Scraper()

        if 'newscrape_sprefs' in request.cookies:
            search_prefs = url_unquote(request.cookies['newscrape_sprefs']).split(',')
            for engine in search_prefs:
                if 'google' in engine:
                    scraper.add_scrapee(GoogleSearch(user.get_keywords()))
                elif 'bing' in engine:
                    scraper.add_scrapee(BingSearch(user.get_keywords()))

        scraper.scrape()
        stories = scraper.fetch_results()
        r = make_response({'status': 'OK', 'data': stories,})
        r.mimetype = 'application/json'

    return r
