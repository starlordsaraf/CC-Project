from flask import Flask, render_template,jsonify,request,abort
import requests
import json
from flask import Response
from bson.json_util import dumps
import pika
import datetime
import math
import atexit
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)

connection_r = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel_r = connection_r.channel()
channel_r.queue_declare(queue="readq")

connection_w = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel_w = connection_w.channel()
channel_w.queue_declare(queue="writeq")

resp_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
resp_channel = resp_connection.channel()
resp_channel.queue_declare(queue="responseq")

class Scale(object):
    total = 0
    count = 0
    number = 0

    def check(self):
        print("################hello in trigger#################")
        containers_needed = math.ceil(self.count/20)
        containers_running = 0 #TODO: Write command to count current containers
        self.count = 0
        if(containers_needed>containers_running):
            for i in range(containers_needed-containers_running):
                self.number+=1
                container_name = "slave"+str(self.number)
                mongo_name = "slave-mongo"+str(self.number)
                #TODO: call container and mongo spawnning commands
        elif(containers_needed<containers_running):
            #TODO: delete containers and theri respective mongo containers
            pass



class Callback(object):
    def __init__(self,body):
        self.body=body
    def response_callback(self, ch, method, properties, body):
        print("[x] received %r" %body)
        d = body.decode("utf-8")
        d = json.loads(d)
        self.body = d
        resp_channel.stop_consuming()


S = Scale()


@app.route('/api/v1/db/read',methods=["POST"])
def read():
    S.total+=1
    if(request.get_json()["method"] not in ["get_id_rides_count","get_all_rides","get_id_rides","get_user_rides"]):
        S.count+=1
    if(S.total==1):
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=S.check, trigger="interval", seconds=120)
        scheduler.start()  
        atexit.register(lambda: scheduler.shutdown())  


    d_values = json.dumps(request.get_json())
    channel_r.basic_publish(exchange='',routing_key='readq',body=d_values)
    print("added to readq")
    #response = resp_channel.basic_get("responseq")[2]  #FIX ME!!
    C = Callback("null")
    resp_channel.basic_consume(queue="responseq", on_message_callback=C.response_callback, auto_ack=True)
    print("Waiting for response messages")
    resp_channel.start_consuming() 
    response = C.body
    #print("Response:",response)
    
    return(json.dumps(response))



@app.route('/api/v1/db/write',methods=["POST"])
def write():
    d_values = json.dumps(request.get_json())
    channel_w.basic_publish(exchange='',routing_key='writeq',body=d_values)
    print("added to writeq")
    return "{}"


@app.route('/api/v1/crash/master')
def kill_master():
    pass


@app.route('/api/v1/crash/slave')
def kill_highest_slave():
    pass


@app.route('/api/v1/worker/list')
def get_sorted_workers_pid():
    pass





if __name__ == '__main__':	
	app.debug=True
	app.run(host="localhost", port=5002, debug=True)