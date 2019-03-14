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


import logging, os, yaml, json, errno, requests, functools, time
from logging.handlers import RotatingFileHandler
from flask import Flask, Blueprint, jsonify, request, Response,json, make_response
from decsup.inouttransforms import InOutTransforms as iotran
from flask_restplus import Api, Resource
from decsup.db_models.models import MongoDB as mongo
from decsup.word2vec import TrainModel as rec_mod
import pandas as pd
from decsup.logger import TangoLogger as TangoLogger




Trn_mod = mongo(collection='trained_model')
dict_db = mongo(collection='dict_users')

rec_mod = rec_mod()
ioObj = iotran()
train_bool = 0 # this needs to start with 0

app = Flask(__name__)
blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, version="0.1",
          title='5GTANGO tng-dec-sup API',
          description="5GTANGO tng-dec-sup REST API to recommendations.")
app.register_blueprint(blueprint)

# LOG = logging.getLogger('logger')
# LOG.setLevel(logging.DEBUG)
LOG = TangoLogger.getLogger(__name__)

def catch_exception(f):
    @functools.wraps(f)
    def func(*args,**kwargs):
        try:
            return f(*args,**kwargs)
        except ValueError as e:
            print('Caught an exception in',f.__name__)

    return func


@api.route('/tests/<user>/<test_id>', methods =['POST'])
class TangoDsm(Resource):

    def post(self, user=None, test_id=None):
        global train_bool
        start_time =time.time()
        LOG.info("Insertion of new selection of user {} with test {}".format(user, test_id),
                 extra={"start_stop": "START"})
        try:
            user_ins = dict_db.insert_user(user, test_id)
        except Exception as e:
            LOG.error(e, extra={"status": 400, "time_elapsed": "%.3f seconds" % (time.time() - start_time)})
            return ioObj.generic_resp(400, 'application/json', ioObj.json_d(ioObj.error_message(e)))
        train_bool = 1
        LOG.info("Insertion of new selection of user {x} with test {y}".format(x=user, y=test_id),
                  extra={ "status": 200, "time_elapsed": "%.3f seconds" % (time.time() - start_time)})
        return ioObj.generic_resp(200,'application/json',
                                  ioObj.json_d(ioObj.success_message("Stored user {x} with test {y}".format(x=user, y=test_id))))



@api.route('/users/<user>',methods=[ 'GET', 'DELETE' ])
class TangoDsmUsers(Resource):

    def get(self, user):
        global train_bool
        start_time = time.time()
        LOG.info("Recommendations of user {}".format(user),
                 extra={"start_stop": "START"})
        try:
            user_exists = dict_db.find_user_bool(user)
            if not user_exists:
                LOG.error("User {} not found".format(user)
                          ,extra={"status": 404,"time_elapsed": "%.3f seconds" % (time.time()-start_time)})
                return ioObj.generic_resp(404,'application/json',
                                   ioObj.json_d(
                                       ioObj.error_message("User {x} not found".format(x=user))))
        except Exception as e:
            LOG.error(e ,extra={"status": 500,"time_elapsed": "%.3f seconds" % (time.time()-start_time)})
            return ioObj.generic_resp(500,'application/json',
                                      ioObj.json_d(
                                          ioObj.error_message(e)))
        n = request.args.get('n',default=2,type=int)
        file = Trn_mod.get_model_metadata(rec_mod.filename)
        if train_bool == 1:
            LOG.debug("Predictions from recommendation engine with re-train")
            pd_users = pd.DataFrame.from_dict(dict_db.find_users())
            rec_mod.train_mod(pd_users, item_col='item', rating_col='rating', user_col='user')
            if Trn_mod.check_exist_model(rec_mod.filename):
                Trn_mod.find_delete_model(file['_id'])
                Trn_mod.find_delete_model_metadata(rec_mod.filename)
            predictions, results = rec_mod.get_user_pred(user_id=user, dataframe=pd_users, item_col='item', rating_col='rating', user_col='user', n=n)
            rec_mod.dump_model(predictions)
            model_id = Trn_mod.insert_grid(rec_mod.filename)
            Trn_mod.insert_model_metadata(model_id, rec_mod.filename)
            train_bool = 0
            LOG.info("Recommendations of user {} =".format(user) + str(ioObj.json_d(results)),
                     extra={"status": 200,"time_elapsed": "%.3f seconds" % (time.time()-start_time)})
            return ioObj.generic_resp(200, 'application/json', ioObj.json_d(ioObj.success_message(results)))
        else:
            LOG.debug("Predictions from same recommendation engine without re-train")
            Trn_mod.load_grid(file['_id'], rec_mod.filename)
            predictions, _ = rec_mod.load_model()
            results = rec_mod.get_user_pred_stable(user, predictions, n=n)
            LOG.info("Recommendations of user {} =".format(user) + str(ioObj.json_d(results)),
                     extra={"status": 200,"time_elapsed": "%.3f seconds" % (time.time()-start_time)})
            return ioObj.generic_resp(200, 'application/json', ioObj.json_d(ioObj.success_message(results)))

    def delete(self, user):
        start_time = time.time()
        try:
            new_dict, occurrences = dict_db.delete_user(delete_item=user, array='user')
            if occurrences == 0:
                LOG.error("User {} not found".format(user)
                          ,extra={"status": 404,"time_elapsed": "%.3f seconds" % (time.time()-start_time)})
                return ioObj.generic_resp(404,'application/json',
                                          ioObj.json_d(
                                              ioObj.error_message("User {x} not found".format(x=user))))
        except TypeError:
            LOG.error("User {} not found due to DB problem".format(user)
                      ,extra={"status": 404,"time_elapsed": "%.3f seconds" % (time.time()-start_time)})
            return ioObj.generic_resp(404,'application/json',
                                      ioObj.json_d(
                                          ioObj.error_message("User {x} not found due to DB problem".format(x=user))))

        dict_db.delete_dictuser()
        dict_db.insert_dictuser(new_dict)

        LOG.info("User {} deleted with {} occurrences".format(user,occurrences),
                 extra={"status": 200,"time_elapsed": "%.3f seconds" % (time.time()-start_time)})
        return ioObj.generic_resp(200,'application/json',
                                  ioObj.json_d(ioObj.success_message("User {} deleted with {} occurrences".format(user, occurrences))))


@api.route('/tests/<item_id>', methods=['DELETE'])
class TangoDsmTestsID(Resource):

    def delete(self, item_id):
        start_time = time.time()
        try:
            new_dict, occurrences = dict_db.delete_user(delete_item=item_id, array='item')
            if occurrences == 0:
                LOG.error("Item {} not found".format(item_id)
                          ,extra={"status": 404,"time_elapsed": "%.3f seconds" % (time.time()-start_time)})
                return ioObj.generic_resp(404,'application/json',
                                          ioObj.json_d(
                                              ioObj.error_message("Item {x} not found".format(x=item_id))))
        except TypeError as e:
            LOG.error("Item {} not found due to DB problem".format(item_id),
                      extra={"status": 404,"time_elapsed": "%.3f seconds" % (time.time()-start_time)})
            return ioObj.generic_resp(404, 'application/json',
                                      ioObj.json_d(
                                          ioObj.error_message("Item {x} not found due to DB problem".format(x=item_id))))
        dict_db.delete_dictuser()
        dict_db.insert_dictuser(new_dict)

        LOG.info("Item {} deleted with {} occurrences".format(item_id,occurrences),
                 extra={"status": 200,"time_elapsed": "%.3f seconds" % (time.time()-start_time)})
        return ioObj.generic_resp(200,'application/json',
                                  ioObj.json_d(ioObj.success_message(
                                      "Item {} deleted with {} occurrences".format(item_id,occurrences))))

@api.route('/tests', methods=['GET'])
class TangoDsmTests(Resource):
    def get(self):
        start_time = time.time()
        try:
            dict_users = dict_db.get_dict()
        except TypeError:
            LOG.error("Recommender vector not found due to DB problem"
                      ,extra={"status": 404,"time_elapsed": "%.3f seconds" % (time.time()-start_time)})
            return ioObj.generic_resp(404,'application/json',
                                      ioObj.json_d(
                                          ioObj.error_message("Recommender vector not found due to DB problem")))

        LOG.info("Recommender vector found",
                 extra={"status": 200,"time_elapsed": "%.3f seconds" % (time.time()-start_time)})
        return ioObj.generic_resp(200, 'application/json',
                                  ioObj.json_d(dict_users))

def mkdir_p(path):
    try:
        os.makedirs(path, exist_ok=True)  # Python>3.2
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise


class MakeFileHandler(RotatingFileHandler):
    def __init__(self, filename, maxBytes, backupCount, mode='a', encoding=None, delay=0):
        mkdir_p(os.path.dirname(filename))
        RotatingFileHandler.__init__(self, filename,maxBytes, backupCount )


if __name__ == '__main__':
    app.debug=True
    # handler = MakeFileHandler ( 'logs/logger' , maxBytes=10000 , backupCount=1 )
    # handler.setLevel ( logging.DEBUG )
    # app.logger.addHandler ( handler )
    # log = logging.getLogger('werkzeug')
    # log.setLevel(logging.INFO)
    # log.addHandler(handler)
    app.run(host='0.0.0.0', port=os.getenv('PORT',4010))
