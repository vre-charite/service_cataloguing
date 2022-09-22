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

from enum import Enum
from atlas_api import module_api
from flask_restx import Api, Resource, fields
from config import ConfigClass

class EDataType(Enum):
    nfs_file = 0
    nfs_file_processed = 1
    nfs_file_download = 2

class EPipeline(Enum):
    dicom_edit = 0
    data_transfer = 1

file_data_post_form = module_api.model(
    'FileDataPostForm',
    {
        'global_entity_id': fields.String(readOnly=True, description='global_entity_id'),
        'uploader': fields.String(readOnly=True, description='uploader'),
        'file_name': fields.String(readOnly=True, description='file name (not include path)'),
        'path': fields.String(readOnly=True, description='path'),
        'file_size': fields.Integer(readOnly=True, description='file size'),
        'description': fields.String(readOnly=True, description='description'),
        'namespace': fields.String(readOnly=True, description='namespace', enum=['greenroom', 'core']),
        'project_code': fields.String(readOnly=True, description='project code'),
        'labels': fields.List(readOnly=True, description='labels', cls_or_instance=fields.String), ## optional
        "dcm_id": fields.String(readOnly=True, description=''), ## optional
        'processed_pipeline': fields.String(readOnly=True, description='processed_pipeline'), ## optional, for processed file
        'operator': fields.String(readOnly=True, description='operator'), ## optional, for processed file
    }
)