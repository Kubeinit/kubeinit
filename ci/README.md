# Required variables

Configure in your GitLab CI/CD settings the following variables:

* VARS_FILE

A file with extra variables to be used

* GH_TOKEN

The GitLab token to trigger the pipelines job.

* CI_PIPELINE_URL

The pipeline URL, like: https://gitlab.com/kubeinit/kubeinit-ci/pipelines/

# How to run:

Create a CI/CD schedule i.e.:

* Description: Cron to check for new PRs
* Interval Pattern: Custom ( Cron syntax ) */15 * * * *
* Cron Timezone: UTC
* Target Branch: master
* Activated: Active

Add the `kubeinit-ci-bot` tag to the runners that
will run the jobs.
