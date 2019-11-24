# Molecule managed
# Copyright 2019 Pystol (pystol.org).
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


{% if item.registry is defined %}
FROM {{ item.registry.url }}/{{ item.image }}
{% else %}
FROM {{ item.image }}
{% endif %}

RUN if [ $(command -v apt-get) ]; then apt-get update && apt-get install -y python sudo bash ca-certificates && apt-get clean; \
    elif [ $(command -v dnf) ]; then dnf makecache && dnf --assumeyes install sudo python*-devel python*-dnf bash {{ item.pkg_extras | default('') }} && dnf clean all; \
    elif [ $(command -v yum) ]; then yum makecache fast && yum install -y python sudo yum-plugin-ovl python-setuptools bash {{ item.pkg_extras | default('') }} && sed -i 's/plugins=0/plugins=1/g' /etc/yum.conf && yum clean all; \
    elif [ $(command -v zypper) ]; then zypper refresh && zypper install -y python sudo bash python-xml {{ item.pkg_extras | default('') }} && zypper clean -a; \
    elif [ $(command -v apk) ]; then apk update && apk add --no-cache python sudo bash ca-certificates {{ item.pkg_extras | default('') }}; \
    elif [ $(command -v xbps-install) ]; then xbps-install -Syu && xbps-install -y python sudo bash ca-certificates {{ item.pkg_extras | default('') }} && xbps-remove -O; fi

{% for pkg in item.easy_install | default([]) %}
# install pip for centos where there is no python-pip rpm in default repos
RUN easy_install {{ pkg }}
{% endfor %}


CMD ["sh", "-c", "while true; do sleep 10000; done"]
