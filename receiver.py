import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue="hello")

def callback(ch,method,properties,body):
    print("[x] received %r" %body)
    d = json.loads(body)
    return(d["A"])


#channel.basic_consume(queue="hello", on_message_callback=callback, auto_ack=True)
body = channel.basic_get("hello")[2]
print(json.dumps(json.loads(body)))

print("Waiting for messages")
channel.start_consuming() 
