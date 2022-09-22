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
import copy

class EAPIResponseCode(Enum):
    success = 200
    internal_error = 500
    bad_request = 400
    not_found = 404
    forbidden = 403
    conflict = 409
    accepted = 202
    

class APIResponse:
    def __init__(self):
        self._attribute_map = {
            'code': EAPIResponseCode.success.value, ## by default success
            'error_msg': '', ## empty when success
            'result': '',
            'page': 1, ## optional
            'total': 1, ## optional
            'num_of_pages': 1, ## optional
        }
    @property
    def to_dict(self):
        return self._attribute_map
    @property
    def code(self):
        return self._attribute_map['code']
    @property
    def error_msg(self):
        return self._attribute_map['code']
    @property
    def result(self):
        return self._attribute_map['result']
    @property
    def page(self):
        return self._attribute_map['page']
    @property
    def total(self):
        return self._attribute_map['total']
    @property
    def num_of_pages(self):
        return self._attribute_map['num_of_pages']
    def set_code(self, code: EAPIResponseCode):
        self._attribute_map['code'] = code.value
    def set_error_msg(self, error_msg: str):
        self._attribute_map['error_msg'] = error_msg
    def set_result(self, result):
        self._attribute_map['result'] = result
    def set_page(self, page_current: int):
        self._attribute_map['page'] = page_current
    def set_total(self, total_rows: int):
        self._attribute_map['total'] = total_rows
    def set_num_of_pages(self, num_of_pages: int):
        self._attribute_map['num_of_pages'] = num_of_pages
