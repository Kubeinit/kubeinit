# The official Kubeinit web dashboard

This is the web interface to monitor the cluster's deployments.

It allows to:

* Check the cluster state
* Check the default available Kubeinit actions.
* Check the executed Kubeinit actions.
* Run Kubeinit actions.

## How to contribute

This dashboard is located at [github.com/kubeinit/kubeinit](github.com/kubeinit/kubeinit).
Any pull request of issue report is welcomed.

## Running the Kubeinit Web interface as standalone.

The Kubeinit web interface can be used as a Kubernetes dashboard
to display the current state of your deployment.

**The Kubeinit UI is currently under heavy development**

In the case you are not using Kubeinit as your fault
injection platform you can still use this web UI
following the next steps.

```bash
git clone git@github.com:kubeinit/kubeinit.git
cd kubeinit/ui
pip3 install -r requirements.txt
export FLASK_APP=run.py
# Set up the DEBUG environment
#export FLASK_ENV=development
flask run --host=0.0.0.0 --port=3000
```

This will start the web interface and
show the Kubernetes cluster status.

You need to run the Flask server from
a machine with access to the cluster.
