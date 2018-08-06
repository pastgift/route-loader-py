# -*- coding: utf-8 -*-

import os

import yaml
from flask import Flask, Blueprint, request, render_template, jsonify

from routeloader import RouteLoader
from my_middlewares import check_something, check_something_by_args_factory
from my_decorators import logged



##### Init RouteLoader #####

# Load API config file
API_CONFIGS = None
basedir = os.path.abspath(os.path.dirname(__file__))
with open(basedir + '/api_configs.yaml') as _f:
    API_CONFIGS = yaml.load(_f.read())

extra_middlewares = [
    check_something,
    check_something_by_args_factory('check', 'ng'),
]
route_loader = RouteLoader(API_CONFIGS, extra_middlewares=extra_middlewares)



##### Use RouteLoader on Flask app object #####

# Flask app object
app = Flask(__name__)

@route_loader.route(app, 'app.index')
def index():
    return render_template('index.html')

@route_loader.route(app, 'app.doPost')
@logged
def do_post():
    ret = request.get_data(as_text=True)

    return ret



##### Use RouteLoader on Flask blueprint object #####

# Flask blueprint object
my_module_bp = Blueprint('my_module', __name__)

@route_loader.route(my_module_bp, 'myModule.index')
def my_module_index():
    return render_template('my_module_index.html')

@route_loader.route(my_module_bp, 'myModule.doPost')
@logged
def my_module_do_post(name):
    return jsonify({'message': 'Hello, ' + name})

# Register blueprint
app.register_blueprint(my_module_bp, url_prefix='/my_module')



##### API Documents #####
route_loader.create_doc(app, '/doc')



##### Other options #####
app.config['TEMPLATES_AUTO_RELOAD'] = True
