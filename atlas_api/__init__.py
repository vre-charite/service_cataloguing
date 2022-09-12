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
from config import ConfigClass

module_api = Api(version='1.0', title='Atlas API',
    description='Atlas API', doc='/v1/api-doc'
)

atlas_entity_ns = module_api.namespace('Atlas Entity Actions', description='Operation on Atlas Entity', path ='/')

from .entity_operation import EntityAction, EntityQueryBasic, EntityActionByGuid, EntityTagByGuid, EntityByGuidBulk
from .audit_operation import AuditAction
from .file_data_operations import FileDataOperations

######################################################### Entity API ###############################################
atlas_entity_ns.add_resource(EntityAction, '/v1/entity')
atlas_entity_ns.add_resource(EntityQueryBasic, '/v1/entity/basic')
atlas_entity_ns.add_resource(EntityByGuidBulk, '/v1/entity/guid/bulk')

atlas_entity_ns.add_resource(EntityActionByGuid, '/v1/entity/guid/<guid>')
atlas_entity_ns.add_resource(EntityTagByGuid, '/v1/entity/guid/<guid>/labels')

######################################################### Audit API ###############################################
atlas_entity_ns.add_resource(AuditAction, '/v1/entity/guid/<guid>/audit')

######################################################### File Meta API ############################################
atlas_entity_ns.add_resource(FileDataOperations, '/v2/filedata')