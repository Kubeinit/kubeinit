FROM registry.access.redhat.com/ubi8-minimal

LABEL maintainer="Carlos Camacho <carloscamachoucv@gmail.com>"
LABEL quay.expires-after=30w

ENV ANSIBLE_GATHERING smart
ENV ANSIBLE_HOST_KEY_CHECKING false
ENV ANSIBLE_RETRY_FILES_ENABLED false
ENV ANSIBLE_SSH_PIPELINING true

ENTRYPOINT ["ansible-playbook", "-e", "kubeinit_container_run=true"]

RUN set -x && \
    \
    echo "==> Installing dependencies..."  && \
    microdnf upgrade -y && microdnf install -y dnf && \
    dnf upgrade -y && dnf install -y \
        python39 python39-pip openssh-clients podman && \
    \
    echo "==> Adding ansible and dependencies..." && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install --upgrade cryptography && \
    python3 -m pip install --upgrade ansible

WORKDIR /root/kubeinit

RUN ln -s /root/kubeinit/ /kubeinit

COPY . .

RUN set -x && \
    \
    echo "==> Installing KubeInit..."  && \
    ansible-playbook -e kubeinit_container_build=true -vv -i kubeinit/setup-inventory kubeinit/setup-playbook.yml 
