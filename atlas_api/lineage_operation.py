from flask import request, make_response, jsonify
from flask_restx import Api, Resource, fields
import requests
from requests.auth import HTTPBasicAuth
from config import ConfigClass
from services.logger_services.logger_factory_service import SrvLoggerFactory
from services.atlas.lineage_manager import SrvLineageMgr
import models.api_lineage as lineage_models
from . import atlas_entity_ns, module_api
import os, datetime
import json

class LineageAction(Resource):
    __logger = SrvLoggerFactory('api_lineage_action').get_logger()
    lineage_mgr = SrvLineageMgr()
    @atlas_entity_ns.response(200, lineage_models.lineage_get_sample_res)
    def get(self):
        '''
        get lineage, query params: full_path, type_name(optional), direction defult(INPUT)
        '''
        entity_name = request.args.get('full_path', None)
        type_name = request.args.get('type_name', None)
        direction = request.args.get('direction', 'INPUT') # "BOTH" or "INPUT" or "OUTPUT"
        if entity_name:
            response = self.lineage_mgr.get(entity_name, type_name, direction)
            if response.status_code == 200:
                response_json = response.json()
                print(response_json)
                return {"result": response_json}, 200
            else:
                self.__logger.error('Error: %s', response.text)
                return {"result": response.text}, response.status_code
        else:
            return {"result": 'Bad Request, param full_path not found'}, 400
    @atlas_entity_ns.expect(lineage_models.lineage_post_form)
    def post(self):
        '''
        add new lineage to the metadata service by payload
            {
                'inputFullPath': '',
                'outputFullPath': '',
                'projectCode': '',
                'pipelineName': '',
                'description': '',
            }
        '''
        self.__logger.info('Calling LineageAction post')
        post_data = request.get_json()
        self.__logger.info('Recieving the payload: %s', json.dumps(post_data))
        creation_form = {}
        try:
            creation_form = lineage_models.creationFormFactory(post_data)
        except Exception as e:
            self.__logger.error('Error in create lineage: %s', str(e))
            return {"result": str(e)}, 400
        try:
            ## create atlas lineage
            res = self.lineage_mgr.create(creation_form)
            # log it if not 200 level response
            if res.status_code >= 300:
                self.__logger.error('Error in response: %s', res.text)
                return {"result": res.text}, res.status_code
        except Exception as e:
            self.__logger.error('Error in create lineage: %s', str(e))
            return {"result": str(e)}, 403

        return {'result': res.json()}, res.status_code

