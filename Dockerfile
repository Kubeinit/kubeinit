FROM registry.access.redhat.com/ubi8-minimal

LABEL maintainer="Carlos Camacho <carloscamachoucv@gmail.com>"
LABEL quay.expires-after=30w

ENV ANSIBLE_GATHERING smart
ENV ANSIBLE_HOST_KEY_CHECKING false
ENV ANSIBLE_RETRY_FILES_ENABLED false
ENV ANSIBLE_SSH_PIPELINING true

ENTRYPOINT ["ansible-playbook", "-e", "kubeinit_container_run=true"]

RUN microdnf --noplugins update -y && rm -rf /var/cache/yum
RUN microdnf --noplugins install -y python39 python39-pip && rm -rf /var/cache/yum
RUN microdnf --noplugins install -y openssh-clients && rm -rf /var/cache/yum
RUN microdnf --noplugins install -y podman && rm -rf /var/cache/yum
RUN microdnf --noplugins install -y jq && rm -rf /var/cache/yum
RUN python3 -m pip install --upgrade netaddr
RUN microdnf --noplugins install -y dnf && rm -rf /var/cache/yum
RUN dnf upgrade -y && dnf clean all

ARG USER=kiuser
ARG UID=1001
ARG HOME=/home/$USER

RUN set -x && \
    \
    echo "==> Creating local user account..."  && \
    useradd --create-home --uid $UID --gid 0 $USER && \
    ln -s $HOME/kubeinit/ /kubeinit

WORKDIR $HOME/kubeinit

COPY . .

RUN chown -R ${USER}:0 .

USER $USER

ENV PATH $HOME/.local/bin:$PATH

RUN set -x && \
    \
    echo "==> Adding ansible and dependencies..." && \
    python3 -m pip install --user --upgrade pip && \
    python3 -m pip install --user --upgrade cryptography && \
    python3 -m pip install --user --upgrade wheel && \
    python3 -m pip install --user --upgrade ansible

RUN set -x && \
    \
    echo "==> Installing KubeInit..."  && \
    ansible-playbook -e kubeinit_container_build=true -vv kubeinit/setup-playbook.yml
