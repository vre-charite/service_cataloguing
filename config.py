# flask configs
import os
class ConfigClass(object):
    # atlas api
    if os.environ['env'] == 'test':
        ATLAS_API = "http://10.3.7.218:21000/"
    else:
        ATLAS_API = "http://atlas.utility:21000/"


    ATLAS_ADMIN = "admin"
    ATLAS_PASSWD = "admin"

    # the packaged modules
    api_modules = ["atlas_api"]

    # error and access log
    LOG_FILE = 'application.log'
