FROM giovtorres/slurm-docker-cluster:latest

RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* && \
    sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

RUN yum makecache && \
    yum install -y openssh-server openssh-clients python-setuptools && \
    yum clean all && \
    easy_install pip && \
    pip install supervisor

RUN ssh-keygen -A && \
    useradd -m admin -s /bin/bash && echo 'admin:admin' | chpasswd

RUN echo -n "this-is-a-secret-munge-key-for-poj-dev-mode" > /etc/munge/munge.key && \
    chown munge:munge /etc/munge/munge.key && \
    chmod 400 /etc/munge/munge.key
RUN mkdir -p /var/run/munge && \
    chown -R munge:munge /var/run/munge /var/log/munge /etc/munge /var/lib/munge && \
    chmod 755 /var/run/munge

RUN mkdir -p /var/log/slurm && \
    chown -R slurm:slurm /var/log/slurm
RUN echo "ClusterName=linux" > /etc/slurm/slurm.conf && \
    echo "ControlMachine=slurmctld" >> /etc/slurm/slurm.conf && \
    echo "SlurmUser=slurm" >> /etc/slurm/slurm.conf && \
    echo "AuthType=auth/munge" >> /etc/slurm/slurm.conf && \
    echo "StateSaveLocation=/var/lib/slurmd" >> /etc/slurm/slurm.conf && \
    echo "SlurmdSpoolDir=/var/lib/slurmd/slurmd" >> /etc/slurm/slurm.conf && \
    echo "SwitchType=switch/none" >> /etc/slurm/slurm.conf && \
    echo "MpiDefault=none" >> /etc/slurm/slurm.conf && \
    echo "SlurmctldPidFile=/var/run/slurmctld.pid" >> /etc/slurm/slurm.conf && \
    echo "SlurmdPidFile=/var/run/slurmd.pid" >> /etc/slurm/slurm.conf && \
    echo "ProctrackType=proctrack/pgid" >> /etc/slurm/slurm.conf && \
    echo "ReturnToService=2" >> /etc/slurm/slurm.conf && \
    echo "FastSchedule=1" >> /etc/slurm/slurm.conf && \
    echo "SchedulerType=sched/backfill" >> /etc/slurm/slurm.conf && \
    echo "SelectType=select/cons_res" >> /etc/slurm/slurm.conf && \
    echo "SelectTypeParameters=CR_Core" >> /etc/slurm/slurm.conf && \
    echo "AccountingStorageType=accounting_storage/slurmdbd" >> /etc/slurm/slurm.conf && \
    echo "AccountingStorageHost=slurmctld" >> /etc/slurm/slurm.conf && \
    echo "JobAcctGatherType=jobacct_gather/none" >> /etc/slurm/slurm.conf && \
    echo "" >> /etc/slurm/slurm.conf && \
    echo "# COMPUTE NODES" >> /etc/slurm/slurm.conf && \
    echo "NodeName=node[1-3] CPUs=1 State=UNKNOWN" >> /etc/slurm/slurm.conf && \
    echo "PartitionName=normal Nodes=node[1-3] Default=YES MaxTime=INFINITE State=UP" >> /etc/slurm/slurm.conf

RUN echo "AuthType=auth/munge" > /etc/slurm/slurmdbd.conf && \
    echo "DbdAddr=localhost" >> /etc/slurm/slurmdbd.conf && \
    echo "DbdHost=localhost" >> /etc/slurm/slurmdbd.conf && \
    echo "SlurmUser=slurm" >> /etc/slurm/slurmdbd.conf && \
    echo "LogFile=/var/log/slurm/slurmdbd.log" >> /etc/slurm/slurmdbd.conf && \
    echo "PidFile=/var/run/slurmdbd.pid" >> /etc/slurm/slurmdbd.conf && \
    echo "StorageType=accounting_storage/mysql" >> /etc/slurm/slurmdbd.conf && \
    echo "StorageHost=mysql" >> /etc/slurm/slurmdbd.conf && \
    echo "StoragePass=password" >> /etc/slurm/slurmdbd.conf && \
    echo "StorageUser=slurm" >> /etc/slurm/slurmdbd.conf && \
    echo "StorageLoc=slurm_acct_db" >> /etc/slurm/slurmdbd.conf && \
    chown slurm:slurm /etc/slurm/slurmdbd.conf && \
    chmod 600 /etc/slurm/slurmdbd.conf

RUN echo "[supervisord]" > /etc/supervisord.conf && \
    echo "nodaemon=true" >> /etc/supervisord.conf && \
    echo "user=root" >> /etc/supervisord.conf && \
    echo "" >> /etc/supervisord.conf && \
    echo "[program:munged]" >> /etc/supervisord.conf && \
    echo "command=/usr/sbin/munged -F" >> /etc/supervisord.conf && \
    echo "user=munge" >> /etc/supervisord.conf && \
    echo "autorestart=true" >> /etc/supervisord.conf && \
    echo "" >> /etc/supervisord.conf && \
    echo "[program:slurmdbd]" >> /etc/supervisord.conf && \
    echo "command=/usr/sbin/slurmdbd -D" >> /etc/supervisord.conf && \
    echo "autorestart=true" >> /etc/supervisord.conf && \
    echo "" >> /etc/supervisord.conf && \
    echo "[program:slurmctld]" >> /etc/supervisord.conf && \
    echo "command=/usr/sbin/slurmctld -D" >> /etc/supervisord.conf && \
    echo "autorestart=true" >> /etc/supervisord.conf && \
    echo "" >> /etc/supervisord.conf && \
    echo "[program:sshd]" >> /etc/supervisord.conf && \
    echo "command=/usr/sbin/sshd -D" >> /etc/supervisord.conf && \
    echo "autorestart=true" >> /etc/supervisord.conf

RUN echo "[supervisord]" > /etc/supervisord_worker.conf && \
    echo "nodaemon=true" >> /etc/supervisord_worker.conf && \
    echo "user=root" >> /etc/supervisord_worker.conf && \
    echo "" >> /etc/supervisord_worker.conf && \
    echo "[program:munged]" >> /etc/supervisord_worker.conf && \
    echo "command=/usr/sbin/munged -F" >> /etc/supervisord_worker.conf && \
    echo "user=munge" >> /etc/supervisord_worker.conf && \
    echo "autorestart=true" >> /etc/supervisord_worker.conf && \
    echo "" >> /etc/supervisord_worker.conf && \
    echo "[program:slurmd]" >> /etc/supervisord_worker.conf && \
    echo "command=/usr/sbin/slurmd -D" >> /etc/supervisord_worker.conf && \
    echo "autorestart=true" >> /etc/supervisord_worker.conf && \
    echo "" >> /etc/supervisord_worker.conf && \
    echo "[program:sshd]" >> /etc/supervisord_worker.conf && \
    echo "command=/usr/sbin/sshd -D" >> /etc/supervisord_worker.conf && \
    echo "autorestart=true" >> /etc/supervisord_worker.conf

CMD ["supervisord", "-c", "/etc/supervisord.conf"]