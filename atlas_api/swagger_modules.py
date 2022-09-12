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