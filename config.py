# flask configs
import os
class ConfigClass(object):
    # atlas api
    ATLAS_API = "http://atlas.utility:21000/"
    # ATLAS_API = "http://10.3.7.222:21000/"
    ATLAS_ADMIN = "admin"
    ATLAS_PASSWD = "admin"

    # the packaged modules
    api_modules = ["atlas_api"]

    # error and access log
    LOG_FILE = 'application.log'