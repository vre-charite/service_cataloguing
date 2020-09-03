from flask import Flask, request
from flask_cors import CORS
from config import ConfigClass

import importlib

import logging
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig

app = Flask(__name__)

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

    # setup the logging 
    handler = RotatingFileHandler(ConfigClass.LOG_FILE, maxBytes=10000, backupCount=1)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # il.setFormatter(formatter)
    handler.setFormatter(formatter)
    
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    return app
