FROM python:slim

LABEL maintainer="Carlos Camacho <carloscamachoucv@gmail.com>"
LABEL quay.expires-after=30w

COPY . .

# Overrides SSH Hosts Checking
RUN set -x && \
    \
    echo "==> Installing dependencies..."  && \
    apt-get update -y && apt-get install -y \
        openssh-client && \
    \
    echo "==> Setting up ssh options..."  && \
    mkdir /root/.ssh && \
    echo "Host *" >> /root/.ssh/config && \
    echo "  StrictHostKeyChecking no" >> /root/.ssh/config && \
    echo "  IdentityFile /root/.ssh/id_rsa" >> /root/.ssh/config && \
    \
    echo "==> Adding Python runtime and deps..."  && \
    pip3 install \
        --upgrade \
        pip \
        shyaml \
        ansible \
        netaddr && \
    \
    echo "==> Installing KubeInit..."  && \
    cd ./kubeinit && \
    rm -rf ~/.ansible/collections/ansible_collections/kubeinit/kubeinit && \
    ansible-galaxy collection build -v --force --output-path releases/ && \
    ansible-galaxy collection install --force --force-with-deps releases/kubeinit-kubeinit-`cat galaxy.yml | shyaml get-value version`.tar.gz

ENV ANSIBLE_GATHERING smart
ENV ANSIBLE_HOST_KEY_CHECKING false
ENV ANSIBLE_RETRY_FILES_ENABLED false
ENV ANSIBLE_SSH_PIPELINING True

ENTRYPOINT ["ansible-playbook"]
