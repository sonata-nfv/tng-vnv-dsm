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

import logging, datetime, json, sys, traceback
class TangoLogger(object):

    @staticmethod
    def getLogger(name):
        logging.basicConfig(filename='logger',level=logging.DEBUG)
        logger = logging.getLogger()
        logger.propagate = False
        th = TangoJsonLogHandler('logger')
        # ch = logging.StreamHandler(sys.stdout)
        # ch.setLevel(logging.DEBUG)
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # ch.setFormatter(formatter)
        # logger.addHandler(ch)
        th.setLevel(logging.INFO)
        logger.addHandler(th)
        return logger


class TangoJsonLogHandler(logging.FileHandler):

    def _to_tango_dict(self, record):
        d = {
            # TANGO default fields
            "type": record.levelname[0],
            "timestamp": "{} UTC".format(datetime.datetime.utcnow()),
            "start_stop": record.__dict__.get("start_stop", ""),
            "component": record.name,
            "operation": record.__dict__.get("operation", record.funcName),
            "message": str(record.msg),
            "status": record.__dict__.get("status", ""),
            "time_elapsed": record.__dict__.get("time_elapsed", "")
        }
        return d

    def emit(self, record):
        print(json.dumps(self._to_tango_dict(record)),file=sys.stdout)
        msg = json.dumps(self._to_tango_dict(record))
        stream = self.stream
        stream.write(msg)
        stream.write(self.terminator)
        # self.flush()
        sys.stdout.flush()
