FROM centos:demo

ENV GITHOST git.aoyou.com
ENV PROJECT Admin

#ENV BRANCH package
ENV BRANCH master

# 自动代码更新
ENV AUTOUPDATECODE 1

RUN yum install -y gcc-c++ make; \
    yum install -y compat-db47; \
    cp /usr/include/db4.7.25/* /usr/include/; \
    pip3 install pika python-etcd leveldb lmdb bsddb3 mysql-connector-python redis mongo;

COPY id_rsa /root/.ssh/id_rsa
COPY id_rsa.pub /root/.ssh/id_rsa.pub
RUN chmod 600 /root/.ssh/id_rsa*

RUN mkdir /work /work/logs /work/tmp /work/run; \
    chmod a+rw /work/logs /work/tmp /work/run;
COPY register /work/register


# 容器内部redis
#RUN yum install -y redis
#ADD redis-devops.conf /etc/redis-devops.conf

ADD start /root/start-work
#ADD start-register /root/start-register
ADD start-code /root/start-code

RUN /root/clean;

# 启动
#CMD /root/start-work && infinite
