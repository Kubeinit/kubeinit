FROM quay.io/centos/centos:stream8

LABEL maintainer="Carlos Camacho <carloscamachoucv@gmail.com>"
LABEL quay.expires-after=30w

ENV ANSIBLE_GATHERING smart
ENV ANSIBLE_HOST_KEY_CHECKING false
ENV ANSIBLE_RETRY_FILES_ENABLED false
ENV ANSIBLE_SSH_PIPELINING true

ENTRYPOINT ["ansible-playbook", "-e", "kubeinit_container_run=true"]

RUN set -x && \
    \
    echo "==> Installing pacakges repo dependencies..."  && \
    curl -L -o /etc/yum.repos.d/kubeinit.repo https://download.opensuse.org/repositories/home:/kubeinit/CentOS_8_Stream/home:kubeinit.repo && \
    echo "priority=1" >> /etc/yum.repos.d/kubeinit.repo && \
    echo "module_hotfixes=1" >> /etc/yum.repos.d/kubeinit.repo && \
    dnf --noplugins update -y && rm -rf /var/cache/yum && \
    dnf upgrade -y && dnf clean all

RUN set -x && \
    \
    echo "==> Installing packages dependencies..."  && \
    dnf --noplugins install -y python39 python39-pip openssh-clients podman jq && rm -rf /var/cache/yum && \
    python3 -m pip install --user --upgrade netaddr && rm -rf /var/cache/yum && \
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
    python3 -m pip install --user --upgrade shyaml netaddr ipython dnspython

COPY --chown=${USER}:0 . .

RUN set -x && \
    \
    echo "==> Installing KubeInit..."  && \
    ansible-playbook -vv kubeinit/build-container-playbook.yml
