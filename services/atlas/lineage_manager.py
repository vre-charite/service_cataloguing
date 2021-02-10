from pprint import pprint
from time import time
from models.meta_class import MetaService
import requests
from requests.auth import HTTPBasicAuth
from config import ConfigClass
from services.logger_services.logger_factory_service import SrvLoggerFactory
from models.api_lineage import creationFormFactory, CreationForm
from models.data_models import EDataType, EPipeline
import os, datetime, json

class SrvLineageMgr(metaclass=MetaService):
    _logger = SrvLoggerFactory('api_lineage_action').get_logger()

    def __init__(self):
        self.base_url = ConfigClass.ATLAS_API
        self.lineage_endpoint = 'api/atlas/v2/lineage/uniqueAttribute/type'
        self.entity_bulk_endpoint = 'api/atlas/v2/entity/bulk'
        self.search_endpoint = 'api/atlas/v2/search/attribute'

    def lineage_to_typename(self, pipeline_name):
        '''
        return (parent_type, child_type)
        '''
        return {
            EPipeline.dicom_edit.name: (EDataType.nfs_file.name, EDataType.nfs_file_processed.name),
            EPipeline.data_transfer.name: (EDataType.nfs_file.name, EDataType.nfs_file_processed.name)
        }.get(pipeline_name, (EDataType.nfs_file.name, EDataType.nfs_file_processed.name))

    def entityname_to_typename(self, entity_name):
        '''
        return type_name
        '''
        if 'processed' in entity_name:
            return EDataType.nfs_file_processed.name
        if '/vre-data/tvbcloud/raw' in entity_name:
            return EDataType.nfs_file_processed.name
        return EDataType.nfs_file.name

    def create(self, creation_form: CreationForm, version = 'v1'):
        '''
        create lineage in Atlas
        '''
        ## to atlas post form
        input_file_name = os.path.basename(creation_form.input_path)
        output_file_name = os.path.basename(creation_form.output_path)
        self._logger.debug('[SrvLineageMgr]input_file_path: ' + creation_form.input_path)
        self._logger.debug('[SrvLineageMgr]output_file_path: ' + creation_form.output_path)
        dt = datetime.datetime.now() - datetime.timedelta(seconds=2) ## temporary solution
        utc_time = dt.replace(tzinfo = datetime.timezone.utc) 
        current_timestamp = utc_time.timestamp() if not creation_form.process_timestamp \
            else creation_form.process_timestamp
        qualifiedName = '{}:{}:{}:{}:to:{}'.format(
            creation_form.project_code,
            creation_form.pipeline_name,
            current_timestamp,
            input_file_name,
            output_file_name)
        ## v2 uses new entity type, v1 uses old one
        typenames = self.lineage_to_typename(creation_form.pipeline_name) if version == 'v1' else ['file_data', 'file_data']
        atlas_post_form_json = {
            "entities": [{
                "typeName": "Process",
                "attributes": {
                    "createTime": current_timestamp,
                    "updateTime": current_timestamp,
                    "qualifiedName": qualifiedName if version == 'v1' else qualifiedName + ":v2",
                    "name": qualifiedName if version == 'v1' else qualifiedName + ":v2",
                    "description": creation_form.description,
                    "inputs":[{
                        "guid": self.get_guid_by_entity_name(creation_form.input_path, typenames[0]),
                        "typeName": typenames[0]
                    }],
                    "outputs":[{
                        "guid": self.get_guid_by_entity_name(creation_form.output_path, typenames[1]),
                        "typeName": typenames[1]
                    }]
                }
            }]
        }
        self._logger.debug('[SrvLineageMgr]atlas_post_form_json: ' + str(atlas_post_form_json))
         ## create atlas lineage
        headers = {'content-type': 'application/json'}
        res = requests.post(self.base_url + self.entity_bulk_endpoint, 
            verify = False, json = atlas_post_form_json, 
            auth = HTTPBasicAuth(ConfigClass.ATLAS_ADMIN, ConfigClass.ATLAS_PASSWD),
            headers=headers
        )
        return res

    def get(self, entity_name, type_name, direction, depth = 50):
        type_name = type_name if type_name else self.entityname_to_typename(entity_name)
        url = self.base_url + self.lineage_endpoint \
            + '/{}'.format(type_name)
        response = requests.get(url, 
                verify = False, 
                params={
                    'attr:name': entity_name,
                    'depth': depth,
                    'direction': direction
                }, 
                auth = HTTPBasicAuth(ConfigClass.ATLAS_ADMIN, ConfigClass.ATLAS_PASSWD)
        )
        return response

    def search_entity(self, entity_name, type_name = None):
        if not type_name:
            type_name = self.entityname_to_typename(entity_name)
        url = self.base_url + self.search_endpoint
        response = requests.get(url, 
                verify = False, 
                params={
                    'attrName': 'name',
                    'typeName': type_name,
                    'attrValuePrefix': entity_name
                }, 
                auth = HTTPBasicAuth(ConfigClass.ATLAS_ADMIN, ConfigClass.ATLAS_PASSWD)
        )
        if response.status_code == 200 and response.json().get('entities'):
            return response
        else:
            response_processed_search = requests.get(url, 
                verify = False, 
                params={
                    'attrName': 'name',
                    'typeName': "nfs_file_processed",
                    'attrValuePrefix': entity_name
                }, 
                auth = HTTPBasicAuth(ConfigClass.ATLAS_ADMIN, ConfigClass.ATLAS_PASSWD))
            if response_processed_search.status_code == 200 and response_processed_search.json().get('entities'):
                return response_processed_search
            else:
                raise(Exception('Not Found Entity: ' + entity_name))

    def get_guid_by_entity_name(self, entity_name, type_name = None):
        search_res = self.search_entity(entity_name, type_name)
        if search_res.status_code == 200:
            my_json = search_res.json()
            self._logger.debug('[SrvLineageMgr]search_res : ' + str(my_json))
            entities = my_json['entities']
            found = [entity for entity in entities if entity['attributes']['name'] == entity_name]
            return found[0]['guid'] if found else None
        else:
            self._logger.error('Error when get_guid_by_entity_name: ' + search_res.text)
            return None

    def mirror_file_data_lineage(self, input_relation_info: dict, output_relation_info: dict,
        guid_map: dict):
        try:
            ## create lineage post form
            input_node_id = input_relation_info['fromEntityId']
            input_node = guid_map[input_node_id]
            process_node_id = input_relation_info['toEntityId']
            output_node_id = output_relation_info['toEntityId']
            output_node = guid_map[output_node_id]
            input_name = input_node['attributes']['name']
            output_name = output_node['attributes']['name']
            process_node = guid_map[process_node_id]
            process_timestamp = round(float(process_node['attributes']['qualifiedName'].split(':')[2]))
            qualifiedName = process_node['attributes']['qualifiedName'] + ":" + "importedat{}".format(round(time())) 
            # post request
            atlas_post_form_json = {
                "entities": [{
                    "typeName": "Process",
                    "attributes": {
                        "createTime": process_timestamp,
                        "updateTime": process_timestamp,
                        "qualifiedName": qualifiedName,
                        "name": qualifiedName,
                        "description": "Auto Imported",
                        "inputs":[{
                            "guid": self.get_guid_by_entity_name(input_name, "file_data"),
                            "typeName": "file_data"
                        }],
                        "outputs":[{
                            "guid": self.get_guid_by_entity_name(output_name, "file_data"),
                            "typeName": "file_data"
                        }]
                    }
                }]
            }
            ## create atlas lineage
            headers = {'content-type': 'application/json'}
            res = requests.post(self.base_url + self.entity_bulk_endpoint, 
                verify = False, json = atlas_post_form_json, 
                auth = HTTPBasicAuth(ConfigClass.ATLAS_ADMIN, ConfigClass.ATLAS_PASSWD),
                headers=headers
            )
            if res.status_code == 200:
                return res.json()
            else:
                raise res.text
        except Exception as e:
            return {
                        "error": True,
                        "msg": str(e)
                    }