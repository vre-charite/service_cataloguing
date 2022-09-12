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

from config import ConfigClass
from flask import request, make_response, jsonify
from flask_restx import Resource
from services.logger_services.logger_factory_service import SrvLoggerFactory
from services.atlas.file_data_manager import SrvFileDataMgr
import models.data_models as data_models
import models.api_response as api_res_models
from . import atlas_entity_ns, module_api
import json

class FileDataOperations(Resource):
    __logger = SrvLoggerFactory('api_file_data').get_logger()
    file_data_mgr = SrvFileDataMgr()
    @atlas_entity_ns.expect(data_models.file_data_post_form)
    def post(self):
        post_data = request.get_json()
        self.__logger.info('FileDataOperations Recieving the payload: %s', json.dumps(post_data))
        try:
            required = ['uploader', 'file_name', 'path', 'file_size', 'namespace', 'project_code', 'global_entity_id']
            for param in required:
                if not param in post_data:
                    return {"result": "{} is required".format(param)}, 404
            uploader = post_data.get('uploader')
            file_name = post_data.get('file_name')
            path = post_data.get('path')
            file_size = post_data.get('file_size')
            description = post_data.get('description', 'N/A')
            namespace = post_data.get('namespace')
            project_code = post_data.get('project_code')
            project_name = post_data.get('project_name', project_code)
            labels = post_data.get('labels', [])
            dcm_id = post_data.get("dcm_id", None)
            global_entity_id = post_data.get('global_entity_id')

            response = self.file_data_mgr.create(
                global_entity_id,
                uploader,
                path,
                file_name,
                file_size,
                description,
                namespace,
                project_code,
                project_name,
                labels,
                dcm_id=dcm_id,
                guid=None
            )
            if response.status_code == 200:
                response_json = response.json()
                return {"result": response_json}, 200
            else:
                self.__logger.error('Error: %s', response.text)
                return {"result": response.text}, response.status_code
        except Exception as e:
            self.__logger.error('Error in update entity: %s', str(e))
            return {"result": str(e)}, 403

    def delete(self):
        post_data = request.get_json()
        self.__logger.info('Calling FileDataOperations delete: ' + str(post_data))
        ## validate inputs
        required = ['file_name', 'path', 'trash_path', 'trash_file_name', 'operator', 'file_name_suffix', 'trash_geid']
        for param in required:
            if not param in post_data:
                return {"result": "{} is required".format(param)}, 404
        file_name = post_data.get('file_name')
        file_name_suffix = post_data.get('file_name_suffix')
        path = post_data.get('path')
        full_path = path + '/' + file_name
        trash_path = post_data.get('trash_path')
        trash_file_name = post_data.get('trash_file_name')
        updated_original_file_path = post_data.get('updated_original_file_path', None)
        operator = post_data.get('operator')
        trash_geid = post_data.get('trash_geid')
        
        ## Entity_types
        entity_types = ['file_data']
        ## Archive filedata entity
        response = api_res_models.APIResponse()
        deletion_ress = []
        for entity_type in entity_types:
            deletion_res = self.file_data_mgr.delete(full_path, entity_type, trash_path, trash_file_name,
            operator, file_name_suffix, geid=trash_geid, updated_original_path=updated_original_file_path)
            if deletion_res.get('error'):
                return deletion_res, deletion_res['status_code']
            else:
                deletion_ress.append(deletion_res)
        response.set_code(api_res_models.EAPIResponseCode.success)
        response.set_result(deletion_ress)
        return response.to_dict, response.code
