---
name: Bug report
about: Create a report
title: ''
labels: ''
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Clone '...'
2. Prepare playbook '...'
3. Run with these variable '...'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Infrastructure**
 - Hypervisors OS: [e.g. CentOS]
 - Version [e.g. 8]

**Deployment command**

```
ansible-playbook ...
```

**Inventory file diff**

Run the following command:

```
diff \
    <(curl https://raw.githubusercontent.com/Kubeinit/kubeinit/main/kubeinit/hosts/k8s/inventory) \
    <(curl https://raw.githubusercontent.com/Kubeinit/kubeinit/main/kubeinit/hosts/okd/inventory)
```

And paste the output:

```
here
```

**Additional context**
Add any other context about the problem here.
