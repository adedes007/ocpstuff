##### # create the image
```
oc new-build https://github.com/nnachefski/ocpstuff.git -i rhel7-custom --context-dir=python-34-custom --name=python-34-custom -e SKIP_REPOS_ENABLE=true -e SKIP_REPOS_DISABLE=true --strategy=docker -n openshift
```