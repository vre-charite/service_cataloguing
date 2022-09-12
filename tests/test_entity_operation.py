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

import unittest
import time
from config import ConfigClass
from tests.logger import Logger
from tests.prepare_tests import SetUpTest, test_client
from datetime import datetime, timedelta

class TestEntityOperation(unittest.TestCase):

    log = Logger(name='test_entity_operation.log')
    test = SetUpTest(log, test_client)
    upload_path = '/test_folder'
    bucket_name = 'test_bucket'
    file_name = 'test_file' + str(time.time())[0:10]
    today_date = datetime.now().date()
    today_datetime = datetime.combine(today_date, datetime.min.time())
    start_date = int(today_datetime.timestamp())

    end_datetime = datetime.combine(
        today_date + timedelta(days=1), datetime.min.time())
    end_date = int(end_datetime.timestamp())
    criterion = [
        {
            'attributeName': 'bucketName',
            'attributeValue': upload_path,
            'operator': 'eq'
        },
        {
            'attributeName': 'createTime',
            'attributeValue': int(start_date),
            'operator': 'gte'
        },
        {
            'attributeName': 'createTime',
            'attributeValue': int(end_date),
            'operator': 'lte'
        }
    ]
    guid = None
    stamp = str(time.time())[0:10]

    @classmethod
    def prepare_data(cls, upload_path, bucket_name, file_name, type_name='nfs_file'):
        post_data = {
            'referredEntities': {},
            'entity': {
                'typeName': type_name,
                'attributes': {
                    'owner': 'unittest',
                    'modifiedTime': 0,
                    'replicatedTo': None,
                    'userDescription': None,
                    'isFile': False,
                    'numberOfReplicas': 0,
                    'replicatedFrom': None,
                    'qualifiedName': upload_path + '/' + file_name,
                    'displayName': None,
                    'description': None,
                    'extendedAttributes': None,
                    'nameServiceId': None,
                    'path': upload_path,
                    'posixPermissions': None,
                    'createTime': cls.stamp,
                    'fileSize': '57250225',
                    'clusterName': None,
                    'name': upload_path + '/' + file_name,
                    'isSymlink': False,
                    'group': None,
                    'updateBy': 'test_no_auth',
                    'bucketName': bucket_name, # project code
                    'fileName': file_name,
                },
                'isIncomplete': False,
                'status': 'ACTIVE',
                'createdBy': "admin",
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
        return post_data

    @classmethod
    def setUpClass(cls):
        cls.log = cls.test.log
        cls.app = cls.test.app
        try:
            cls.post_data = cls.prepare_data(cls.upload_path,
                                             cls.bucket_name,
                                             cls.file_name)
            cls.guid = cls.test.create_entity(cls.post_data)
        except Exception as e:
            cls.log.error(f"FAILED SETUP TEST: {e}")
            raise unittest.SkipTest(f"Failed setup test {e}")

    @classmethod
    def tearDownClass(cls):
        cls.log.info("\n")
        cls.test.delete_entity(cls.guid)

    def test_01_create_entity(self):
        self.log.info("\n")
        self.log.info(f"01 Test create_entity".center(80, '-'))
        testing_api = "/v1/entity"
        filename = self.file_name + self.stamp
        post_data = self.prepare_data(self.upload_path, self.bucket_name, filename)
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST DATA: {post_data}")
        try:
            res = self.app.post(testing_api, json=post_data)
            self.log.info(f"RESPONSE DATA: {res.data}")
            self.log.info(F"RESPONSE STATUS: {res.status_code}")
            self.assertEqual(res.status_code, 200)
            guid_res = res.json['result']
            guid_res = guid_res['mutatedEntities']['CREATE']
            guid = guid_res[0]['guid']
            self.log.info(f"CHECK guid exist: {guid}")
            self.assertIsNotNone(guid)
            self.log.info(f"CHECK guid LENGTH: {len(guid)} VS {len(self.guid)}")
            self.assertEqual(len(guid), len(self.guid))
            self.test.delete_entity(guid)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_02_create_entity_without_filename(self):
        self.log.info("\n")
        self.log.info(f"02 Test create_entity_without_filename".center(80, '-'))
        testing_api = "/v1/entity"
        post_data = self.prepare_data(self.upload_path, self.bucket_name, "")
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST DATA: {post_data}")
        try:
            res = self.app.post(testing_api, json=post_data)
            self.log.info(f"RESPONSE DATA: {res.data}")
            self.log.info(F"RESPONSE STATUS: {res.status_code}")
            self.assertEqual(res.status_code, 200)
            guid_res = res.json['result']
            guid_res = guid_res['mutatedEntities']['CREATE']
            guid = guid_res[0]['guid']
            self.log.info(f"CHECK guid exist: {guid}")
            self.assertIsNotNone(guid)
            self.log.info(f"CHECK guid LENGTH: {len(guid)} VS {len(self.guid)}")
            self.assertEqual(len(guid), len(self.guid))
            self.test.delete_entity(guid)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_03_create_entity_without_type(self):
        self.log.info("\n")
        self.log.info(f"03 Test create_entity_without_type".center(80, '-'))
        testing_api = "/v1/entity"
        file = self.file_name + self.stamp
        post_data = self.prepare_data(self.upload_path, self.bucket_name, file, 'sometype')
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST DATA: {post_data}")
        try:
            res = self.app.post(testing_api, json=post_data)
            self.log.info(f"RESPONSE DATA: {res.data}")
            self.log.info(F"RESPONSE STATUS: {res.status_code}")
            self.assertEqual(res.status_code, 400)
            self.assertIn(b'Type ENTITY with name sometype does not exist', res.data)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_04_get_entity_by_guid(self):
        # EntityActionByGuid, '/v1/entity/guid/<guid>'
        self.log.info("\n")
        self.log.info(f"04 Test get_entity_by_guid".center(80, '-'))
        testing_api = '/v1/entity/guid/%s' % str(self.guid)
        self.log.info(f"POST API: {testing_api}")
        try:
            res = self.app.get(testing_api)
            self.log.info(f"GET GUID: {self.guid}")
            self.log.info(f"GET STATUS: {res.status_code}")
            self.log.info(f"GET RESPONSE: {res.data}")
            self.assertEqual(res.status_code, 200)

            actual_result = res.json['result']
            actual_entity = actual_result['entity']
            actual_attributes = actual_entity['attributes']
            actual_relations = actual_entity['relationshipAttributes']

            expected_result = self.post_data
            expected_entity = expected_result['entity']
            expected_attributes = expected_entity['attributes']
            expected_relations = expected_entity['relationshipAttributes']

            for entity in expected_result:
                # compare other fields such as referredEntities
                if entity not in ['entity', 'attributes', 'relationshipAttributes']:
                    self.log.info(f"COMPARING ENTITY: {entity}")
                    self.assertEqual(actual_result[entity], expected_result[entity])
                # compare fields in entity
                elif entity == 'entity':
                    self.log.info(f"COMPARING ENTITY: {entity}")
                    for e in actual_entity:
                        # compare attributes entity
                        if e == 'attributes':
                            for attr in actual_attributes:
                                if attr not in ['raw', 'pipeline', 'processed']:
                                    self.assertEqual(str(actual_attributes[attr]),
                                                     str(expected_attributes[attr]))
                        # compare relationshipAttributes entity
                        elif e == 'relationshipAttributes':
                            for r in actual_relations:
                                if r not in ['raw', 'processed']:
                                    self.assertEqual(actual_relations[r], expected_relations[r])
                        # compare rest entities that not just in response
                        elif e not in ['guid', 'updatedBy', 'updateTime', 'createTime']:
                            self.assertEqual(actual_entity[e], expected_entity[e])
        except Exception as e:
            self.log.error(e)
            raise e

    def test_05_get_entity_by_not_exist_guid(self):
        # EntityActionByGuid, '/v1/entity/guid/<guid>'
        self.log.info("\n")
        self.log.info(f"05 Test get_entity_by_not_exist_guid".center(80, '-'))
        testing_api = '/v1/entity/guid/%s' % str('test')
        self.log.info(f"POST API: {testing_api}")
        try:
            res = self.app.get(testing_api)
            self.log.info(f"GET STATUS: {res.status_code}")
            self.log.info(f"GET RESPONSE: {res.data}")
            self.log.info(f"COMPARING: {res.status_code} VS {404}")
            self.assertEqual(res.status_code, 404)
            self.log.info(f"CHECK RESPONSE: {b'Given instance guid test is invalid/not found'} IN {res.data}")
            self.assertIn(b'Given instance guid test is invalid/not found', res.data)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_06_get_entity_by_empty_guid(self):
        # EntityActionByGuid, '/v1/entity/guid/<guid>'
        self.log.info("\n")
        self.log.info(f"06 Test get_entity_by_empty_guid".center(80, '-'))
        testing_api = '/v1/entity/guid/%s' % str('test')
        self.log.info(f"POST API: {testing_api}")
        try:
            res = self.app.get(testing_api)
            self.log.info(f"GET STATUS: {res.status_code}")
            self.log.info(f"GET RESPONSE: {res.data}")
            self.log.info(f"COMPARING: {res.status_code} VS {404}")
            self.assertEqual(res.status_code, 404)
            self.log.info(f"CHECK RESPONSE: {b'Given instance guid test is invalid/not found'} IN {res.data}")
            self.assertIn(b'Given instance guid test is invalid/not found', res.data)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_07_update_tag_with_space(self):
        # EntityTagByGuid, '/v1/entity/guid/<guid>/labels'
        self.log.info("\n")
        self.log.info(f"07 Test update_tag_with_space".center(80, '-'))
        testing_api = '/v1/entity/guid/%s/labels' % str(self.guid)
        payload = {'labels': ['test label']}
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST PAYLOAD: {payload}")
        try:
            res = self.app.post(testing_api, json=payload)
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.assertEqual(res.status_code, 403)
            self.assertIn(b"Invalid label: test label, label should contain alphanumeric characters, _ or -", res.data)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_08_update_tag_without_space(self):
        # EntityTagByGuid, '/v1/entity/guid/<guid>/labels'
        self.log.info("\n")
        self.log.info(f"08 Test update_tag".center(80, '-'))
        testing_api = '/v1/entity/guid/%s/labels' % str(self.guid)
        payload = {'labels': ['test_label']}
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST PAYLOAD: {payload}")
        try:
            res = self.app.post(testing_api, json=payload)
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"success", res.data)

            get_entity_api = '/v1/entity/guid/%s' % str(self.guid)
            get_res = self.app.get(get_entity_api)
            self.log.info(f"GET GUID: {get_res.data}")
            get_res = get_res.json
            labels = get_res['result']['entity']['labels']
            self.log.info(f"COMPARING CURRENT LABELS: {payload['labels']} VS {labels}")
            self.assertEqual(labels, payload['labels'])
            self.log.info("RESET TAG")
            reset = self.app.post(testing_api, json={'labels': []})
            self.assertEqual(res.status_code, 200)
            self.log.info(f"RESET RESULT: {reset.data}")
        except Exception as e:
            self.log.error(e)
            raise e

    def test_09_update_long_tag(self):
        # EntityTagByGuid, '/v1/entity/guid/<guid>/labels'
        self.log.info("\n")
        self.log.info(f"09 Test update_long_tag".center(80, '-'))
        testing_api = '/v1/entity/guid/%s/labels' % str(self.guid)
        # magic number for tag length is 51
        payload = {'labels': ['LoremspaceIpsumspaceisspacesimplyspacedummyspacetex']}
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST PAYLOAD TAG LENGTH {len(payload['labels'][0])}: {payload}")
        try:
            res = self.app.post(testing_api, json=payload)
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.assertEqual(res.status_code, 403)
            self.assertIn(b"label size should not be greater than 50", res.data)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_10_update_tag_with_characters(self):
        # EntityTagByGuid, '/v1/entity/guid/<guid>/labels'
        self.log.info("\n")
        self.log.info(f"10 Test update_tag_with_characters".center(80, '-'))
        testing_api = '/v1/entity/guid/%s/labels' % str(self.guid)
        payload = {'labels': ['!@#$%']}
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST PAYLOAD TAG LENGTH {len(payload['labels'][0])}: {payload}")
        try:
            res = self.app.post(testing_api, json=payload)
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.assertEqual(res.status_code, 403)
            self.assertIn(b"label should contain alphanumeric characters, _ or -", res.data)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_11_update_tag_without_labels(self):
        # EntityTagByGuid, '/v1/entity/guid/<guid>/labels'
        self.log.info("\n")
        self.log.info(f"11 Test update_tag_without_labels".center(80, '-'))
        testing_api = '/v1/entity/guid/%s/labels' % str(self.guid)
        payload = {}
        self.log.info(f"POST API: {testing_api}")
        try:
            res = self.app.post(testing_api, json=payload)
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.assertEqual(res.status_code, 403)
            self.assertIn(b"labels is required", res.data)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_12_update_tag_with_string_labels(self):
        # EntityTagByGuid, '/v1/entity/guid/<guid>/labels'
        self.log.info("\n")
        self.log.info(f"12 Test update_tag_with_string_labels".center(80, '-'))
        testing_api = '/v1/entity/guid/%s/labels' % str(self.guid)
        payload = {'labels': 'test_labels'}
        self.log.info(f"POST API: {testing_api}")
        try:
            res = self.app.post(testing_api, json=payload)
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.assertEqual(res.status_code, 403)
            self.assertIn(b"labels is required", res.data)
        except Exception as e:
            self.log.error(e)
            raise e

    """
    def test_13_use_imbedded_sql_query(self):
        # EntityQueryDSL, '/v1/entity/dsl'
        self.log.info("\n")
        self.log.info(f"13 Test use_imbedded_sql_query".center(80, '-'))
        testing_api = '/v1/entity/dsl'
        self.log.info(f"GET API: {testing_api}")
        res = self.app.get(testing_api)
        self.log.info(f"GET STATUS: {res.status_code}")
        self.log.info(f"GET RESPONSE: {res.data}")
    """

    def test_14_get_list_of_entities_by_query_daily_count(self):
        # EntityQueryBasic, '/v1/entity/basic'
        self.log.info("\n")
        self.log.info(f"14 Test get_list_of_entities_by_query_daily_count".center(80, '-'))
        page = 0
        page_size = 10
        # data ops usage in dailyFileCount, '/containers/<container_id>/files/count/daily'
        post_data = {
            'excludeDeletedEntities': True,
            'includeSubClassifications': False,
            'includeSubTypes': False,
            'includeClassificationAttributes': False,
            'entityFilters': {
                "condition": "AND",
                "criterion": self.criterion
            },
            'tagFilters': None,
            'attributes': ['owner', 'downloader', 'fileName'],
            'limit': 10,
            'offset': str(int(page) * int(page_size)),
            'sortBy': 'createTime',
            'sortOrder': 'DESCENDING',
            'typeName': 'nfs_file',
            'classification': None,
            'termName': None
        }
        compare = {'eq': '=', 'gte': '>=', 'lte':'<='}
        testing_api = '/v1/entity/basic'
        self.log.info(f"POST API: {testing_api}")
        try:
            res = self.app.post(testing_api, json=post_data, headers={'content-type': 'application/json'})
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.log.info(f"COMPARINTG: {res.status_code} VS {200}")
            self.assertEqual(res.status_code, 200)
            res = res.json
            self.log.info(f"RESPONSE JOSN: {res}")
            result = res["result"]["searchParameters"]
            self.assertEqual(result['typeName'], self.post_data['entity']['typeName'])
            for r in result:
                self.log.info(f"COMPARING {r}: {result[r]} VS {post_data[r]}")
                if r == 'entityFilters':
                    self.assertEqual(result[r]['condition'], post_data['entityFilters']['condition'])
                    new_criterion = result[r]['criterion']
                    for n in range(len(new_criterion)):
                        self.assertEqual(self.criterion[n]['attributeName'], new_criterion[n]['attributeName'])
                        self.assertEqual(str(self.criterion[n]['attributeValue']), new_criterion[n]['attributeValue'])
                        self.assertEqual(compare[self.criterion[n]['operator']], new_criterion[n]['operator'])
                else:
                    if isinstance(result[r], list):
                        self.assertEqual(set(result[r]), set(post_data[r]))
                    else:
                        self.assertEqual(str(result[r]), str(post_data[r]))
        except Exception as e:
            self.log.error(e)
            raise e

    def test_15_get_list_of_entities_by_query_download_log_desc(self):
        # EntityQueryBasic, '/v1/entity/basic'
        self.log.info("\n")
        self.log.info(f"15 Test get_list_of_entities_by_query_download_log_desc".center(80, '-'))
        page = 0
        page_size = 10
        sorting = 'createTime'
        order = 'DESCENDING'
        entity_type = 'nfs_file'
        # data ops usage file_download_log, '/files/download/log'
        post_data = {
            'excludeDeletedEntities': True,
            'includeSubClassifications': False,
            'includeSubTypes': False,
            'includeClassificationAttributes': False,
            'tagFilters': None,
            'attributes': ['bucketName', 'fileName', 'downloader'],
            'limit': page_size,
            'offset': page * page_size,
            'sortBy': sorting,
            'sortOrder': order,
            'typeName': entity_type,
            'classification': None,
            'termName': None
        }
        testing_api = '/v1/entity/basic'
        self.log.info(f"POST API: {testing_api}")
        try:
            res = self.app.post(testing_api, json=post_data, headers={'content-type': 'application/json'})
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.log.info(f"COMPARINTG: {res.status_code} VS {200}")
            self.assertEqual(res.status_code, 200)
            res = res.json
            self.log.info(f"RESPONSE JOSN: {res}")
            result = res["result"]["searchParameters"]
            self.assertEqual(result['typeName'], self.post_data['entity']['typeName'])
            for r in result:
                self.log.info(f"COMPARING {r}: {result[r]} VS {post_data[r]}")
                if isinstance(result[r], list):
                    self.assertEqual(set(result[r]), set(post_data[r]))
                else:
                    self.assertEqual(str(result[r]), str(post_data[r]))
        except Exception as e:
            self.log.error(e)
            raise e

    def test_16_get_list_of_entities_by_query_download_log_asc(self):
        # EntityQueryBasic, '/v1/entity/basic'
        self.log.info("\n")
        self.log.info(f"16 Test get_list_of_entities_by_query_download_log_asc".center(80, '-'))
        page = 0
        page_size = 10
        sorting = 'createTime'
        order = 'ASCENDING'
        entity_type = 'nfs_file'
        # data ops usage file_download_log, '/files/download/log'
        post_data = {
            'excludeDeletedEntities': True,
            'includeSubClassifications': False,
            'includeSubTypes': False,
            'includeClassificationAttributes': False,
            'tagFilters': None,
            'attributes': ['bucketName', 'fileName', 'downloader'],
            'limit': page_size,
            'offset': page * page_size,
            'sortBy': sorting,
            'sortOrder': order,
            'typeName': entity_type,
            'classification': None,
            'termName': None
        }
        testing_api = '/v1/entity/basic'
        self.log.info(f"POST API: {testing_api}")
        try:
            res = self.app.post(testing_api, json=post_data, headers={'content-type': 'application/json'})
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.log.info(f"COMPARINTG: {res.status_code} VS {200}")
            self.assertEqual(res.status_code, 200)
            res = res.json
            self.log.info(f"RESPONSE JOSN: {res}")
            result = res["result"]["searchParameters"]
            self.assertEqual(result['typeName'], self.post_data['entity']['typeName'])
            for r in result:
                self.log.info(f"COMPARING {r}: {result[r]} VS {post_data[r]}")
                if isinstance(result[r], list):
                    self.assertEqual(set(result[r]), set(post_data[r]))
                else:
                    self.assertEqual(str(result[r]), str(post_data[r]))
        except Exception as e:
            self.log.error(e)
            raise e

    def test_17_get_list_of_entities_by_query_file_meta(self):
        # EntityQueryBasic, '/v1/entity/basic'
        self.log.info("\n")
        self.log.info(f"17 Test get_list_of_entities_by_query_file_meta".center(80, '-'))
        page = 0
        page_size = 10
        sorting = 'createTime'
        order = 'DESCENDING'
        entity_type = 'nfs_file'
        # data ops usage in FileMetaRestful, '/containers/<container_id>/files/meta'
        post_data = {
            'excludeDeletedEntities': True,
            'includeSubClassifications': False,
            'includeSubTypes': False,
            'includeClassificationAttributes': False,
            'entityFilters': {
                "condition": "AND",
                "criterion": self.criterion
            },
            'tagFilters': None,
            'attributes': ['fileName', 'fileSize', 'path'],
            'limit': page_size,
            'offset': page * page_size,
            'sortBy': sorting,
            'sortOrder': order,
            'typeName': entity_type,
            'classification': None,
            'termName': None
        }
        compare = {'eq': '=', 'gte': '>=', 'lte':'<='}
        testing_api = '/v1/entity/basic'
        self.log.info(f"POST API: {testing_api}")
        try:
            res = self.app.post(testing_api, json=post_data, headers={'content-type': 'application/json'})
            self.log.info(f"POST STATUS: {res.status_code}")
            self.log.info(f"POST RESPONSE: {res.data}")
            self.log.info(f"COMPARINTG: {res.status_code} VS {200}")
            self.assertEqual(res.status_code, 200)
            res = res.json
            self.log.info(f"RESPONSE JOSN: {res}")
            result = res["result"]["searchParameters"]
            self.assertEqual(result['typeName'], self.post_data['entity']['typeName'])
            for r in result:
                self.log.info(f"COMPARING {r}: {result[r]} VS {post_data[r]}")
                if r == 'entityFilters':
                    self.assertEqual(result[r]['condition'], post_data['entityFilters']['condition'])
                    new_criterion = result[r]['criterion']
                    for n in range(len(new_criterion)):
                        self.assertEqual(self.criterion[n]['attributeName'], new_criterion[n]['attributeName'])
                        self.assertEqual(str(self.criterion[n]['attributeValue']), new_criterion[n]['attributeValue'])
                        self.assertEqual(compare[self.criterion[n]['operator']], new_criterion[n]['operator'])
                else:
                    if isinstance(result[r], list):
                        self.assertEqual(set(result[r]), set(post_data[r]))
                    else:
                        self.assertEqual(str(result[r]), str(post_data[r]))
        except Exception as e:
            self.log.error(e)
            raise e

    def test_18_get_audit_log(self):
        """
        This API is not currently in use.
        If this API is using by any service, please update test case accordingly
        """
        # EntityQueryBasic, '/v1/entity/basic'
        self.log.info("\n")
        self.log.info(f"18 Test get_audit_log".center(80, '-'))
        testing_api = '/v1/entity/guid/%s/audit' % str(self.guid)
        params = {'count': 25}
        try:
            res = self.app.get(testing_api, query_string=params)
            self.log.info(f"GET STATUS: {res.status_code}")
            self.log.info(f"GET RESPONSE: {res.data}")
        except Exception as e:
            self.log.error(e)
            raise e




