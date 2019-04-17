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

import json_logging, logging, sys
import os
import json
import requests
from collections import defaultdict
from surprise import SVD
from surprise import Dataset
from surprise import Reader
import csv


json_logging.ENABLE_JSON_LOGGING = True
json_logging.init()

logger = logging.getLogger("tng-vnv-dsm")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))


cwd = os.getcwd()  # Get the current working directory (cwd)
file = os.path.join(cwd,'src','rec_sys','rec_methods','data','custom_dataset.data')  

## Prepare the Reader for the Dataset and load the data
## 1. Prepare the Reader
reader = Reader(line_format='user item rating', sep=',', skip_lines=1, rating_scale=(1, 5))
logger.info("Surprise Reader for the Dataset created succesfully")

## 3. Load the dataset 
data = Dataset.load_from_file(file, reader=reader)
logger.info("> dataset OK")

## Creating train dataset...
trainset = data.build_full_trainset()
logger.info("> train dataset OK")

## Training...
algo = SVD()
algo.fit(trainset)
logger.info("> Training OK")

# Predict ratings for all pairs (u, i) that are NOT in the training set.
testset = trainset.build_anti_testset()
predictions = algo.test(testset)
logger.info("> Predictions OK")


#Method to get the test descriptors uuids from the package metadata
def get_testds_uuids(package_uuid):
    cat_url = os.getenv('CATALOGUES_URL', "http://pre-int-vnv-bcn.5gtango.eu:4011/catalogues/api/v2/")
    pack_url = cat_url + "packages/" + package_uuid
    headers = {'Content-type': 'application/json'}
    r = requests.get(pack_url, headers=headers)
    logger.info("Request to Catalogue for retrieve the package was succesfull")
    json_respo = r.json()
    pack_cont = json_respo["pd"]["package_content"]
    test_desc_uuids = []
    for object_item in pack_cont:
        if ("tstd" in object_item["content-type"]):
            test_desc_uuids.append(object_item["uuid"])
    return(test_desc_uuids)
    
#Method to get the user name from the package metadata
def get_username(package_uuid):
    cat_url = os.getenv('CATALOGUES_URL', "http://pre-int-vnv-bcn.5gtango.eu:4011/catalogues/api/v2/")
    pack_url = cat_url + "packages/" + package_uuid
    headers = {'Content-type': 'application/json'}
    r = requests.get(pack_url, headers=headers)
    json_respo = r.json()
    user_name = json_respo["username"]   
    return(user_name)
 
#Method to get the test tages from the test descriptors
def get_test_tags(test_descriptors_uuids):
    test_tags = []
    for descr_uuid in test_descriptors_uuids:
        cat_url = os.getenv('CATALOGUES_URL', "http://pre-int-vnv-bcn.5gtango.eu:4011/catalogues/api/v2/")
        testd_url = cat_url + "tests/" + descr_uuid
        headers = {'Content-type': 'application/json'}
        r = requests.get(testd_url, headers=headers)
        json_respo = r.json()
        for test_tag in json_respo["testd"]["test_tags"]:
            test_tags.append(test_tag)
    return test_tags

#Method to add user-item in the Dataset            
def add_user_item(test_tags,user_name):
	if (len(test_tags) > 0):	
		with open(file, 'a', newline='') as f:
			 wr = csv.writer(f)
			 for test_tag in test_tags:
				 wr.writerow([user_name, test_tag, '1'])
		return {'Response':'User-Item Added in the Dataset'}
	else:
		return {'Response':'No test tags were found in the test decriptor'}		

#Method for retrival of the trained users
def get_users():
    try:
        with open(file) as f:
            #Skip First line as it is the Header of the Csv
            next(f)
            users_list = []
            rows = csv.reader(f)
            for row in rows:
                users_list.append(row[0])
        #Remove duplicates        
        updated_list = list(dict.fromkeys(users_list))
        return(updated_list) 
    except Exception as e:
        error = str(e)
        return (error)

def get_items():
    try:
        with open(file) as f:
            #Skip First line as it is the Header of the Csv
            next(f)
            items_list = []
            rows = csv.reader(f)
            for row in rows:
                items_list.append(row[1])
        #Remove duplicates        
        updated_list = list(dict.fromkeys(items_list))        
        return(updated_list)
    except Exception as e:
        error = str(e)
        return (error)
        

#Method to delete a user from the dataset and his'her assosiated test items
def del_user(user):
    counter = 0
    try:
        with open(file) as f:
            #Skip First line as it is the Header of the Csv
            next(f)
            updated_rows = []
            rows = csv.reader(f)
            for row in rows:
                if (row[0] != user):
                    updated_rows.append(row) 
                else:
                    counter = 1
            with open(file, 'w', newline='') as f:
                wr = csv.writer(f)
                wr.writerow(['user', 'item', 'rating'])
                for list_item in updated_rows:
                    print(list_item)
                    wr.writerow(list_item)
            if (counter == 1):
                return  {'Response':'User Deleted'}
            else:
                return  {'Response':'User Not Found'}
    except Exception as e:
        error = str(e)
        return (error)        
   
# Method for retrieve the top n recommendations
def get_top_n(predictions, n=10):
    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n

## Get top n predictions, default=2
top_n = get_top_n(predictions, n=2)
logger.info("Top N retrieved > OK")

# Print the recommended items for each user
def get_recommendations(user_id):
    my_json_string = {}
    for uid, user_ratings in top_n.items():
        if uid == user_id:
            json_data = ([iid for (iid, _) in user_ratings])
            my_json_string = json.dumps({'user': uid, 'rec_tests': json_data})
    return my_json_string