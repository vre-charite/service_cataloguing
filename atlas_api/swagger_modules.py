from flask_restx import Api, Resource, fields

from . import module_api

entity_attribute = module_api.model('entity_attribute', {
    # only samples
    "owner": fields.String(readOnly=True, description='Who owns the entity'),
    "qualifiedName": fields.String(readOnly=True, description='Name of the entity'),
    "path": fields.String(readOnly=True, description='In nfs, the path of the file'),
    "name": fields.String(readOnly=True, description='Name of the entity'),
    "updateBy":fields.String(readOnly=True, description='Who updated the entity last time'),

    # other options
    "other_property":fields.String(readOnly=True, description='Other entities')

})


entity = module_api.model('entity', {
    "typeName": fields.String(readOnly=True, description='The metadata type of entity'),
    "attributes": fields.Nested(entity_attribute, readOnly=True, description='Attribute that entity has'),
    "isIncomplete": fields.Boolean(readOnly=True, description='Is entity completed'),
    "status": fields.String(readOnly=True, description='Active/Inactive'),
    "createdBy": fields.String(readOnly=True, description='Who create the entity'),
    "version": fields.Integer(readOnly=True, description='Version number'),
})

create_update_entity = module_api.model('create_update_entity', {
    "entity": fields.Nested(entity, readOnly=True, description='entity description')
})