# flask configs
import os
class ConfigClass(object):
    # atlas api
    if os.environ['env'] == 'test':
        ATLAS_API = "http://10.3.7.218:21000/"
        NEO4J_SERVICE = "http://10.3.7.216:5062/v1/neo4j/"
    else:
        ATLAS_API = "http://atlas.utility:21000/"
        NEO4J_SERVICE = "http://neo4j.utility:5062/v1/neo4j/"
   
    UTILITY_SERVICE = "http://common.utility:5062"

    ATLAS_ADMIN = "admin"
    ATLAS_PASSWD = "admin"

    # the packaged modules
    api_modules = ["atlas_api"]

    # error and access log
    LOG_FILE = 'application.log'

