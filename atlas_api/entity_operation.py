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
from flask_restx import Api, Resource, fields
import requests
from requests.auth import HTTPBasicAuth
from config import ConfigClass  
import json

from app import app
from atlas_api.swagger_modules import entity_attribute, entity, create_update_entity
from . import atlas_entity_ns, module_api

class EntityAction(Resource):

    post_sample_return = '''
    # Below are the sample return
    {
        "result": {
            "mutatedEntities": {
                "CREATE": [
                    {
                        "typeName": "nfs_path",
                        "guid": "c502b322-01d2-4516-99dc-3398c66c203c",
                        "status": "ACTIVE"
                    }
                ]
            },
            "guidAssignments": {
                "-4348009237357927": "c502b322-01d2-4516-99dc-3398c66c203c"
            }
        }
    }
    '''

    @atlas_entity_ns.expect(create_update_entity)
    @atlas_entity_ns.response(200, post_sample_return)
    # to add the new entity to atlas
    def post(self):
        '''
        add new entity to the metadata service by payload
        '''
        post_data = request.get_json()

        try:
            headers = {'content-type': 'application/json'}
            res = requests.post(ConfigClass.ATLAS_API+'api/atlas/v2/entity', 
                verify=False, json=post_data, 
                auth=HTTPBasicAuth(ConfigClass.ATLAS_ADMIN, ConfigClass.ATLAS_PASSWD),
                headers=headers
            )

            # log it if not 200 level response
            if res.status_code >= 300:
                app.logger.error('Error in response: %s', res.text)
                return {"result": res.text}, res.status_code

        except Exception as e:
            app.logger.error('Error in creating new entity: %s', str(e))
            return {"result":str(e)}, 403

        return {'result':res.json()}, res.status_code


class EntityQueryBasic(Resource):

    query_sample_return = '''
    {
        "result":[
            {
                "typeName": "nfs_path",
                "attributes": {
                    # attribute when created
                    "owner": "admin",
                    "createTime": 0,
                    "name": "test_path_66"
                },
                # global Id
                "guid": "0363af63-0478-4dbc-ba16-25a82e3163ff",
                "status": "ACTIVE",
                "displayText": "test_path_66",
                "classificationNames": [],
                "classifications": [],
                "meaningNames": [],
                "meanings": []
            },
        ]
    }
    '''
    
    query_payload = module_api.model('query_payload_basic', {
        'excludeDeletedEntities': fields.Boolean(readOnly=True, description=''),
        'includeSubClassifications': fields.Boolean(readOnly=True, description=''),
        'includeSubTypes': fields.Boolean(readOnly=True, description=''),
        'includeClassificationAttributes': fields.Boolean(readOnly=True, description=''),
        'limit': fields.Integer(readOnly=True, description='number of entities for return'),
        'offset': fields.Integer(readOnly=True, description='pagination'),
        'typeName': fields.String(readOnly=True, description='type of entity')
    })

    # to accept the payload to query to entity
    @atlas_entity_ns.expect(query_payload)
    @atlas_entity_ns.response(200, query_sample_return)
    def post(self):
        '''
        Get list of entities by the payload query
        '''
        post_data = request.get_json()

        #######################################################################
        # Note: I dont know why atlas will give wrong approximate count
        # but aggregation in the quick search will return correct number
        # here I call the quick search again to get that number for pagination
        #######################################################################
        # print(post_data)
        type_name = post_data.get('typeName', None)
        app.logger.debug(ConfigClass.ATLAS_API+'api/atlas/v2/search/quick')
        app.logger.debug('EntityQueryBasic post_data' + str(post_data))
        limit = 0 
        offset = 0
        if post_data.get("limit", None):
            limit = post_data.pop("limit")
        if post_data.get("offset", None):
            offset = post_data.pop("offset")

        post_data["limit"] = 99999 
        try:
            headers = {'content-type': 'application/json'}
            res = requests.post(ConfigClass.ATLAS_API+'api/atlas/v2/search/basic', 
                verify=False, headers=headers, json=post_data, 
                auth=HTTPBasicAuth(ConfigClass.ATLAS_ADMIN, ConfigClass.ATLAS_PASSWD)
            )
            # log it if not 200 level response
            if res.status_code >= 300:
                app.logger.error('Error in response: %s', res.text)
                return {"result": res.text}, res.status_code
            # also update the approximate count
            app.logger.debug('EntityQueryBasic res 2: ' + str(res.json()))
            ret_json = res.json()

        except Exception as e:
            app.logger.error('Error in getting file list: %s', str(e))
            return {"result":str(e)}, 403
        entity_data = []
        if 'entities' in ret_json:
            entity_data = ret_json["entities"]

        approximateCount = len(entity_data)

        if int(offset):
            entity_data = entity_data[int(offset):]
        if int(limit):
            entity_data = entity_data[:int(limit)]
        ret_json["entities"] = entity_data
        ret_json["approximateCount"] = approximateCount
        ret_json["searchParameters"]["limit"] = int(limit) 
        ret_json["searchParameters"]["offset"] = int(offset) 
        app.logger.debug('EntityQueryBasic ret_json: ' + str(ret_json))
        return {"result":ret_json}, res.status_code
        

class EntityActionByGuid(Resource):
    entity_sample_return = '''
    {
        "result": {
            "referredEntities": {},
            "entity": {
                "typeName": "nfs_path",
                "attributes": {
                    "owner": "admin",
                    "path": "test_path_66",
                    "createTime": 0,
                    "updateBy": null,
                    "name": "test_path_66",
                    "description": null
                },
                "guid": "0363af63-0478-4dbc-ba16-25a82e3163ff",
                "status": "ACTIVE",
                "createdBy": "admin",
                "updatedBy": "admin",
                "createTime": 1594320166984,
                "updateTime": 1594320166984,
                "version": 0
            }
        }
    }
    '''

    # to get the guid entity from atlas
    @atlas_entity_ns.response(200, entity_sample_return)
    def get(self, guid):
        '''
        get specific entity by guid
        '''
        app.logger.info('Recieving the parameter: %s', guid)

        try:
            headers = {'content-type': 'application/json'}
            res = requests.get(ConfigClass.ATLAS_API+'api/atlas/v2/entity/guid/%s'%(guid), 
                verify=False, headers=headers, 
                auth=HTTPBasicAuth(ConfigClass.ATLAS_ADMIN, ConfigClass.ATLAS_PASSWD)
            )

            # log it if not 200 level response
            if res.status_code >= 300:
                app.logger.error('Error in response: %s', res.text)
                return {"result": res.text}, res.status_code
        except Exception as e:
            app.logger.error('Error in getting entity by guid: %s', str(e))
            return {"result":str(e)}, 403

        return {"result":res.json()}, res.status_code


    # deprecate the entity by guid
    def delete(self, guid):
        app.logger.info('Recieving the parameter: %s', guid)

        try:
            headers = {'content-type': 'application/json'}
            res = requests.delete(ConfigClass.ATLAS_API+'api/atlas/v2/entity/guid/%s'%(guid), 
                verify=False, headers=headers, 
                auth=HTTPBasicAuth(ConfigClass.ATLAS_ADMIN, ConfigClass.ATLAS_PASSWD)
            )

            # log it if not 200 level response
            if res.status_code >= 300:
                app.logger.error('Error in response: %s', res.text)
                return {"result": res.text}, res.status_code
        except Exception as e:
            app.logger.error('Error in getting entity by guid: %s', str(e))
            return {"result":str(e)}, 403

        return {"result":res.json()}, res.status_code


class EntityByGuidBulk(Resource):
    entity_sample_return = '''
    {
        "result": { "entities": [{
            "referredEntities": {},
            "entity": {
                "typeName": "nfs_path",
                "attributes": {
                    "owner": "admin",
                    "path": "test_path_66",
                    "createTime": 0,
                    "updateBy": null,
                    "name": "test_path_66",
                    "description": null
                },
                "guid": "0363af63-0478-4dbc-ba16-25a82e3163ff",
                "status": "ACTIVE",
                "createdBy": "admin",
                "updatedBy": "admin",
                "createTime": 1594320166984,
                "updateTime": 1594320166984,
                "version": 0
            }
        }]}
    }
    '''

    @atlas_entity_ns.response(200, entity_sample_return)
    def post(self):
        guids = request.get_json().get("guids", [])
        if not guids:
            return {"result": "guids required"}, 400

        try:
            res = requests.get(ConfigClass.ATLAS_API+'api/atlas/v2/entity/bulk', 
                auth=HTTPBasicAuth(ConfigClass.ATLAS_ADMIN, ConfigClass.ATLAS_PASSWD),
                params={"guid": guids}
            )
            if res.status_code >= 300:
                app.logger.error('Error in response: %s', res.text)
                return {"result": res.text}, res.status_code
        except Exception as e:
            app.logger.error('Error in getting entity by guid: %s', str(e))
            return {"result":str(e)}, 403
        return {"result":res.json()}, res.status_code


class EntityTagByGuid(Resource):
    def post(self, guid):
        '''
        the api allow to update the tags given one guid
        '''

        post_data = request.get_json()
        label = post_data.get('labels', None)
        if not isinstance(label, list):
            return {"result": "labels is required"}, 403
        app.logger.info('Recieving the parameter: %s', guid)

        try:
            ###################################
            # NOTE HERE THIS IS ONLY TEMPORARY SOLUTION
            # label should contain alphanumeric characters, _ or -
            import os
            cmd = '''
            curl -XPOST -H "Content-type: application/json" -d '%s' '%sapi/atlas/v2/entity/guid/%s/labels' -u %s:%s
            '''%(json.dumps(post_data['labels']), ConfigClass.ATLAS_API, guid, ConfigClass.ATLAS_ADMIN, ConfigClass.ATLAS_PASSWD)
            stream = os.popen(cmd)

            # here since the curl will return the str so try to parse into json
            # the special case is if it success then it will return nothing
            output = stream.read()
            if output != '':
                error_json = json.loads(output)
                return {"result":error_json.get('errorMessage', None)}, 403

        except Exception as e:
            if "Invalid label" in str(e):
                return {"result":str(e)}, 403
            app.logger.error('Error in update entity by guid: %s', str(e))
            return {"result":str(e)}, 500

        return {"result":'success'}, 200

    def get(self, guid):
        try:
            url = ConfigClass.ATLAS_API + "api/atlas/v2/entity/guid/{}".format(guid)
            res = requests.get(
                url, 
                auth=HTTPBasicAuth(ConfigClass.ATLAS_ADMIN, ConfigClass.ATLAS_PASSWD)
            )
            if res.status_code == 200:
                return res.json()['entity'].get('labels', []), 200
            else:
                return res.text, res.status_code
        except Exception as e:
            app.logger.error('Error in update entity by guid: %s', str(e))
            return {"result":str(e)}, 500
