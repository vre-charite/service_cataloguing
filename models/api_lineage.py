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

from flask_restx import Api, Resource, fields
from atlas_api import module_api
from services.logger_services.logger_factory_service import SrvLoggerFactory

_logger = SrvLoggerFactory('api_lineage_action').get_logger()

class CreationForm:
    def __init__(self, event=None):
        if event:
            self._attribute_map = event
        else:
            self._attribute_map = {
                'input_path': '',
                'output_path': '',
                'project_code': '',
                'pipeline_name': '',
                'description': '',
                'process_timestamp': '',
            }

    @property
    def to_dict(self):
        return self._attribute_map

    @property
    def input_path(self):
        return self._attribute_map['input_path']

    @input_path.setter
    def input_path(self, input_path):
        self._attribute_map['input_path'] = input_path

    @property
    def output_path(self):
        return self._attribute_map['output_path']

    @output_path.setter
    def output_path(self, output_path):
        self._attribute_map['output_path'] = output_path

    @property
    def project_code(self):
        return self._attribute_map['project_code']

    @project_code.setter
    def project_code(self, project_code):
        self._attribute_map['project_code'] = project_code

    @property
    def pipeline_name(self):
        return self._attribute_map['pipeline_name']

    @pipeline_name.setter
    def pipeline_name(self, pipeline_name):
        self._attribute_map['pipeline_name'] = pipeline_name

    @property
    def description(self):
        return self._attribute_map['description']

    @description.setter
    def description(self, description):
        self._attribute_map['description'] = description

    @property
    def process_timestamp(self):
        return self._attribute_map['process_timestamp']

    @process_timestamp.setter
    def process_timestamp(self, process_timestamp):
        self._attribute_map['process_timestamp'] = process_timestamp

def creationFormFactory(post_form):
    try:
        my_form = CreationForm()
        my_form.input_path = post_form['inputFullPath']
        my_form.output_path = post_form['outputFullPath']
        my_form.project_code = post_form['projectCode']
        my_form.pipeline_name = post_form['pipelineName']
        my_form.description = post_form.get('description', '')
        my_form.process_timestamp = post_form.get('process_timestamp', None)
        return my_form
    except Exception as e:
        _logger.error(str(e))
        raise(Exception('Invalid post form: ' + str(post_form)))

lineage_get_sample_res = '''
{
    "result": {
    "baseEntityGuid": "2697440c-c150-460a-b697-bd5bca1518f3",
    "lineageDirection": "BOTH",
    "lineageDepth": 20,
    "guidEntityMap": {
        "94f65a97-c8f0-41ec-8b33-eca77aa2e599": {
            "typeName": "Process",
            "attributes": {
                "owner": "root",
                "qualifiedName": "lineage:test:1016:etl:cleaned:to:trained",
                "name": "lineage:test:1016:etl:cleaned:to:trained",
                "description": "lineage:test:1016:etl:cleaned:to:trained"
            },
            "guid": "94f65a97-c8f0-41ec-8b33-eca77aa2e599",
            "status": "ACTIVE",
            "displayText": "lineage:test:1016:etl:cleaned:to:trained",
            "classificationNames": [],
            "meaningNames": [],
            "meanings": [],
            "isIncomplete": false,
            "labels": []
        },
        "016014c2-f49a-4aa7-a25f-39596a1b21d4": {
            "typeName": "DataSet",
            "attributes": {
                "qualifiedName": "lineage:test:1016723:trained:test2",
                "name": "lineage:test:1016723:trained:test2"
            },
            "guid": "016014c2-f49a-4aa7-a25f-39596a1b21d4",
            "status": "ACTIVE",
            "displayText": "lineage:test:1016723:trained:test2",
            "classificationNames": [],
            "meaningNames": [],
            "meanings": [],
            "isIncomplete": false,
            "labels": []
        },
        "3a824599-388b-4391-924a-c3543bd7d232": {
            "typeName": "DataSet",
            "attributes": {
                "qualifiedName": "lineage:test:1016723:cleaned:test2",
                "name": "lineage:test:1016723:cleaned:test2"
            },
            "guid": "3a824599-388b-4391-924a-c3543bd7d232",
            "status": "ACTIVE",
            "displayText": "lineage:test:1016723:cleaned:test2",
            "classificationNames": [],
            "meaningNames": [],
            "meanings": [],
            "isIncomplete": false,
            "labels": []
        },
        "2697440c-c150-460a-b697-bd5bca1518f3": {
            "typeName": "DataSet",
            "attributes": {
                "qualifiedName": "lineage:test:1016723:raw:test2",
                "name": "lineage:test:1016723:raw:test2"
            },
            "guid": "2697440c-c150-460a-b697-bd5bca1518f3",
            "status": "ACTIVE",
            "displayText": "lineage:test:1016723:raw:test2",
            "classificationNames": [],
            "meaningNames": [],
            "meanings": [],
            "isIncomplete": false,
            "labels": []
        },
        "1ab6c46f-2d5b-4bcc-b1e3-a8e6431d0183": {
            "typeName": "Process",
            "attributes": {
                "owner": "root",
                "qualifiedName": "lineage:test:1016:etl:raw:to:cleaned",
                "name": "lineage:test:1016:etl:raw:to:cleaned",
                "description": "lineage:test:1016:etl:raw:to:cleaned"
            },
            "guid": "1ab6c46f-2d5b-4bcc-b1e3-a8e6431d0183",
            "status": "ACTIVE",
            "displayText": "lineage:test:1016:etl:raw:to:cleaned",
            "classificationNames": [],
            "meaningNames": [],
            "meanings": [],
            "isIncomplete": false,
            "labels": []
        }
    },
    "relations": [
        {
            "fromEntityId": "1ab6c46f-2d5b-4bcc-b1e3-a8e6431d0183",
            "toEntityId": "3a824599-388b-4391-924a-c3543bd7d232",
            "relationshipId": "e7da2c36-a46f-49da-b2e3-438cbede9a0d"
        },
        {
            "fromEntityId": "2697440c-c150-460a-b697-bd5bca1518f3",
            "toEntityId": "1ab6c46f-2d5b-4bcc-b1e3-a8e6431d0183",
            "relationshipId": "36c9a578-e733-46d1-b21e-b19aa5ea37e4"
        },
        {
            "fromEntityId": "94f65a97-c8f0-41ec-8b33-eca77aa2e599",
            "toEntityId": "016014c2-f49a-4aa7-a25f-39596a1b21d4",
            "relationshipId": "2363d9e8-83df-42b5-883d-56c26e25aa0a"
        },
        {
            "fromEntityId": "3a824599-388b-4391-924a-c3543bd7d232",
            "toEntityId": "94f65a97-c8f0-41ec-8b33-eca77aa2e599",
            "relationshipId": "d4f55413-82d8-44fb-91f6-5e0d7d55eb41"
        }
    ]
}
}
'''

lineage_post_form = module_api.model(
    'lineage_post_form',
    {
        'inputFullPath': fields.String(readOnly=True, description='inputFullPath'),
        'outputFullPath': fields.String(readOnly=True, description='outputFullPath'),
        'projectCode': fields.String(readOnly=True, description='projectCode'),
        'pipelineName': fields.String(readOnly=True, description='pipelineName'),
        'description': fields.String(readOnly=True, description='description'),
    }
)


lineage_import_post_form = module_api.model(
    'lineage_import_post_form',
    {
        'full_path': fields.String(readOnly=True, description='full_path'),
        'entity_type': fields.String(readOnly=True, description='entity_type')
    }
)

