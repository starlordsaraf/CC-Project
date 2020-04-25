import pika
import json
from pymongo import MongoClient
from datetime import datetime
from bson.json_util import dumps
from subprocess import check_output
import os



connection_sync = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel_sync = connection_sync.channel()

channel_sync.exchange_declare(exchange='logs', exchange_type='fanout')

result = channel_sync.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel_sync.queue_bind(exchange='logs', queue=queue_name)

print(' [*] Waiting for logs')

def callback(ch, method, properties, body):
    print(" [x] %r" % body)                     #FIX ME! -- add to db + check if already updated for a command

channel_sync.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

channel_sync.start_consuming()