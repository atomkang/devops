"""
Author: Atom
Create time: 2020-08-20 11:23
IDE: PyCharm
"""

import pika
import json
import os
import time

service_name=os.getenv('PROJECT')

cred = pika.PlainCredentials('pengkang01','abcd1234!')

conparm = pika.ConnectionParameters("192.168.103.153", credentials=cred,virtual_host='aoyou_test')
conbrok = pika.BlockingConnection(conparm)
cnl = conbrok.channel()
cnl.exchange_declare(exchange="atom", exchange_type="direct", passive=False, durable=True, auto_delete=False)
cnl.queue_declare(queue="hello-queue", durable=True)
cnl.queue_bind(queue="hello-queue", exchange="atom", routing_key="hola")

def cbmsg(channel, mth, hdr, body):
    channel.basic_ack(delivery_tag=mth.delivery_tag)
    if body == "quit":
        channel.basic_cancel(consumer_tag="hello-receiver")
        channel.stop_consuming()
    else:
        print(body)
        msg=json.loads(body)
#        msg["container_name"]
#        print(msg["container_name"])
        if msg["container_name"] == service_name:
              os.system('cd /work/code; git pull')
    return

cnl.basic_consume("hello-queue", cbmsg, consumer_tag="hello-receiver")
cnl.start_consuming()
