"""
Author: Atom
Create time: 2020-08-19 20:52
IDE: PyCharm
"""

import pika
import json
import sys

cred = pika.PlainCredentials('pengkang01','abcd1234!')

conparm = pika.ConnectionParameters("192.168.103.153", credentials=cred,virtual_host='aoyou_test')

conbrok = pika.BlockingConnection(conparm)

# 声明一个管道,在管道里发消息
channel = conbrok.channel()

channel.exchange_declare(exchange="atom", exchange_type="direct", passive=False, durable=True, auto_delete=False)

# msg = sys.argv[1]
msg = {}
msg["container_name"]= sys.argv[1]
msg["commit_id"] = sys.argv[2]
# msg[sys.argv[1]]=sys.argv[2]
json_msg = json.dumps(msg)
msg_props = pika.BasicProperties()
msg_props.content_type="application/json"
msg_props.delivery_mode=2

channel.basic_publish(body=json_msg, exchange="atom", properties=msg_props, routing_key="hola")

