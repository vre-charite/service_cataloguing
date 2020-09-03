from flask_restx import Api, Resource, fields
from config import ConfigClass

module_api = Api(version='1.0', title='Neo4j API',
    description='Neo4j API', doc='/v1/api-doc'
)

atlas_entity_ns = module_api.namespace('Atlas Entity Actions', description='Operation on Atlas Entity', path ='/')

from .entity_operation import EntityAction, EntityQueryBasic, EntityActionByGuid, EntityQueryDSL
from .audit_operation import AuditAction
from .relation_operation import RelationAction

######################################################### Entity API ###############################################
atlas_entity_ns.add_resource(EntityAction, '/v1/entity')
atlas_entity_ns.add_resource(EntityQueryBasic, '/v1/entity/basic')
atlas_entity_ns.add_resource(EntityQueryDSL, '/v1/entity/dsl')

atlas_entity_ns.add_resource(EntityActionByGuid, '/v1/entity/guid/<guid>')

######################################################### Audit API ###############################################
atlas_entity_ns.add_resource(AuditAction, '/v1/entity/guid/<guid>/audit')

######################################################### Relation API ############################################
atlas_entity_ns.add_resource(RelationAction, '/v1/relation')
