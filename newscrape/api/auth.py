import werkzeug.urls
from datetime import datetime
from flask import request, abort, g
from functools import wraps
from newscrape.utils import validate_inputs
import newscrape as ns

# This will store the user's id in g as g.uid
def api_key_required(api_method):
    @wraps(api_method)
    def verify_api_key(*args, **kwargs):
        if len(request.args) == 0:
            abort(401)
        key = request.args['api']
        if not len(key) == 0:
            key = werkzeug.urls.url_unquote_plus(key)
            try:
                validate_inputs(key, r"\)|'|;|!|\||\\|,")
            except ValueError:
                abort(400)
            key_user = ns.models.User.query.filter_by(api_key=key).first()
            if key_user is None:
                abort(401)
            if datetime.now() > key_user.key_expire:
                abort(401)
            g.uid = key_user.id
            return api_method(*args, **kwargs)
        else:
            abort(401)

    return verify_api_key
