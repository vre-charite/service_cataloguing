import unittest
import time
from tests.logger import Logger
from tests.prepare_tests import SetUpTest, test_client
from config import ConfigClass


class TestLineageOperation(unittest.TestCase):

    log = Logger(name='test_lineage_operation.log')
    test = SetUpTest(log, test_client)
    upload_path = '/test_folder'
    bucket_name = 'test_bucket'
    guid_1 = None
    guid_2 = None
    create_lineage_sample_output = {"result": {
        "mutatedEntities": {"CREATE": [
            {"typeName": "Process",
             "attributes": {
                 "qualifiedName": "test_bucket:test-pipeline:2020-11-09T22:05:53.830955+00:00:test_file_1_1604977552:to:test_file_2_1604977552",
                 "name": "test_bucket:test-pipeline:2020-11-09T22:05:53.830955+00:00:test_file_1_1604977552:to:test_file_2_1604977552",
                 "description": ""
             },
             "guid": "e0ed9bf1-e587-4757-ae78-34922ecddea5",
             "status": "ACTIVE",
             "displayText": "test_bucket:test-pipeline:2020-11-09T22:05:53.830955+00:00:test_file_1_1604977552:to:test_file_2_1604977552",
             "classificationNames": [],
             "classifications": [],
             "meaningNames": [],
             "meanings": [],
             "isIncomplete": False,
             "labels": []
             }
        ],
            "UPDATE": [{"typeName": "nfs_file",
                        "attributes": {"owner": "unittest",
                                       "createTime": 1604977552,
                                       "qualifiedName": "/test_folder/test_file_1_1604977552",
                                       "name": "/test_folder/test_file_1_1604977552"
                                       },
                        "guid": "f0ad5988-3f56-4625-9df1-9e3d998d2c5c",
                        "status": "ACTIVE",
                        "displayText": "/test_folder/test_file_1_1604977552",
                        "classificationNames": [],
                        "meaningNames": [],
                        "meanings": [],
                        "isIncomplete": False,
                        "labels": []
                        },
                       {"typeName": "nfs_file",
                        "attributes": {
                            "owner": "unittest",
                            "createTime": 1604977552,
                            "qualifiedName": "/test_folder/test_file_2_1604977552",
                            "name": "/test_folder/test_file_2_1604977552"
                        },
                        "guid": "5bc169ce-615f-4aff-9414-aa5e39070319",
                        "status": "ACTIVE",
                        "displayText": "/test_folder/test_file_2_1604977552",
                        "classificationNames": [],
                        "meaningNames": [],
                        "meanings": [],
                        "isIncomplete": False,
                        "labels": []
                        }
                       ]
        },
        "guidAssignments": {"-9268633982505831": "e0ed9bf1-e587-4757-ae78-34922ecddea5"
                            }
    }}

    @classmethod
    def prepare_data(cls, upload_path, bucket_name, filename):
        post_data = {
            'referredEntities': {},
            'entity': {
                'typeName': 'nfs_file',
                'attributes': {
                    'owner': 'unittest',
                    'modifiedTime': 0,
                    'replicatedTo': None,
                    'userDescription': None,
                    'isFile': False,
                    'numberOfReplicas': 0,
                    'replicatedFrom': None,
                    'qualifiedName': upload_path + '/' + filename,
                    'displayName': None,
                    'description': None,
                    'extendedAttributes': None,
                    'nameServiceId': None,
                    'path': upload_path,
                    'posixPermissions': None,
                    'createTime': str(time.time())[0:10],
                    'fileSize': '57250225',
                    'clusterName': None,
                    'name': upload_path + '/' + filename,
                    'isSymlink': False,
                    'group': None,
                    'updateBy': 'test_no_auth',
                    'bucketName': bucket_name, # project code
                    'fileName': filename,
                    'generateID': 'undefined'
                },
                'isIncomplete': False,
                'status': 'ACTIVE',
                'createdBy': ConfigClass.ATLAS_ADMIN,
                'version': 0,
                'relationshipAttributes': {
                    'schema': [],
                    'inputToProcesses': [],
                    'meanings': [],
                    'outputFromProcesses': []
                },
                'customAttributes': {},
                'labels': []
            }
        }
        return post_data, upload_path + '/' + filename

    @classmethod
    def setUpClass(cls):
        cls.log = cls.test.log
        cls.app = cls.test.app
        try:
            file_name1 = 'test_file_1_' + str(time.time())[0:10]
            file_name2 = 'test_file_2_' + str(time.time())[0:10]
            cls.post_data_1, cls.path1 = cls.prepare_data(cls.upload_path, cls.bucket_name, file_name1)
            cls.post_data_2, cls.path2 = cls.prepare_data(cls.upload_path, cls.bucket_name, file_name2)
            cls.guid_1 = cls.test.create_entity(cls.post_data_1)
            cls.post_data_2['entity']['typeName'] = 'nfs_file_processed'
            cls.guid_2 = cls.test.create_entity(cls.post_data_2)
            cls.log.info(f'PREPARED FILE 1: {cls.path1}')
            cls.log.info(f'PREPARED FILE 2: {cls.path2}')
        except Exception as e:
            cls.log.error(f"FAILED SETUP TEST: {e}")
            raise unittest.SkipTest(f"Failed setup test {e}")

    @classmethod
    def tearDownClass(cls):
        cls.log.info("\n")
        cls.test.delete_entity(cls.guid_1)
        cls.test.delete_entity(cls.guid_2)

    def test_01_create_lineage(self):
        # LineageAction, '/v1/lineage'
        testing_api = '/v1/lineage'
        self.log.info("\n")
        self.log.info(f"01 Test create_lineage".center(80,'-'))
        payload = {'inputFullPath': self.path1,
                   'outputFullPath': self.path2,
                   'projectCode': self.bucket_name,
                   'pipelineName': 'test_pipeline',
                   'description': '',
                   }
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST PAYLOAD: {payload}")
        update_attr = {}
        try:
            res = self.app.post(testing_api, json=payload)
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.assertEqual(res.status_code, 200)
            self.log.info(f"RESPONSE JSON: {res.json}")
            result = res.json['result']['mutatedEntities']
            create_type = result['CREATE'][0]['typeName']
            self.log.info(f"CHECK CREATE TYPE: {create_type}")
            # Comparing items in CREATE
            self.assertEqual(create_type, 'Process')
            create_attr = result['CREATE'][0]['attributes']
            qualified_name = create_attr['qualifiedName']
            name = create_attr['name']
            substring_pipeline = f"{self.bucket_name}:{payload['pipelineName']}"
            substring_direction = f"{self.path1.split('/')[2]}:to:{self.path2.split('/')[2]}"
            self.log.info(f"COMPARING qualifiedName 1st part: {substring_pipeline} VS {qualified_name[0:len(substring_pipeline)]}")
            self.log.info(f"COMPARING qualifiedName 2nd part: {substring_direction} VS {qualified_name[-(len(substring_direction))::]}")
            self.assertEqual(substring_pipeline, qualified_name[0:len(substring_pipeline)])
            self.assertEqual(substring_direction, qualified_name[-(len(substring_direction))::])
            self.log.info(f"COMPARING name 1st part: {substring_pipeline} VS {name[0:len(substring_pipeline)]}")
            self.log.info(f"COMPARING name 2nd part: {substring_direction} VS {name[-(len(substring_direction))::]}")
            self.assertEqual(substring_pipeline, name[0:len(substring_pipeline)])
            self.assertEqual(substring_direction, name[-(len(substring_direction))::])
            # Comparing items in UPDATE
            update_type = result['UPDATE'][0]['typeName']
            self.log.info(f"CHECK UPDATE TYPE: {update_type}")
            update_attr = result['UPDATE'][0]['attributes']
            self.log.info(f"COMPARING owner: {update_attr['owner']} VS {self.post_data_1['entity']['attributes']['owner']}")
            self.assertEqual(update_attr['owner'], self.post_data_1['entity']['attributes']['owner'])
            self.log.info(f"COMPARING qualifiedName: {update_attr['qualifiedName']} VS {self.path1}")
            self.assertEqual(update_attr['qualifiedName'], self.path1)
            self.log.info(f"COMPARING name: {update_attr['name']} VS {self.path1}")
            self.assertEqual(update_attr['name'], self.path1)
        except AssertionError:
            self.log.info(f"COMPARING owner: {update_attr['owner']} VS {self.post_data_2['entity']['attributes']['owner']}")
            self.assertEqual(update_attr['owner'], self.post_data_2['entity']['attributes']['owner'])
            self.log.info(f"COMPARING qualifiedName: {update_attr['qualifiedName']} VS {self.path2}")
            self.assertEqual(update_attr['qualifiedName'], self.path2)
            self.log.info(f"COMPARING name: {update_attr['name']} VS {self.path2}")
            self.assertEqual(update_attr['name'], self.path2)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_02_create_lineage_with_same_path(self):
        # LineageAction, '/v1/lineage'
        testing_api = '/v1/lineage'
        self.log.info("\n")
        self.log.info(f"02 Test create_lineage_with_same_path".center(80,'-'))
        payload = {'inputFullPath': self.path1,
                   'outputFullPath': self.path1,
                   'projectCode': self.bucket_name,
                   'pipelineName': 'test_pipeline',
                   'description': '',
                   }
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST PAYLOAD: {payload}")
        try:
            res = self.app.post(testing_api, json=payload)
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.log.info(f"COMPARING: {res.status_code} VS {403}")
            self.assertEqual(res.status_code, 403)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_03_create_lineage_without_output_path(self):
        # LineageAction, '/v1/lineage'
        testing_api = '/v1/lineage'
        self.log.info("\n")
        self.log.info(f"03 Test create_lineage_without_output_path".center(80,'-'))
        payload = {'inputFullPath': self.path1,
                   'projectCode': self.bucket_name,
                   'pipelineName': 'test_pipeline',
                   'description': '',
                   }
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST PAYLOAD: {payload}")
        try:
            res = self.app.post(testing_api, json=payload)
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.assertEqual(res.status_code, 400)
            self.assertIn(b'Invalid post', res.data)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_04_create_lineage_without_pipeline(self):
        # LineageAction, '/v1/lineage'
        testing_api = '/v1/lineage'
        self.log.info("\n")
        self.log.info(f"04.1 Test create_lineage_without_pipeline".center(80,'-'))
        payload = {'inputFullPath': self.path1,
                   'outputFullPath': self.path2,
                   'projectCode': self.bucket_name,
                   'description': '',
                   }
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST PAYLOAD: {payload}")
        try:
            res = self.app.post(testing_api, json=payload)
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.assertEqual(res.status_code, 400)
            self.assertIn(b'Invalid post', res.data)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_05_create_lineage_without_project_code(self):
        # LineageAction, '/v1/lineage'
        testing_api = '/v1/lineage'
        self.log.info("\n")
        self.log.info(f"05 Test create_lineage_without_project_code".center(80,'-'))
        payload = {'inputFullPath': self.path1,
                   'outputFullPath': self.path2,
                   'description': '',
                   }
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST PAYLOAD: {payload}")
        try:
            res = self.app.post(testing_api, json=payload)
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.assertEqual(res.status_code, 400)
            self.assertIn(b'Invalid post', res.data)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_06_create_lineage_with_description(self):
        # LineageAction, '/v1/lineage'
        testing_api = '/v1/lineage'
        self.log.info("\n")
        self.log.info(f"06 Test create_lineage_with_description".center(80,'-'))
        # Add a description longer with length 300
        random_description = "i6lX3W6im3xMMMBCA18iPULY9jnA2RCU8EdNRlJWHgSritjNCp37FkFmBpVZa5IJkTyxbLVCZucSwuCwBRk2joEebrDYwk2HxnL0zJlUXLz5pgE4FcB86wRCZUXZn8DgkqIzmwFh4vDEt8Epge4h8lhAWM008Y1nOWXotvooH3OKoxA7rGemdM0uBoX8SzBG0UcPqCCkKm232dRtd2qyRdGUeEjmsURlbzldIhrI3GHjQ6f6KxG0sQ0P6I0UA1GAnRoz8RzDrcSLxCwjW1U4dDVnSaJGfCOImMQtbUi0FoSc"
        payload = {'inputFullPath': self.path1,
                   'outputFullPath': self.path2,
                   'projectCode': self.bucket_name,
                   'pipelineName': 'test_pipeline',
                   'description': random_description,
                   }
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST PAYLOAD: {payload}")
        try:
            res = self.app.post(testing_api, json=payload)
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.assertEqual(res.status_code, 200)
            self.log.info(f"RESPONSE JSON: {res.json}")
            description = res.json['result']['mutatedEntities']['CREATE'][0]['attributes']['description']
            self.log.info(f"COMPARING: {description} VS {payload['description']}")
            self.assertEqual(description, payload['description'])
        except Exception as e:
            self.log.error(e)
            raise e

    def test_07_get_lineage_raw(self):
        # LineageAction, '/v1/lineage'
        testing_api = '/v1/lineage'
        self.log.info("\n")
        self.log.info(f"07 Test get_lineage_raw".center(80,'-'))
        params = {'full_path': self.path1,
                  'type_name': 'nfs_file',
                  'direction': 'INPUT'}
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST PAYLOAD: {params}")
        try:
            res = self.app.get(testing_api, query_string=params)
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.log.info(f"POST JSON: {res.json}")
            self.assertEqual(res.status_code, 200)
            self.log.info(f"{self.guid_1}, {res.json['result']['baseEntityGuid']}")
            self.assertEqual(self.guid_1, res.json['result']['baseEntityGuid'])
            self.log.info(f"COMPARING DIRECTION: INPUT, {res.json['result']['lineageDirection']}")
            self.assertEqual('INPUT', res.json['result']['lineageDirection'])
        except Exception as e:
            self.log.error(e)
            raise e

    def test_08_get_lineage_processed(self):
        # LineageAction, '/v1/lineage'
        testing_api = '/v1/lineage'
        self.log.info("\n")
        self.log.info(f"08 Test get_lineage_processed".center(80,'-'))
        params = {'full_path': self.path2,
                  'type_name': 'nfs_file_processed',
                  'direction': 'INPUT'}
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST PAYLOAD: {params}")
        try:
            res = self.app.get(testing_api, query_string=params)
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.log.info(f"POST JSON: {res.json}")
            self.assertEqual(res.status_code, 200)
            self.log.info(f"{self.guid_2}, {res.json['result']['baseEntityGuid']}")
            self.assertEqual(self.guid_2, res.json['result']['baseEntityGuid'])
            self.log.info(f"COMPARING DIRECTION: INPUT, {res.json['result']['lineageDirection']}")
            self.assertEqual('INPUT', res.json['result']['lineageDirection'])
        except Exception as e:
            self.log.error(e)
            raise e

    def test_09_get_lineage_both_direction(self):
        # LineageAction, '/v1/lineage'
        testing_api = '/v1/lineage'
        self.log.info("\n")
        self.log.info(f"09 Test get_lineage_both_direction".center(80,'-'))
        params = {'full_path': self.path1,
                  'type_name': 'nfs_file',
                  'direction': 'BOTH'}
        try:
            res = self.app.get(testing_api, query_string=params)
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.log.info(f"POST JSON: {res.json}")
            self.assertEqual(res.status_code, 200)
            self.log.info(f"COMPARING guid: {self.guid_1}, {res.json['result']['baseEntityGuid']}")
            self.assertEqual(self.guid_1, res.json['result']['baseEntityGuid'])
            self.log.info(f"COMPARING DIRECTION: BOTH, {res.json['result']['lineageDirection']}")
            self.assertEqual('BOTH', res.json['result']['lineageDirection'])
        except Exception as e:
            self.log.error(e)
            raise e

    def test_10_get_lineage_output_direction(self):
        # LineageAction, '/v1/lineage'
        testing_api = '/v1/lineage'
        self.log.info("\n")
        self.log.info(f"10 Test get_lineage_output_direction".center(80,'-'))
        params = {'full_path': self.path1,
                  'type_name': 'nfs_file',
                  'direction': 'OUTPUT'}
        try:
            res = self.app.get(testing_api, query_string=params)
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.log.info(f"POST JSON: {res.json}")
            self.assertEqual(res.status_code, 200)
            self.log.info(f"COMPARING guid: {self.guid_1}, {res.json['result']['baseEntityGuid']}")
            self.assertEqual(self.guid_1, res.json['result']['baseEntityGuid'])
            self.log.info(f"COMPARING DIRECTION: OUTPUT, {res.json['result']['lineageDirection']}")
            self.assertEqual('OUTPUT', res.json['result']['lineageDirection'])
        except Exception as e:
            self.log.error(e)
            raise e

