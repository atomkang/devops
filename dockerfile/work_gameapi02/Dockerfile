FROM centos:work

#ENV GITHOST gitlab
#ENV PROJECT gameapi
#ENV BRANCH develop

ENV DEVOPS_USERGROUP nginx
ENV NGINXSITE /etc/nginx/conf.d

# php
RUN yum install -y https://mirrors.aliyun.com/remi/enterprise/remi-release-7.rpm; \
    rm -rf /etc/yum.repos.d/remi*;
COPY remi-safe.repo /etc/yum/repos.d/
COPY remi-php72.repo /etc/yum/repos.d/

# 安装php70
RUN yum install -y php70; \
    yum install -y php70-php-devel; \
    yum install -y php70-php-fpm; \
    ln -s /usr/bin/php70 /usr/bin/php; \
    ln -s /opt/remi/php70/root/usr/sbin/php-fpm /usr/sbin/php-fpm; \
    ln -s /opt/remi/php70/root/bin/php-config /usr/bin/php-config; \
    ln -s /opt/remi/php70/root/bin/php-cgi /usr/bin/php-cgi; \
    ln -s /opt/remi/php70/root/bin/phpize /usr/bin/phpize;

# 安装php扩展
RUN yum install -y php70-php-opcache; \
    yum install -y php70-php-mbstring; \
    yum install -y php70-php-gd; \
    yum install -y php70-php-pecl-xdebug; \
    yum install -y php70-php-pdo; \
    yum install -y php70-php-mysqlnd; \
    yum install -y php70-php-pecl-mysql; \
    yum install -y php70-php-pecl-redis4; \
    yum install -y php70-php-pecl-mongodb; \
    yum install -y php70-php-pecl-seaslog; \
    yum install -y php70-php-pecl-crypto; \
    yum install -y php70-php-pecl-apcu; \
    yum install -y php70-php-pgsql; \
    yum install -y php70-php-gmp; \
    yum install -y php70-php-pecl-ssh2; \
    yum install -y php70-php-pecl-memcache; \
    yum install -y php70-php-pecl-memcached; \
    yum install -y php70-php-pecl-scrypt; \
    yum install -y php70-php-pecl-oauth; \
    yum install -y php70-php-soap; \
    yum install -y php70-php-xml; \
    yum install -y php70-php-xmlrpc; \
    yum install -y php70-php-pecl-amqp; \
    yum install -y php70-php-pecl-zmq; \
    yum install -y php70-php-intl; \
    yum install -y php70-php-pecl-gearman; \
    yum install -y php70-php-pecl-leveldb; \
    yum install -y php70-php-pecl-lua; \
    yum install -y php70-php-pecl-mosquitto; \
    yum install -y php70-php-pecl-nsq; \
    yum install -y php70-php-pecl-protobuf; \
    yum install -y php70-php-pecl-grpc; \
    yum install -y php70-php-pecl-yaml; \
    yum install -y php70-php-pecl-zip; \
    yum install -y php70-php-dba; \
    yum install -y php70-php-uuid;

# env init
ENV PHPCONF /etc/opt/remi/php70
ENV PHPINI $PHPCONF/php.ini
ENV PHPEXTINI $PHPCONF/php.d
ENV PHPFPMCONF /etc/opt/remi/php70
ENV FPMCONF ${PHPFPMCON}/php-fpm.conf
ENV FPMPOOL ${PHPFPMCONF}/php-fpm.d

# install custom extensions
#COPY xhprof /root/xhprof
#COPY install-extensions /root/install-extensions
#RUN  /root/install-extensions

# config nginx
COPY index.php /usr/share/nginx/html/index.php
COPY php.ini ${PHPINI}
COPY default.conf ${NGINXSITE}/default.conf
COPY www.conf ${FPMPOOL}/www.conf
RUN mkdir -p /run/php; \
    chown ${DEVOPS_USERGROUP}:${DEVOPS_USERGROUP} /run/php;

# install composer
COPY composer.phar /usr/bin/composer
COPY devops-code-init /work/devops-code-init
COPY devops-code-pull /work/devops-code-pull
COPY mq_consumer.py /opt/mq_consumer.py

# clean
RUN /root/clean

# 启动
ADD start /root/start-php-base
CMD /root/start-php-base  && infinite 
