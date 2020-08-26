FROM centos:7.4.1708

# 当前运行于docker中
ENV container docker
ENV DEVOPS docker

# 正式版标记(注释掉即为DEVOPS_DEVELOP)
ENV DEVOPS_RELEASE docker

# 渠道
ENV CHANNEL package

# centos配置
#RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == \
#    systemd-tmpfiles-setup.service ] || rm -f $i; done); \
#    rm -f /lib/systemd/system/multi-user.target.wants/*;\
#    rm -f /etc/systemd/system/*.wants/*;\
#    rm -f /lib/systemd/system/local-fs.target.wants/*; \
#    rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
#    rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
#    rm -f /lib/systemd/system/basic.target.wants/*;\
#    rm -f /lib/systemd/system/anaconda.target.wants/*;
VOLUME [ "/sys/fs/cgroup" ]

# 换源
RUN yum install -y epel-release; \
    yum install -y https://mirrors.aliyun.com/ius/ius-release-el7.rpm; \
    yum install -y http://nginx.org/packages/centos/7/noarch/RPMS/nginx-release-centos-7-0.el7.ngx.noarch.rpm

COPY ius/*.repo /etc/yum.repos.d/
COPY epel/*.repo /etc/yum.repos.d/
COPY centos.repo /etc/yum.repos.d/CentOS-Base.repo
# 更新系统
RUN yum makecache \
    yum upgrade -y

# 设置时区
ENV LANG en_US.utf8
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# 安装基础软件
RUN yum install -y wget which net-tools git tig bzip2 lzma subversion \
    yum install -y nginx
COPY nginx.conf /etc/nginx/nginx.conf

# python
COPY pip.conf /root/.config/pip/pip.conf
RUN yum install -y python36u python36u-pip python36u-devel; \
    ln -s /usr/bin/python3.6 /usr/bin/python3; \
    ln -s /usr/bin/pip3.6 /usr/bin/pip3; \
    pip3 install --upgrade pip; \
    find / -name "*.py[co]" -exec rm '{}' ';'

# 清理
COPY clean /root/clean

RUN /root/clean;

# 默认打开了nginx的端口
EXPOSE 80 443

# 容器持久运行
COPY infinite /usr/bin/infinite
