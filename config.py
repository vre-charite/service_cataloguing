import os
import requests
from requests.models import HTTPError
from pydantic import BaseSettings, Extra
from typing import Dict, Set, List, Any
from functools import lru_cache

SRV_NAMESPACE = os.environ.get("APP_NAME", "service_cataloguing")
CONFIG_CENTER_ENABLED = os.environ.get("CONFIG_CENTER_ENABLED", "false")
CONFIG_CENTER_BASE_URL = os.environ.get("CONFIG_CENTER_BASE_URL", "NOT_SET")

def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == "false":
        return {}
    else:
        return vault_factory(CONFIG_CENTER_BASE_URL)

def vault_factory(config_center) -> dict:
    url = f"{config_center}/v1/utility/config/{SRV_NAMESPACE}"
    config_center_respon = requests.get(url)
    if config_center_respon.status_code != 200:
        raise HTTPError(config_center_respon.text)
    return config_center_respon.json()['result']


class Settings(BaseSettings):
    port: int = 5064
    host: str = "0.0.0.0"
    env: str = "test"
    namespace: str = ""
    
    # disk mounts
    NFS_ROOT_PATH: str = "./"
    VRE_ROOT_PATH: str = "/vre-data"
    ROOT_PATH: str = {
        "vre": "/vre-data"
    }.get(namespace, "/data/vre-storage")
    ATLAS_API: str 
    NEO4J_SERVICE: str 
    UTILITY_SERVICE: str 
    ATLAS_ADMIN: str 
    ATLAS_PASSWD: str 

    # the packaged modules
    api_modules: List[str] = ["atlas_api"]


    # trigger pipeline
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                load_vault_settings,
                env_settings,
                init_settings,
                file_secret_settings,
            )
    

@lru_cache(1)
def get_settings():
    settings =  Settings()
    return settings

class ConfigClass(object):
    settings = get_settings()

    version = "0.1.0"
    env = settings.env
    disk_namespace = settings.namespace
    
    # disk mounts
    NFS_ROOT_PATH = settings.NFS_ROOT_PATH
    VRE_ROOT_PATH = settings.VRE_ROOT_PATH
    ROOT_PATH = settings.ROOT_PATH
    ATLAS_API = settings.ATLAS_API + "/"
    NEO4J_SERVICE = settings.NEO4J_SERVICE + "/v1/neo4j/"
    UTILITY_SERVICE = settings.UTILITY_SERVICE + "/v1/"
    ATLAS_ADMIN = settings.ATLAS_ADMIN
    ATLAS_PASSWD = settings.ATLAS_PASSWD

    # the packaged modules
    api_modules = settings.api_modules
