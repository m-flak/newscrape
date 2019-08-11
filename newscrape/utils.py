import os
import re
from flask import url_for

# LOADS SECRET KEY FROM FILE IN PACKAGE DIRECTORY
def get_secret_key(for_app):
    # our package directory
    pkg_path = os.path.abspath(os.path.dirname(__file__))

    with open(os.path.join(pkg_path,'secret.key'), 'r') as key:
         for_app.secret_key = key.read()

    return

# RUNS A REGEX THAT IF MATCHES RAISES A ValueError
def validate_inputs(inputs, regex):
    if isinstance(inputs, list):
        for s in inputs:
            if re.search(regex, s) is not None:
                raise ValueError("Item {} : {} is invalid".format(inputs.index(s), s))
        return
    else:
        s = inputs
        if re.search(regex, inputs) is not None:
            raise ValueError("Item {} : {} is invalid".format(inputs.index(s), s))
    return

# CHECK IF ANY OF THE PASSED ARGUMENTS ARE EMPTY STRINGS
def empty_params(*args):
    empties = [i for i in args if len(i) == 0]
    if len(empties) > 0:
        return True
    return False

# CHECK IF A URL EXISTS AS A ROUTE
def url_is_route(for_app, url):
    for k in for_app.view_functions.keys():
        if k == 'static' or k == 'bootstrap.static':
            continue
        if url in url_for(k):
            return True
    return False

# FIX B64 STRINGS WITH 'INCORRECT PADDING'
def fix_bad_b64(b64str):
    bs   = b64str
    bsl  = len(bs)
    if not bs[bsl-2:bsl] == '==':
        bs += '=='
    return bs
