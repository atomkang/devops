"""
Author: Atom
Create time: 2020-08-27 10:21
IDE: PyCharm
"""

import time
import os
from pyapollo import ApolloClient

while True:
    client = ApolloClient(app_id='pm',config_server_url='http://192.168.102.202:8080')
    client.start(5)
    content=(client.get_value('pm'))

    fo = open("/work/code/.env","w")
    fo.write(content)
    fo.close()
    time.sleep(60)
