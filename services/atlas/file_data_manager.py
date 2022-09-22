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

from models.meta_class import MetaService
from services.logger_services.logger_factory_service import SrvLoggerFactory
from config import ConfigClass
import requests
import time
import json
import os

class SrvFileDataMgr(metaclass=MetaService):
    _logger = SrvLoggerFactory('api_file_data').get_logger()
    def __init__(self):
        self.base_url = ConfigClass.ATLAS_API
        self.entity_endpoint = 'api/atlas/v2/entity'
        self.search_endpoint = 'api/atlas/v2/search/attribute'
        self.entity_uniquename_endpoint = "api/atlas/v2/entity/uniqueAttribute/type/{}?attr:qualifiedName={}"
        self.entity_type = 'file_data'

    def create(self, geid, uploader, path, file_name, file_size,
        description, namespace, project_code, project_name,
        labels, dcm_id=None , guid=None):
        '''
        create data entity or update in Atlas
        ''' 
        headers = {'content-type': 'application/json'}

        attrs = {
            'global_entity_id': geid,
            'name': geid,
            'file_name': file_name,
            'path': path,
            'qualifiedName': geid,
            'full_path': geid, # full path requires unique
            'file_size': file_size,
            "dcm_id": dcm_id,
            'archived': False,
            'description': description,
            'owner': uploader,
            'time_created': time.time(),
            'time_lastmodified': time.time(),
            'namespace': namespace,
            'project_code': project_code,
            'bucketName': project_code,
            ## ------------------------------------------------------------------------------------
            'createTime': time.time(),
            'modifiedTime': 0,
            'replicatedTo': None,
            'userDescription': None,
            'isFile': False,
            'numberOfReplicas': 0,
            'replicatedFrom': None,
            'displayName': None,
            'extendedAttributes': None,
            'nameServiceId': None,
            'posixPermissions': None,
            'clusterName': None,
            'isSymlink': False,
            'group': None,
        }
        if dcm_id:
            attrs["dcm_id"] = dcm_id
        if project_name:
            attrs['project_name'] = project_name
        
        atlas_post_form_json = {
            'referredEntities': {},
            'entity': {
                'typeName': self.entity_type,
                'attributes': attrs,
                'isIncomplete': False,
                'status': 'ACTIVE',
                'createdBy': uploader,
                'version': 0,
                'relationshipAttributes': {
                    'schema': [],
                    'inputToProcesses': [],
                    'meanings': [],
                    'outputFromProcesses': []
                },
                'customAttributes': {},
                'labels': labels
            }
        }
        if guid:
            atlas_post_form_json['entity']['guid'] = guid
        
        res = requests.post(self.base_url + self.entity_endpoint, 
            verify = False, json = atlas_post_form_json, 
            auth = requests.auth.HTTPBasicAuth(ConfigClass.ATLAS_ADMIN,
                ConfigClass.ATLAS_PASSWD),
            headers=headers
        )
        return res

    def delete(self, entity_name, type_name, trash_path, trash_file_name, operator, file_name_suffix, geid=None, updated_original_path=None):
        try:
            ## Entity geid
            neo4j_url = ConfigClass.NEO4J_SERVICE + 'nodes/File/query'
            post_payload = {
                "full_path": entity_name
            }
            neo4j_res = requests.post(neo4j_url, json=post_payload)
            neo4j_data = json.loads(neo4j_res.text)
            if len(neo4j_data) > 0:
                entity_geid = neo4j_data[0]["global_entity_id"]

            query_url = self.base_url + self.entity_uniquename_endpoint.format(type_name, entity_geid)
            self._logger.info(f"query url is {query_url}")
            query_res = requests.get(query_url, auth = requests.auth.HTTPBasicAuth(ConfigClass.ATLAS_ADMIN,
                    ConfigClass.ATLAS_PASSWD))
            if not query_res.status_code == 200 and not query_res.status_code == 404:
                return {
                    'error': True,
                    'status_code': 404,
                    'error_msg': 'Invalid entity {}, not found in Atlas: '.format(type_name) + entity_name
                }
            ## Not found in Atlas
            if query_res.status_code == 404:
                self._logger.info('Not found in atlas {}, skipped deletion: '.format(type_name) + entity_name)
                return {
                    'msg': 'Skipped deleting entity {}: '.format(type_name) + entity_name
                }
            else:
                entity = query_res.json()['entity']
                self._logger.info(f"Entity in atlas is: {str(entity)}")
                ## update file name
                file_name = entity['attributes'].get('file_name') or entity['attributes'].get('fileName')
                file_path = entity['attributes'].get('path')
                myfilename, file_extension = os.path.splitext(file_name)
                updated_full_path = file_path + "/" + trash_file_name if not updated_original_path else updated_original_path + "/" + trash_file_name
                if type_name == 'file_data':
                    # entity['attributes']['full_path'] = updated_full_path
                    entity['attributes']['file_name'] = trash_file_name
                else:
                    entity['attributes']['fileName'] = trash_file_name
                # entity['attributes']['name'] = updated_full_path
                # entity['attributes']['qualifiedName'] = updated_full_path
                ## Add attribute archived
                if entity['attributes'].get('archived'):
                    entity['attributes']['archived'] = True
                if not entity.get('customAttributes'):
                    entity['customAttributes'] = {}
                entity['customAttributes']['archived'] = True
                ## Update timestamp
                if entity['attributes'].get('time_lastmodified'):
                    entity['attributes']['time_lastmodified'] = time.time()
                    entity['attributes']['time_archived'] = time.time()
                entity['attributes']['modifiedTime'] = time.time()
                if entity['attributes'].get('pipeline', None):
                    entity['attributes'].pop('pipeline')
            update_payload = {
                "entity": entity
            }
            # print(update_payload)
            print(self.base_url + self.entity_endpoint)
            headers = {'content-type': 'application/json'}
            res = requests.post(self.base_url + self.entity_endpoint, 
                verify = False, json = update_payload, 
                auth = requests.auth.HTTPBasicAuth(ConfigClass.ATLAS_ADMIN,
                    ConfigClass.ATLAS_PASSWD),
                headers=headers
            )
            ## Create trash entity
            if type_name == 'file_data':
                ## fetch global entity id
                entity_id_url = ConfigClass.UTILITY_SERVICE + "utility/id?entity_type=file_data"
                respon_entity_id_fetched = requests.get(entity_id_url)
                if respon_entity_id_fetched.status_code == 200:
                    pass
                else:
                    raise Exception('Entity id fetch failed: ' + entity_id_url)
                trash_geid = respon_entity_id_fetched.json()['result'] if not geid else geid
                ## need inherite tags from nfs_file and it will be deprecated after not using nfs_file
                location = 'nfs_file'

                if not ConfigClass.ROOT_PATH in entity_name or not '/raw' in entity_name:
                    self._logger.info('entity_name is: {}'.format(str(entity_name)))
                    location = 'nfs_file_processed'
                query_url = self.base_url + self.entity_uniquename_endpoint.format(location, entity_name)
                query_res = requests.get(query_url, auth = requests.auth.HTTPBasicAuth(ConfigClass.ATLAS_ADMIN,
                        ConfigClass.ATLAS_PASSWD))

                tags = []
                if query_res.status_code == 200:
                    nfs_entity = query_res.json()['entity']
                    tags = nfs_entity['labels']
                    self._logger.info('delete nfs entity: {}'.format(str(nfs_entity)))
                self._logger.info('delete tags: {}'.format(str(tags)))

                operator_role = 'admin'
                neo4j_url = ConfigClass.NEO4J_SERVICE + 'relations/query'
                headers = {'content-type': 'application/json'}
                project_code = entity['attributes'].get('project_code')
                neo4j_json = {
                    "start_label": "User",
                    "end_label": "Container",
                    "start_params": {
                        "name": operator
                    },
                    "end_params": {
                        "code": project_code
                    }
                }
                neo4j_res = requests.post(neo4j_url, json=neo4j_json)
                neo4j_data = json.loads(neo4j_res.text)

                if len(neo4j_data) > 0:
                    operator_role = neo4j_data[0]["r"]["type"]

                self._logger.info('delete entity payload: operator: {}, operator_role: {}, project_code: {}'.format(operator, operator_role, project_code))

                origin_guid = entity.pop('guid', None)
                trash_full_path = trash_path + '/' + trash_file_name
                entity['attributes']['name'] = trash_geid
                entity['attributes']['qualifiedName'] = trash_geid
                entity['attributes']['file_name'] = trash_file_name
                entity['attributes']['full_path'] = trash_geid
                entity['attributes']['path'] = trash_path
                entity['attributes']['time_archived'] = time.time()
                entity['attributes']['archived'] = False
                entity['attributes']['global_entity_id'] = trash_geid
                entity['relationshipAttributes'] = {
                    'schema': [],
                    'inputToProcesses': [],
                    'meanings': [],
                    'outputFromProcesses': []
                }
                entity['customAttributes'] = {}
                if entity['attributes'].get('pipeline', None):
                    entity['attributes'].pop('pipeline')
                if len(tags) > 0:
                    entity['labels'] = tags
                trash_payload = {
                    "entity": entity
                }
                self._logger.debug('trash_payload: ' + str(trash_payload))
                headers = {'content-type': 'application/json'}
                res = requests.post(self.base_url + self.entity_endpoint, 
                    verify = False, json = trash_payload, 
                    auth = requests.auth.HTTPBasicAuth(ConfigClass.ATLAS_ADMIN,
                        ConfigClass.ATLAS_PASSWD),
                    headers=headers
                )
            return res.json()
        except Exception as e:
            return {
                'error': True,
                'status_code': 500,
                'error_msg': str(e)
            }
