from app import create_app



app = create_app()
app.config['TESTING'] = True
app.config['DEBUG'] = True
test_client = app.test_client()


class SetUpTest:

    create_entity_response = """
                            {"result": 
                                {"mutatedEntities": 
                                    {"UPDATE": [{"typeName": "nfs_file_processed",
                                                 "attributes": {"owner": "test_owner",
                                                                "createTime": 1603814950,
                                                                "qualifiedName": "test_file",
                                                                "name": "/data/vre-storage/generate/processed/dicom_edit/test_file_name"
                                                                },
                                                 "guid": "f6b6db37-fe16-4bf9-92e4-68fa0b8320de",
                                                 "status": "ACTIVE",
                                                 "displayText": "/data/vre-storage/generate/processed/dicom_edit/test_file_name",
                                                 "classificationNames": [],
                                                 "classifications": [],
                                                 "meaningNames": [],
                                                 "meanings": [],
                                                 "isIncomplete": false,
                                                 "labels": []
                                                 }]
                                     },
                                 "guidAssignments": {
                                     "-9171417058881428": "f6b6db37-fe16-4bf9-92e4-68fa0b8320de"
                                 }
                                 }
                             }
                            """

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
