#!/usr/bin/env python3

import pika, platform, os, re, time

def hasenv(name):
    return os.getenv(name) != None

IS_DEVOPSRELPEASE = hasenv('DEVOPS_RELEASE')
IS_DEVOPSDEVELOP = not IS_DEVOPSRELPEASE and hasenv('DEVOPS')
IS_DEVOPS = hasenv('DEVOPS')
IS_LOCAL = not IS_DEVOPS

open('/work/.reposync.pid', 'w').write(str(os.getpid()))

class Consumer(object):
    exchange = 'gitlab.hook.post-receive'
    queue = platform.node() + '.reposync.' + str(os.getpid())
    host = 'amqp://devops:devops@rabbitmq/devops'
    def __init__(self):
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumertag = None
    def connect(self):
        return pika.SelectConnection(pika.URLParameters(self.host), self.on_connection_open, stop_ioloop_on_close=False)
    def on_connection_open(self, unuse_connection):
        print("reposync: connected")
        self.add_on_connection_close_callback()
        self.open_channel()
    def add_on_connection_close_callback(self):
        print("reposync: adding callback for connection closed")
        self._connection.add_on_close_callback(self.on_connection_closed)
    def on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            print("reposync: connection lost, reconnecting in 5 seconds")
            self._connection.ioloop.call_later(5, self.reconnect)
    def reconnect(self):
        self._connection.ioloop.stop()
        if not self._closing:
            self._connection = self.connect()
            self._connection.ioloop.start()
    def open_channel(self):
        print("reposync: creating new channel")
        self._connection.channel(on_open_callback=self.on_channel_open)
    def on_channel_open(self, channel):
        print("reposync: channel opened")
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_queue(self.queue)
    def add_on_channel_close_callback(self):
        print("reposync: adding callback for channel closed")
        self._channel.add_on_close_callback(self.on_channel_closed)
    def on_channel_closed(self, channel, reply_code, reply_text):
        print("reposync: channel %i was closed: %s" % (channel, reply_text))
        self._connection.close()
    def setup_queue(self, queue_name):
        print("reposync: declaring queue %s" % queue_name)
        self._channel.queue_declare(self.on_queue_declareok, queue_name, auto_delete=True)
    def on_queue_declareok(self, method_frame):
        print("reposync: binding %s to %s" % (self.exchange, self.queue))
        self._channel.queue_bind(self.on_bindok, self.queue, self.exchange)
    def on_bindok(self, unused_frame):
        print("reposync: queue bound")
        self.start_consuming()
    def start_consuming(self):
        print("reposync: start consuming")
        self.add_on_cancel_callback()
        self._consumertag = self._channel.basic_consume(self.on_message, self.queue)
    def add_on_cancel_callback(self):
        print("reposync: adding callback for consumer cancellation")
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)
    def on_consumer_cancelled(self, method_frame):
        print("reposync: consumer shutting down: %s" % method_frame)
        if self._channel:
            self._channel.close()
    def on_message(self, unused_channel, basic_deliver, properties, body):
        print("reposync: received message")
        self.acknowledge_message(basic_deliver.delivery_tag)
        on_message(self, body)
    def acknowledge_message(self, delivery_tag):
        self._channel.basic_ack(delivery_tag)
    def stop_consuming(self):
        if self._channel:
            print("reposync: stop consuming")
            self._channel.basic_cancel(self.on_cancelok, self._consumertag)
    def on_cancelok(self, unused_frame):
        print("reposync: send stop command")
        self.close_channel()
    def close_channel(self):
        print("reposync: closing channel")
        self._channel.close()
    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()
    def stop(self):
        print("reposync: stopping")
        self._closing = True
        self.stop_consuming()
        self._connection.ioloop.start()
        print("reposync: stopped")
    def close_connection(self):
        print("reposync: closing connection")
        self._connection.close()    

def on_message(consumer, body):
    res = re.compile(r'(.+\/.+)\.git').search(body.decode('utf-8'))
    if res is None:
        return
    prj = res.group(1)
    print('gitlab: ' + prj + ' changed')
    if prj == 'devops/reposync':
        os.system('cd /work/reposync; git pull')
        os.system('/work/reposync/reposync.py &')
        time.sleep(1)
        print("reposync: close old version")
        consumer.stop()
    if prj == 'devops/register':
        pid = open('/work/.register.pid', 'r').read()
        os.system('kill ' + pid)
        os.system('cd /work/register; git pull')
        os.system('/work/register/register.py &')
    if prj == os.getenv('PROJECT'):        
        os.system('cd /work/code; git pull')
        if os.path.isfile('/work/devops-code-pull'):
            os.system('/work/devops-code-pull &')
        if os.path.isfile('/work/code/devops-code-pull'):
            os.system('/work/code/devops-code-pull &')

def main():
    consumer = Consumer()
    try:
        consumer.run()
    except KeyboardInterrupt:
        consumer.stop()

if __name__ == '__main__':
    main()
