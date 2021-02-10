from flask import request, make_response, jsonify
from flask_restx import Api, Resource, fields
import requests
from requests.auth import HTTPBasicAuth
from config import ConfigClass
from services.logger_services.logger_factory_service import SrvLoggerFactory
from services.atlas.lineage_manager import SrvLineageMgr
import models.api_lineage as lineage_models
from . import atlas_entity_ns, module_api
import copy, pprint, time

class LineageActionV2(Resource):
    __logger = SrvLoggerFactory('api_lineage_action').get_logger()
    lineage_mgr = SrvLineageMgr()
    @atlas_entity_ns.response(200, lineage_models.lineage_get_sample_res)
    def get(self):
        '''
        get lineage, query params: full_path, direction defult(INPUT)
        '''
        entity_name = request.args.get('full_path', None)
        type_name = 'file_data'
        direction = request.args.get('direction', 'INPUT') # "BOTH" or "INPUT" or "OUTPUT"
        if entity_name:
            response = self.lineage_mgr.get(entity_name, type_name, direction)
            if response.status_code == 200:
                response_json = response.json()
                if response_json['guidEntityMap']:
                    pass
                else:
                    res_default_entity = self.lineage_mgr.search_entity(entity_name, type_name=type_name)
                    if res_default_entity.status_code == 200 and len(res_default_entity.json()['entities']) > 0:
                        default_entity = res_default_entity.json()['entities'][0]
                        response_json['guidEntityMap'] = {
                            '{}'.format(default_entity['guid']): default_entity
                        }
                    else:
                        return {"result": "Invalid Entity"}, 400
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
        post_data = request.get_json()
        creation_form = {}
        try:
            creation_form = lineage_models.creationFormFactory(post_data)
        except Exception as e:
            self.__logger.error('Error in create lineage: %s', str(e))
            return {"result": str(e)}, 400
        try:
            ## create atlas lineage
            res = self.lineage_mgr.create(creation_form, version='v2')
            # log it if not 200 level response
            if res.status_code >= 300:
                self.__logger.error('Error in response: %s', res.text)
                return {"result": res.text}, res.status_code
        except Exception as e:
            self.__logger.error('Error in create lineage: %s', str(e))
            return {"result": str(e)}, 403

        return {'result': res.json()}, res.status_code

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
                if response_json['guidEntityMap']:
                    pass
                else:
                    res_default_entity = self.lineage_mgr.search_entity(entity_name, type_name=type_name)
                    if res_default_entity.status_code == 200 and len(res_default_entity.json()['entities']) > 0:
                        default_entity = res_default_entity.json()['entities'][0]
                        response_json['guidEntityMap'] = {
                            '{}'.format(default_entity['guid']): default_entity
                        }
                    else:
                        return {"result": "Invalid Entity"}, 400
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
        post_data = request.get_json()
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

class LineageImport(Resource):
    __logger = SrvLoggerFactory('api_lineage_import').get_logger()
    lineage_mgr = SrvLineageMgr()
    @atlas_entity_ns.expect(lineage_models.lineage_import_post_form)
    def post(self):
        '''
        import existing lineage to new file data entity
            {
                'full_path': '',
                'entity_type': ''
            }
        '''
        post_data = request.get_json()
        try:
            required = ['full_path', 'entity_type']
            for param in required:
                if param not in post_data:
                    return {"error_message": "Invalid request, no {} found".format(param)}, 400
            full_path = post_data['full_path']
            entity_type = post_data['entity_type']
            # search original entity
            entity_uniquename_endpoint = "api/atlas/v2/entity/uniqueAttribute/type/{}?attr:qualifiedName={}"
            get_origin_entity_url = ConfigClass.ATLAS_API + entity_uniquename_endpoint.format(entity_type, full_path)
            query_res = requests.get(get_origin_entity_url, auth = requests.auth.HTTPBasicAuth(ConfigClass.ATLAS_ADMIN,
                    ConfigClass.ATLAS_PASSWD))
            ## Not found original entity in Atlas
            if not query_res.status_code == 200 and not query_res.status_code == 404:
                return {
                    'error_msg': 'Invalid entity {}, not found in Atlas: '.format(entity_type) + full_path
                }, 404
            if query_res.status_code == 404:
                self.__logger.info('Not found in atlas {}, skipped lineage synchro: '.format(entity_type) + full_path)
                return {
                    'error_msg': 'Not found in atlas {}, skipped lineage synchro: '.format(entity_type) + full_path
                }, 404
            ## get original entity
            entity = query_res.json()['entity']
            original_guid = entity['guid']
            # copy output relations
            response = self.lineage_mgr.get(full_path, entity_type, "OUTPUT")
            if response.status_code == 200:
                respon_json = response.json()
                my_relations = respon_json['relations']
                my_output_relations = [relation for relation in my_relations if relation['fromEntityId'] == original_guid]
                for relation in my_output_relations:
                    input_relations = [input_relation for input_relation in my_relations
                    if relation['toEntityId'] == input_relation['fromEntityId']]
                    for input_relation in input_relations:
                        respon_relation_mirror = self.lineage_mgr.mirror_file_data_lineage(
                            relation,
                            input_relation,
                            respon_json['guidEntityMap'])
                        if respon_relation_mirror.get('error'):
                            self.__logger.error(respon_relation_mirror)
            else:
                pass

        except Exception as e:
            self.__logger.error('Error in import lineage: %s', str(e))
            return {"result": str(e)}, 500
        self.__logger.info('Succeed mirrored: ' + full_path)
        return {'result': "Succeed"}, 200

