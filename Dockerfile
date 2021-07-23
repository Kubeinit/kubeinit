FROM registry.access.redhat.com/ubi8-minimal

LABEL maintainer="Carlos Camacho <carloscamachoucv@gmail.com>"
LABEL quay.expires-after=30w

WORKDIR /kubeinit

RUN set -x && \
    \
    echo "==> Installing dependencies..."  && \
    microdnf upgrade -y && microdnf install -y dnf && \
    dnf upgrade -y && dnf install -y \
        python3 openssh-clients iproute jq && \
    \
    echo "==> Setting up ssh options..."  && \
    mkdir /root/.ssh && \
    echo "Host *" >> /root/.ssh/config && \
    echo "  StrictHostKeyChecking no" >> /root/.ssh/config && \
    echo "  IdentityFile /root/.ssh/id_rsa" >> /root/.ssh/config && \
    \
    echo "==> Adding Python runtime and deps..."  && \
    python3 -m pip install \
        --upgrade \
        pip \
        shyaml \
        cryptography==3.3.2 \
        ansible==3.4.0 \
        netaddr

COPY . .

RUN set -x && \
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
