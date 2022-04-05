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
    microdnf --noplugins update -y && rm -rf /var/cache/yum && \
    microdnf --noplugins install -y python39 python39-pip openssh-clients podman jq && rm -rf /var/cache/yum && \
    python3 -m pip install --upgrade netaddr && \
    microdnf --noplugins install -y dnf && rm -rf /var/cache/yum && \
    dnf upgrade -y && dnf clean all

ARG USER=kiuser
ARG UID=1001
ARG HOME=/home/$USER

RUN set -x && \
    \
    echo "==> Creating local user account..."  && \
    useradd --create-home --uid $UID --gid 0 $USER && \
    ln -s $HOME/kubeinit/ /kubeinit

WORKDIR $HOME/kubeinit

RUN chown -R ${USER}:0 $HOME

USER $USER

ENV PATH $HOME/.local/bin:$PATH

RUN set -x && \
    \
    echo "==> Adding ansible and dependencies..." && \
    python3 -m pip install --user --upgrade pip && \
    python3 -m pip install --user --upgrade cryptography && \
    python3 -m pip install --user --upgrade wheel && \
    python3 -m pip install --user --upgrade ansible && \
    python3 -m pip install --user --upgrade shyaml netaddr ipython

COPY --chown=${USER}:0 . .

RUN set -x && \
    \
    echo "==> Installing KubeInit..."  && \
    ansible-playbook -vv kubeinit/build-container-playbook.yml
