# Instructions for local testing

Install the collection by:

```
# Assumming KubeInit is in the home directory

cd
cd kubeinit
rm -rf releases
mkdir -p releases
ansible-galaxy collection build kubeinit --verbose --force --output-path releases/
cd releases
LATEST=$(ls kubeinit-kubeinit*.tar.gz | grep -v latest | sort -V | tail -n1)
ln -sf $LATEST kubeinit-kubeinit-latest.tar.gz
ansible-galaxy collection install --force kubeinit-kubeinit-latest.tar.gz
cd
```

Then proceed to render the page:

```
sudo pip3 install --upgrade pip
sudo pip3 install --upgrade virtualenv
sudo pip3 install --upgrade setuptools
sudo pip3 install --upgrade ansible
sudo pip3 install --upgrade markdown
sudo pip3 install --upgrade ruamel.yaml
sudo pip3 install --upgrade sphinx-rtd-theme
sudo dnf install -y python3-sphinx
# Build the docs
cd docs/src
make html
open _build/html/index.html
```
