# Copyright 2022 Indoc Research
# 
# Licensed under the EUPL, Version 1.2 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
# You may obtain a copy of the Licence at:
# 
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
# 
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
# 

import os
import requests
from common import VaultClient
from requests.models import HTTPError
from pydantic import BaseSettings, Extra
from typing import Dict, Set, List, Any
from functools import lru_cache
from dotenv import load_dotenv

#load env var from local env file for local test
load_dotenv()
SRV_NAMESPACE = os.environ.get("APP_NAME", "service_cataloguing")
CONFIG_CENTER_ENABLED = os.environ.get("CONFIG_CENTER_ENABLED", "false")

def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == "false":
        return {}
    else:
        vc = VaultClient(os.getenv("VAULT_URL"), os.getenv("VAULT_CRT"), os.getenv("VAULT_TOKEN"))
        return vc.get_from_vault(SRV_NAMESPACE)


class Settings(BaseSettings):
    port: int = 5064
    host: str = "0.0.0.0"
    env: str = "test"
    version: str = "0.1.0"
    namespace: str = ""
    opentelemetry_enabled: bool = False
    
    ROOT_PATH: str
    ATLAS_API: str 
    NEO4J_SERVICE: str 
    UTILITY_SERVICE: str 
    ATLAS_ADMIN: str 
    ATLAS_PASSWD: str 

    # the packaged modules
    api_modules: List[str] = ["atlas_api"]

    def __init__(self):
        super().__init__()

        self.opentelemetry_enabled = True if self.OPEN_TELEMETRY_ENABLED == "TRUE" else False
        self.ATLAS_API += "/"
        self.NEO4J_SERVICE += "/v1/neo4j/"
        self.UTILITY_SERVICE += "/v1/"
    
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
                init_settings,
                load_vault_settings,
                env_settings,
                file_secret_settings,
            )
    

@lru_cache(1)
def get_settings():
    settings =  Settings()
    return settings

ConfigClass = Settings()
