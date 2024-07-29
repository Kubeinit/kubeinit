<!--
##############################################
# This page is rendered automatically        #
# from the ci/render_periodic_jobs_page.py   #
# script any change here will be overwritten #
##############################################
-->

<p style="text-align: center" align="center">
    <a href="https://www.kubeinit.org"><img src="https://raw.githubusercontent.com/Kubeinit/kubeinit/master/images/logo.svg?sanitize=true" alt="The KUBErnetes INITiator"/></a>
</p>

# Periodic jobs status

| Distribution     | Label/Status  | Driver           | Controllers       | Computes          | Hypervisors           | Launch from           |
|------------------|---------------|------------------|-------------------|-------------------|-----------------------|-----------------------|
| Origin Distribution of K8s | <a href='https://ci.kubeinit.org/file/kubeinit-ci/jobs/okd-libvirt-3-1-1-h-periodic-pid-weekly-u/index.html'><img height='20px' src='https://ci.kubeinit.org/file/kubeinit-ci/jobs/okd-libvirt-3-1-1-h-periodic-pid-weekly-u/badge_status.svg'/></a> | libvirt | 3 | 1 | 1 | Host |
| Origin Distribution of K8s | <a href='https://ci.kubeinit.org/file/kubeinit-ci/jobs/okd-libvirt-3-0-2-h-periodic-pid-weekly-u/index.html'><img height='20px' src='https://ci.kubeinit.org/file/kubeinit-ci/jobs/okd-libvirt-3-0-2-h-periodic-pid-weekly-u/badge_status.svg'/></a> | libvirt | 3 | 0 | 2 | Host |
| Origin Distribution of K8s | <a href='https://ci.kubeinit.org/file/kubeinit-ci/jobs/okd-libvirt-1-1-1-h-periodic-pid-weekly-u/index.html'><img height='20px' src='https://ci.kubeinit.org/file/kubeinit-ci/jobs/okd-libvirt-1-1-1-h-periodic-pid-weekly-u/badge_status.svg'/></a> | libvirt | 1 | 1 | 1 | Host |
| Origin Distribution of K8s | <a href='https://ci.kubeinit.org/file/kubeinit-ci/jobs/okd-libvirt-1-0-1-h-periodic-pid-weekly-u/index.html'><img height='20px' src='https://ci.kubeinit.org/file/kubeinit-ci/jobs/okd-libvirt-1-0-1-h-periodic-pid-weekly-u/badge_status.svg'/></a> | libvirt | 1 | 0 | 1 | Host |
| Vanilla K8s | <a href='https://ci.kubeinit.org/file/kubeinit-ci/jobs/k8s-libvirt-3-1-1-h-periodic-pid-weekly-u/index.html'><img height='20px' src='https://ci.kubeinit.org/file/kubeinit-ci/jobs/k8s-libvirt-3-1-1-h-periodic-pid-weekly-u/badge_status.svg'/></a> | libvirt | 3 | 1 | 1 | Host |
| Vanilla K8s | <a href='https://ci.kubeinit.org/file/kubeinit-ci/jobs/k8s-libvirt-3-0-2-h-periodic-pid-weekly-u/index.html'><img height='20px' src='https://ci.kubeinit.org/file/kubeinit-ci/jobs/k8s-libvirt-3-0-2-h-periodic-pid-weekly-u/badge_status.svg'/></a> | libvirt | 3 | 0 | 2 | Host |
| Vanilla K8s | <a href='https://ci.kubeinit.org/file/kubeinit-ci/jobs/k8s-libvirt-1-1-1-h-periodic-pid-weekly-u/index.html'><img height='20px' src='https://ci.kubeinit.org/file/kubeinit-ci/jobs/k8s-libvirt-1-1-1-h-periodic-pid-weekly-u/badge_status.svg'/></a> | libvirt | 1 | 1 | 1 | Host |
| Vanilla K8s | <a href='https://ci.kubeinit.org/file/kubeinit-ci/jobs/k8s-libvirt-1-0-1-h-periodic-pid-weekly-u/index.html'><img height='20px' src='https://ci.kubeinit.org/file/kubeinit-ci/jobs/k8s-libvirt-1-0-1-h-periodic-pid-weekly-u/badge_status.svg'/></a> | libvirt | 1 | 0 | 1 | Host |

The content of this page is rendered from each job label defined
in [get_periodic_jobs_labels](https://github.com/Kubeinit/kubeinit/blob/main/ci/kubeinit_ci_utils.py#L146) and
processed in the
[render_periodic_jobs_page.py](https://github.com/Kubeinit/kubeinit/blob/main/ci/render_periodic_jobs_page.py) script.
After every merge, changes to this file will be verified by the
[render_periodic_jobs_status_page](https://github.com/Kubeinit/kubeinit/blob/main/.github/workflows/render_periodic_jobs_status_page.yml)
job, if there are changes, a new PR will be pushed automatically.
