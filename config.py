import os
import requests
from requests.models import HTTPError

srv_namespace = "service_cataloguing"
CONFIG_CENTER = "http://10.3.7.222:5062" \
    if os.environ.get('env') == "test" \
    else "http://common.utility:5062"


def vault_factory() -> dict:
    url = CONFIG_CENTER + \
        "/v1/utility/config/{}".format(srv_namespace)
    config_center_respon = requests.get(url)
    if config_center_respon.status_code != 200:
        raise HTTPError(config_center_respon.text)
    return config_center_respon.json()['result']


class ConfigClass(object):
    vault = vault_factory()
    env = os.environ.get('env')
    disk_namespace = os.environ.get('namespace')
    version = "0.1.0"
    # disk mounts
    NFS_ROOT_PATH = "./"
    VRE_ROOT_PATH = "/vre-data"
    ROOT_PATH = {
        "vre": "/vre-data"
    }.get(os.environ.get('namespace'), "/data/vre-storage")
    ATLAS_API = vault['ATLAS_API']+"/"
    NEO4J_SERVICE = vault['NEO4J_SERVICE']+"/v1/neo4j/"
    UTILITY_SERVICE = vault['UTILITY_SERVICE']+"/v1/"
    ATLAS_ADMIN = vault['ATLAS_ADMIN']
    ATLAS_PASSWD = vault['ATLAS_PASSWD']

    # the packaged modules
    api_modules = ["atlas_api"]
