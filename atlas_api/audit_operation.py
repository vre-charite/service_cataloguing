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

from flask import request, make_response, jsonify
# from flask_restful import Resource
from flask_restx import Api, Resource

import requests
from requests.auth import HTTPBasicAuth

from config import ConfigClass  
from app import app
import json

class AuditAction(Resource):
    def get(self, guid):
        '''
        Get the audit log from entity by guid
        '''
        count = request.args.get('count', 25)
        app.logger.info('Recieving the parameter: count %s, guid %s', count, guid)

        try:
            headers = {'content-type': 'application/json'}
            res = requests.get(ConfigClass.ATLAS_API+'api/atlas/v2/entity/%s/audit?count=%d'%(guid, int(count)), 
                verify=False, headers=headers, 
                auth=HTTPBasicAuth(ConfigClass.ATLAS_ADMIN, ConfigClass.ATLAS_PASSWD)
            )

            # log it if not 200 level response
            if res.status_code >= 300:
                app.logger.error('Error in response: %s', res.text)
                return {"result": res.text}, res.status_code
        except Exception as e:
            app.logger.error('Error in get the audit log: %s', str(e))
            return {"result":str(e)}, 403

        return {"result": res.json()}, res.status_code