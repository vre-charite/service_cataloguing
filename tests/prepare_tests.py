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

from app import create_app



app = create_app()
app.config['TESTING'] = True
app.config['DEBUG'] = True
test_client = app.test_client()


class SetUpTest:

    def __init__(self, log, test_app):
        self.log = log
        self.app = test_app

    def create_entity(self, payload):
        self.log.info(f"PREPARING TEST: START CREATING ENTITY")
        self.log.info(f"POST DATA: {payload}")
        res = self.app.post("/v1/entity", json=payload)
        self.log.info(f"RESPONSE DATA: {res.data}")
        self.log.info(F"RESPONSE STATUS: {res.status_code}")
        assert res.status_code == 200
        self.log.info(f"TESTING ENTITY CREATED")
        guid_res = res.json['result']
        guid_res = guid_res['mutatedEntities']['CREATE']
        guid = guid_res[0]['guid']
        self.log.info(f"SETUP GUID: {guid}")
        return guid

    def delete_entity(self, guid):
        self.log.info("Delete the testing entity".center(50, '='))
        self.log.warning(f"DELETING TESTING NODE: {guid}")
        res = self.app.delete('/v1/entity/guid/' + str(guid))
        self.log.info(f"DELETING STATUS: {res.status_code}")
        assert res.status_code == 200
        self.log.info(f"DELETING RESPONSE: {res.data}")
