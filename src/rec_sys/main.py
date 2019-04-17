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

import json
from flask import Flask,Response 
from rec_methods import methods
import json_logging, logging, sys

app = Flask(__name__)

json_logging.ENABLE_JSON_LOGGING = True
json_logging.init(framework_name='flask')
json_logging.init_request_instrument(app)

# init the logger as usual
logger = logging.getLogger("tng-vnv-dsm")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))



# Api Method for retrieve the user's recommendation        
@app.route('/tng-vnv-dsm/api/v1/users/<user>', methods=['GET'])
def user_recommend(user):    
    logger.info("/tng-vnv-dsm/api/v1/users/<user> Call")
    response = methods.get_recommendations(user)
    response_length = len(response)
    
    if response_length > 2:
        return Response(methods.get_recommendations(user),  mimetype='application/json')
    else:
        error_response = {'Response':'User Not Found'}  
        return Response(json.dumps(error_response), status=404,  mimetype='application/json')

# Api Method for retrieve the component's health
@app.route('/tng-vnv-dsm/api/v1/health', methods=['GET'])
def health():
    logger.info("/tng-vnv-dsm/api/v1/health Call")
    response= {'Status':'Alive!'}  
    return Response(json.dumps(response),  mimetype='application/json')

# Api Method for retrieve the tests tags the systems is trained for
@app.route('/tng-vnv-dsm/api/v1/test_items', methods=['GET'])
def tests():
    logger.info("/tng-vnv-dsm/api/v1/test_items Call")
    response_length = len(methods.get_items())
    if response_length > 0:
        return Response(json.dumps(methods.get_items()), status=200, mimetype='application/json')
    else:
        response= {'Response':'No test items currently available - Dataset Empty'}
        return Response(json.dumps(response), status=404, mimetype='application/json')		

# Api Method for retrieve the users the systems is trained for
@app.route('/tng-vnv-dsm/api/v1/users', methods=['GET'])
def users():
    logger.info("/tng-vnv-dsm/api/v1/users Call")
    response_length = len(methods.get_users())
    if response_length > 1:
        return Response(json.dumps(methods.get_users()), mimetype='application/json')
    else:
        response= {'Response':'No Users currently available - Dataset Empty'}
        return Response(json.dumps(response), status=404, mimetype='application/json')		   

# Api Method to add user-item pairs from a test descriptor
@app.route('/tng-vnv-dsm/api/v1/users/items/<package_uuid>', methods=['POST'])
def add_user_item(package_uuid):
    logger.info("/tng-vnv-dsm/api/v1/users/items/<package_uuid> Call")
    try:
        user_name = methods.get_username(package_uuid)
        if (user_name == None):
            user_name = "Evgenia"               
        test_descriptors_uuids = methods.get_testds_uuids(package_uuid)
        test_tags = methods.get_test_tags(test_descriptors_uuids)
        response =  methods.add_user_item(test_tags,user_name)
        logger.info("/tng-vnv-dsm/api/v1/users/items/<package_uuid> Call", extra={'props': {"Response": 'User - Item added succesfully'}})
        return Response(json.dumps(response), status=201,  mimetype='application/json')
    except Exception as e:
        error_response = {'Response':'An error Occurred'}
        logger.info("/tng-vnv-dsm/api/v1/users/items/<package_uuid> Call", extra={'props': {"Error": e}})
        return Response(json.dumps(error_response),  status=404,  mimetype='application/json')

# Api Method to delete a user and his'her assosiated items
@app.route('/tng-vnv-dsm/api/v1/users/<user>', methods=['DELETE'])
def del_user(user):
    logger.info("/tng-vnv-dsm/api/v1/users/<user> Call")
    return Response(json.dumps(methods.del_user(user)), mimetype='application/json')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4010, debug=True)

