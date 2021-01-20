from flask import Flask, render_template,jsonify,request,abort
from flask_pymongo import PyMongo
import requests
import json
import re
from flask import Response
from bson.json_util import dumps
from datetime import datetime
import logging



app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/users"
mongo = PyMongo(app)


#API to add user
@app.route('/api/v1/users',methods=['PUT'])
def add_user():
    f = open("users_count.txt","r")
    count = int(f.read())
    count +=1
    f.close()
    f = open("users_count.txt","w")
    f.write(str(count))
    f.close()

    username = request.get_json()["username"]
    password = request.get_json()["password"]
    #print(username)
    #print(password)
    no_user = mongo.db.users.find({"username":username}).count()
    if(no_user==0):
        if(re.match("^[a-fA-F0-9]{40}$",password)):
            data ={"method":"put","collection":"users","data":{"username":username,"password":password}}
            requests.post('http://127.0.0.1:5001/api/v1/db/users/write',json =data)
            return Response(json.dumps({}),status=201,mimetype='application/json')
        else:
            return Response(json.dumps({}), status=400,mimetype='application/json')
    else:
        return Response(json.dumps({}), status=400,mimetype='application/json')


#API to delete user
@app.route('/api/v1/users/<string:name>',methods=['DELETE'])
def delete_user(name):
    f = open("users_count.txt","r")
    count = int(f.read())
    count +=1
    f.close()
    f = open("users_count.txt","w")
    f.write(str(count))
    f.close()

    no_user = mongo.db.users.find({"username":name}).count()
    if(no_user==0):
        return Response(json.dumps({}), status=400, mimetype='application/json')
    else:
        data ={"method":"delete","collection":"users","data":{"username":name}}
        requests.post('http://127.0.0.1:5001/api/v1/db/users/write',json =data)
        return Response(json.dumps({}), status=200, mimetype='application/json')



#API to list users
@app.route('/api/v1/users',methods=['GET'])
def list_users():
    f = open("users_count.txt","r")
    count = int(f.read())
    count +=1
    f.close()
    f = open("users_count.txt","w")
    f.write(str(count))
    f.close()

    #print(result)
    data = {"method":"get_all","collection":"users","data":"null"}
    response = requests.post('http://127.0.0.1:5001/api/v1/db/users/read',json =data)
    if(json.loads(response.content.decode("utf-8"))==[]):
        return Response(json.dumps({}), status=204, mimetype='application/json')
    else:
        return(response.content)




#API to write to db
@app.route('/api/v1/db/users/write',methods=["POST"])
def write():
    d_values = request.get_json()
    #d_values = json.loads(values)
    collection = d_values["collection"]
    data = d_values["data"]
    method = d_values["method"]
    if(method=="put" and collection=="users"):
        mongo.db.users.insert(data)
    if(method=="delete" and collection=="users"):
        mongo.db.users.remove(data)
    
    return "done"


#API to read from db
@app.route('/api/v1/db/users/read',methods=["POST"])
def read():
    d_values = request.get_json()
    collection = d_values["collection"]
    data = d_values["data"]
    method = d_values["method"]
    if(method=="get_all" and collection=="users"):
        result = dumps(mongo.db.users.find({},{"_id":0}))
    return result

#API to clear db
@app.route('/api/v1/db/clear',methods=["POST"])
def clear():
    f = open("users_count.txt","r")
    count = int(f.read())
    count +=1
    f.close()
    f = open("users_count.txt","w")
    f.write(str(count))
    f.close()

    mongo.db.users.remove({})
    return '{}'



#API to count http requests to users app
@app.route('/api/v1/_count',methods=["GET"])
def getrequestcount():
    f = open("users_count.txt","r")
    count = int(f.read())
    f.close()
    return ('[ '+str(count)+' ]')

#reset requests count for users app
@app.route('/api/v1/_count',methods=["DELETE"])
def resetrequestcount():
    f = open("users_count.txt","r")
    count = int(f.read())
    count = 0
    f.close()
    f = open("users_count.txt","w")
    f.write(str(count))
    f.close()
    return '{}'


@app.errorhandler(404)
def not_found(e):
    f = open("users_count.txt","r")
    count = int(f.read())
    count +=1
    f.close()
    f = open("users_count.txt","w")
    f.write(str(count))
    f.close()
    return Response('',status=404)

# @app.errorhandler(400)
# def not_found_bad(e):
#     f = open("users_count.txt","r")
#     count = int(f.read())
#     count +=1
#     f.close()
#     f = open("users_count.txt","w")
#     f.write(str(count))
#     f.close()
#     return Response('',status=400)

@app.errorhandler(405)
def not_method(e):
    f = open("users_count.txt","r")
    count = int(f.read())
    count +=1
    f.close()
    f = open("users_count.txt","w")
    f.write(str(count))
    f.close()
    return Response('',status=405)


if __name__ == '__main__':	
	app.debug=True
	app.run()