## Copyright (c) 2015 SONATA-NFV, 2017 5GTANGO [, ANY ADDITIONAL AFFILIATION]
## ALL RIGHTS RESERVED.
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
## Neither the name of the SONATA-NFV, 5GTANGO [, ANY ADDITIONAL AFFILIATION]
## nor the names of its contributors may be used to endorse or promote
## products derived from this software without specific prior written
## permission.
##
## This work has been performed in the framework of the SONATA project,
## funded by the European Commission under Grant number 671517 through
## the Horizon 2020 and 5G-PPP programmes. The authors would like to
## acknowledge the contributions of their colleagues of the SONATA
## partner consortium (www.sonata-nfv.eu).
##
## This work has been performed in the framework of the 5GTANGO project,
## funded by the European Commission under Grant number 761493 through
## the Horizon 2020 and 5G-PPP programmes. The authors would like to
## acknowledge the contributions of their colleagues of the 5GTANGO
## partner consortium (www.5gtango.eu).

import functools, time, yaml, json
from flask import Response
from decsup.logger import TangoLogger as TangoLogger

LOG = TangoLogger.getLogger(__name__)


def catch_exception(f):
    @functools.wraps(f)
    def func(*args,**kwargs):
        try:
            return f(*args,**kwargs)
        except ValueError as e:
            print('Caught an exception in',f.__name__)

    return func

class InOutTransforms:

    def dict_generator(self, indict,pre=None):
        pre = pre[ : ] if pre else [ ]
        if isinstance(indict,dict):
            for key, value in indict.items():
                if isinstance(value,dict):
                    for d in self.dict_generator(value, [key]+pre):
                        yield d
                elif isinstance(value,list) or isinstance(value, tuple):
                    for v in value:
                        for d in self.dict_generator(v, [key]+pre):
                            yield d
                else:
                    yield pre+[key, value]
        else:
            yield indict

    @catch_exception
    def yaml_d(self, content):
        try:
            return yaml.duml(content)
        except ValueError as e:
            return self.generic_resp(400, "application/x-yaml", "InvalidArgument:" + str(e))

    @catch_exception
    def json_d(self, content):
        try:
            return json.dumps(content)
        except ValueError as e:
            return self.generic_resp(400, "application/json", "InvalidArgument:" + str(e))

    @catch_exception
    def yaml_l(self, content):
        try:
            return yaml.load(content)
        except ValueError as e:
            return self.generic_resp(400, "application/x-yaml", "InvalidArgument:" + str(e))

    @catch_exception
    def error_message(self, message):
         return {'Error': message}

    @catch_exception
    def success_message(self, message):
         return {'Success': message}

    @catch_exception
    def json_l(self, content):
        try:
            return json.loads(content)
        except ValueError as e:
            return self.generic_resp(400, "application/json", "InvalidArgument:" + str(e))

    def generic_resp(self, status, content_type, response):
        return Response(status = status,
                        content_type = content_type,
                        response = response)

    def transform_text(self, request):
        if request.content_type == "application/json":
            return self.json_l(request.data)
        elif request.content_type == "application/x-yaml":
            return self.yaml_l(request.data)
        else:
            return False
