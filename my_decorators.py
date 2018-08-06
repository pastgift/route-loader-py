# -*- coding: utf-8 -*-

from functools import wraps

from flask import request

def logged(handler):
    @wraps(handler)
    def wrapped_handler(*args, **kwargs):
        print '[LOG] -> {} {}'.format(request.method, request.full_path)

        return handler(*args, **kwargs)

    return wrapped_handler