from flask import request, make_response, jsonify
# from flask_restful import Resource
from flask_restx import Api, Resource, fields
import requests
from requests.auth import HTTPBasicAuth
from config import ConfigClass 

import json

class RelationAction(Resource):
    sample_post = '''
    {
        "createTime" : 12345,
        "createdBy" : "admin",
        "end1" : {
            "guid" : "bd57d993-8124-47ea-8204-fe2c91e9be83",
            "typeName" : "hdfs_path"
        },
        "end2" : {
            "guid" : "23adf710-9484-438e-9982-2c8ec4031b3b",
            "typeName" : "hdfs_path"
        },
        "propagateTags" : "NONE",
        "label" : "test_label",
        "status" : "ACTIVE",
        "provenanceType" : 12345,
        "updateTime" : 12345,
        "updatedBy" : "admin",
        "version" : 12345,
        "typeName" : "test_label"
    }

    '''
    def post(self):
        '''
        add new entity to the metadata service by payload
        '''
        app.logger.info('Calling RelationAction post')
        post_data = request.get_json()
        app.logger.info('Recieving the payload: %s', json.dumps(post_data))

        try:
            headers = {'content-type': 'application/json'}
            res = requests.post(ConfigClass.ATLAS_API+'api/atlas/v2/relationship', 
                verify=False, json=post_data, 
                auth=HTTPBasicAuth(ConfigClass.ATLAS_ADMIN, ConfigClass.ATLAS_PASSWD),
                headers=headers
            )

            # log it if not 200 level response
            if res.status_code >= 300:
                app.logger.error('Error in response: %s', res.text)
                return {"result": res.text}, res.status_code
        except Exception as e:
            app.logger.error('Error in create relationship: %s', str(e))
            return {"result":str(e)}, 403

        return {'result':res.json()}, res.status_code
