FROM centos:cxx

EXPOSE 6379
VOLUME [ "/data" ]

WORKDIR /root
ADD redis-5.0.0.tar.gz /root/
RUN cd redis-5.0.0 && make MALLOC=libc && make install && make clean; \
    rm -rf /root/redis-5.0.0; \
    /root/clean;

COPY redis.conf /etc/redis.conf
COPY start /root/start-redis

RUN chmod +x /root/start-redis && chmod +x /usr/bin/infinite
# 特殊配置
CMD /root/start-redis && infinite

# 修改host
# echo "vm.overcommit_memory=1" >> /etc/sysctl.conf
# echo never > /sys/kernel/mm/transparent_hugepage/enabled or
# echo "echo never > /sys/kernel/mm/transparent_hugepage/enabled" >> /etc/rc.local
# docker run --sysctl net.core.somaxconn=511 and /etc/sysctl.conf
