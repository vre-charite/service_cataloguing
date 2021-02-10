from flask_restx import Api, Resource, fields
from config import ConfigClass

module_api = Api(version='1.0', title='Atlas API',
    description='Atlas API', doc='/v1/api-doc'
)

atlas_entity_ns = module_api.namespace('Atlas Entity Actions', description='Operation on Atlas Entity', path ='/')

from .entity_operation import EntityAction, EntityQueryBasic, EntityActionByGuid, EntityTagByGuid, EntityByGuidBulk
from .audit_operation import AuditAction
from .lineage_operation import LineageAction, LineageActionV2, LineageImport
from .file_data_operations import FileDataOperations

######################################################### Entity API ###############################################
atlas_entity_ns.add_resource(EntityAction, '/v1/entity')
atlas_entity_ns.add_resource(EntityQueryBasic, '/v1/entity/basic')
atlas_entity_ns.add_resource(EntityByGuidBulk, '/v1/entity/guid/bulk')

atlas_entity_ns.add_resource(EntityActionByGuid, '/v1/entity/guid/<guid>')
atlas_entity_ns.add_resource(EntityTagByGuid, '/v1/entity/guid/<guid>/labels')

######################################################### Audit API ###############################################
atlas_entity_ns.add_resource(AuditAction, '/v1/entity/guid/<guid>/audit')

######################################################### Lineage API ############################################
atlas_entity_ns.add_resource(LineageAction, '/v1/lineage')
atlas_entity_ns.add_resource(LineageActionV2, '/v2/lineage')
atlas_entity_ns.add_resource(LineageImport, '/v2/lineage-import')
######################################################### File Meta API ############################################
atlas_entity_ns.add_resource(FileDataOperations, '/v2/filedata')