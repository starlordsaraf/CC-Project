import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue="hello")
'''
def callback(ch,method,properties,body):
    print("[x] received %r" %body)
    d = body.decode("utf-8")
    d = json.loads(d)
    channel.stop_consuming()
    return(d)
'''

class Callback(object):
    def __init__(self,body):
        self.body=body
    def callback(self, ch, method, properties, body):
        print("[x] received %r" %body)
        d = body.decode("utf-8")
        d = json.loads(d)
        self.body = d
        channel.stop_consuming()
        
C = Callback("null")
channel.basic_consume(queue="hello", on_message_callback=C.callback, auto_ack=True)

#body = channel.basic_get("hello")[2]
#print(json.dumps(json.loads(body)))

print("Waiting for messages")
channel.start_consuming() 
response = C.body
print(type(response))
print("Response:",response)