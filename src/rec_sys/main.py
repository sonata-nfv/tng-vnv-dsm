# Copyright (c) 2015 SONATA-NFV, 2017 5GTANGO [, ANY ADDITIONAL AFFILIATION]
# ALL RIGHTS RESERVED.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Neither the name of the SONATA-NFV, 5GTANGO [, ANY ADDITIONAL AFFILIATION]
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
# This work has been performed in the framework of the SONATA project,
# funded by the European Commission under Grant number 671517 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the SONATA
# partner consortium (www.sonata-nfv.eu).
#
# This work has been performed in the framework of the 5GTANGO project,
# funded by the European Commission under Grant number 761493 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the 5GTANGO
# partner consortium (www.5gtango.eu).

import json
from flask import Flask, Response, Blueprint
from flask_restplus import Api, Resource
from rec_methods import methods
import json_logging, logging, sys

app = Flask(__name__)

blueprint = Blueprint('api', __name__, url_prefix='/tng-vnv-dsm/api/v1')
api = Api(blueprint, version="0.1",
          title='5GTANGO tng-vnv-dsm API',
          description="5GTANGO Decision Support Mechanism - Test Recommendation System.")
app.register_blueprint(blueprint)

json_logging.ENABLE_JSON_LOGGING = True
json_logging.init(framework_name='flask')
json_logging.init_request_instrument(app)

# init the logger as usual
logger = logging.getLogger("tng-vnv-dsm")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))


# Api Method for retrieve the component's health
@api.route('/health', methods=['GET'])
class DsmHealth(Resource):

    def get(self):
        response = {'Status': 'Alive'}
        return Response(json.dumps(response), mimetype='application/json')

# Api method to add a new pair based on what the user has selected
@api.route('/users/<user>/<item>', methods=['POST'])
class DsmUserItem(Resource):

    def post(self, user=None, item=None):
        test_tags = []
        test_tags.append(item)
        logger.info("/tng-vnv-dsm/api/v1/users/<user>/<item> Call")
        return Response(json.dumps(methods.add_user_item(test_tags, user)), mimetype='application/json')


# Api Method to add user-item pairs from a test descriptor
@api.route('/users/items/<package_uuid>', methods=['POST'])
class DsmAddUserItem(Resource):

    def post(self, package_uuid=None):
        logger.info("/tng-vnv-dsm/api/v1/users/items/<package_uuid> Call")
        try:
            user_name = methods.get_username(package_uuid)
            if (user_name == ""):
                user_name = "tango_user"
            # test_descriptors_uuids = methods.get_testds_uuids(package_uuid)
            test_tags = methods.get_testing_tags(package_uuid)
            response = methods.add_user_item(test_tags, user_name)
            logger.info("/tng-vnv-dsm/api/v1/users/items/<package_uuid> Call",
                        extra={'props': {"Response": 'User - Item added succesfully'}})
            return Response(json.dumps(response), status=201, mimetype='application/json')
        except Exception as e:
            error_response = {'Response': 'Package could not be found'}
            logger.info("/tng-vnv-dsm/api/v1/users/items/<package_uuid> Call", extra={'props': {"Error": e}})
            return Response(json.dumps(error_response), status=404, mimetype='application/json')


# Api Method for retrieve the tests tags the systems is trained for
@api.route('/test_items', methods=['GET'])
class DsmTestItems(Resource):

    def get(self):
        logger.info("/tng-vnv-dsm/api/v1/test_items Call")
        response_length = len(methods.get_items())
        if response_length > 0:
            return Response(json.dumps(methods.get_items()), status=200, mimetype='application/json')
        else:
            response = {'Response': 'No test items currently available - Dataset Empty'}
            return Response(json.dumps(response), status=404, mimetype='application/json')

# Api Method for retrieve the users the systems is trained for
@api.route('/users', methods=['GET'])
class DsmGetUsers(Resource):

    def get(self):
        logger.info("/tng-vnv-dsm/api/v1/users Call")
        response_length = len(methods.get_users())
        if response_length > 1:
            return Response(json.dumps(methods.get_users()), mimetype='application/json')
        else:
            response = {'Response': 'No Users currently available - Dataset Empty'}
            return Response(json.dumps(response), status=404, mimetype='application/json')


# Api Method for retrieve the user's recommendation
@api.route('/users/<user>', methods=['GET'])
class DsmRec(Resource):

    def get(self, user=None):
        logger.info("/tng-vnv-dsm/api/v1/users/<user> Call")
        return Response(methods.get_recommendations(user), mimetype='application/json')


# Api method to delete a user and all his/her associated items
@api.route('/users/delete/<user>', methods=['DELETE'])
class DsmDeleteUser(Resource):

    def delete(self, user=None):
        logger.info("/tng-vnv-dsm/api/v1/users/delete/<user> Call")
        return Response(json.dumps(methods.del_user(user)), mimetype='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4010, debug=True)
