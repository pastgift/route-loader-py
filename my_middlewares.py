# -*- coding: utf-8 -*-

from flask import request, abort, make_response

def check_something(config):
    if request.args.get('check_something', None) is not None:
        abort(make_response('Hit check_something in query, aborted.', 400))

def check_something_by_args_factory(field, value):
    def check_something_by_args(config):
        if request.args.get(field, None) == value:
            abort(make_response('Hit {}={} in query, aborted.'.format(field, value), 400))

    return check_something_by_args