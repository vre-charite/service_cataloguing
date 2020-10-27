from flask import Flask, request
from flask_cors import CORS
from config import ConfigClass

import importlib

from services.logger_services.logger_factory_service import SrvLoggerFactory

app = Flask(__name__)
_main_logger = SrvLoggerFactory('main').get_logger()

def create_app(extra_config_settings={}):
    # initialize app and config app
    app.config.from_object(__name__+'.ConfigClass')
    CORS(
        app, 
        origins="*",
        allow_headers=["Content-Type", "Authorization","Access-Control-Allow-Credentials"],
        supports_credentials=True, 
        intercept_exceptions=False)

    # initialize flask executor
    # executor.init_app(app)

    # dynamic add the dataset module by the config we set
    for apis in ConfigClass.api_modules:
        api = importlib.import_module(apis)
        api.module_api.init_app(app)
    
    app.logger = _main_logger

    return app
