# -*- coding: utf-8 -*-

from functools import wraps
import json

from flask import request, abort, render_template, make_response, jsonify
import markdown

from objectchecker import ObjectChecker

def render_md(text):
    exts = [
        'markdown.extensions.tables',
        'markdown.extensions.codehilite',
    ]
    return markdown.markdown(text, extensions=exts)

class RouteLoader(object):
    def __init__(self, api_configs, extra_middlewares=None):
        super(RouteLoader, self).__init__()

        self.api_configs = api_configs
        self.mounted_api_configs = []

        if hasattr(extra_middlewares, '__call__'):
            self.extra_middlewares = [extra_middlewares]
        elif isinstance(extra_middlewares, (tuple, list)):
            self.extra_middlewares = extra_middlewares
        else:
            self.extra_middlewares = []

    def route(self, flask_app_or_blueprint, config_path, **options):
        def decorator(handler):
            module_name, api_name = config_path.split('.')
            route_config = self.api_configs[module_name][api_name]

            self.mounted_api_configs.append(route_config)

            # Options for original Flask route options
            rule     = route_config['url']
            endpoint = options.pop('endpoints', None)
            options['methods'] = [route_config['method']]

            @wraps(handler)
            def wrapped_handler(*args, **kwargs):
                print route_config
                # Check query
                if route_config.get('query'):
                    default_required = False
                    custom_directives = {
                      '$desc'      : None,
                      '$name'      : None,
                      '$type'      : None,
                      '$example'   : None,
                    }

                    checker = ObjectChecker(default_required=default_required, custom_directives=custom_directives)

                    incomming_query = request.args
                    ret = checker.check(incomming_query, route_config.get('query'))
                    if not ret.get('isValid'):
                        # !! Change check failure response here
                        abort(make_response(jsonify(ret), 400))

                # Check body
                if route_config.get('body'):
                    default_required = False
                    custom_directives = {
                      '$desc'      : None,
                      '$name'      : None,
                      '$example'   : None,
                    }

                    checker = ObjectChecker(default_required=default_required, custom_directives=custom_directives)

                    incomming_body = json.loads(request.get_data(as_text=True))
                    ret = checker.check(incomming_body, route_config.get('body'))
                    if not ret.get('isValid'):
                        # !! Change check failure response here
                        abort(make_response(jsonify(ret), 400))

                # Run extra checkers
                if self.extra_middlewares:
                    for checker in self.extra_middlewares:
                        checker(route_config)

                # Run handler
                return handler(*args, **kwargs)

            return flask_app_or_blueprint.add_url_rule(rule, endpoint, wrapped_handler, **options)

        return decorator

    def doc_handler(self):
        return render_template('api_doc.html',
                mounted_api_configs=self.mounted_api_configs,
                render_md=render_md)

    def create_doc(self, flask_app_or_blueprint, rule):
        options = {
            'methods': ['GET']
        }
        return flask_app_or_blueprint.add_url_rule(rule, None, self.doc_handler, **options)
