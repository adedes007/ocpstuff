### # Make a prep.sh script on the master/ansible host.
##### use the contend below to make this file (copy and paste)
##### # SET THESE VARIABLES ###
```
echo ROOT_DOMAIN=ocp.nicknach.net               >> /etc/environment
echo APPS_DOMAIN=apps.$ROOT_DOMAIN              >> /etc/environment
echo LDAP_SERVER=gw.home.nicknach.net           >> /etc/environment
echo ANSIBLE_HOST_KEY_CHECKING=False            >> /etc/environment
echo MY_REPO=repo.home.nicknach.net             >> /etc/environment
echo OCP_VER=v3.11                              >> /etc/environment
echo RHN_ID=nnachefs@redhat.com                 >> /etc/environment
echo RHN_PASSWD=                                >> /etc/environment
echo RHN_POOL=8a85f98260c27fc50160c323263339ff  >> /etc/environment
```
##### # set vars in running shell
```
for i in `cat /etc/environment`; do `echo export $i`; done
```
##### # install sub manager
```
yum install -y subscription-manager yum-utils wget 
```
##### # OR add your internal repos (for disconnected installs)
```
rm -rf /etc/yum.repos.d/* && yum clean all
#yum-config-manager --add-repo http://$MY_REPO/repo/rhel-7-server-ose-3.10-rpms
yum-config-manager --add-repo http://$MY_REPO/repo/rhel-7-fast-datapath-rpms
yum-config-manager --add-repo http://$MY_REPO/repo/rhel-7-server-rpms
yum-config-manager --add-repo http://$MY_REPO/repo/rhel-7-server-extras-rpms
yum-config-manager --add-repo http://$MY_REPO/repo/rh-gluster-3-client-for-rhel-7-server-rpms
yum-config-manager --add-repo http://$MY_REPO/repo/rhel-7-server-ansible-2.6-rpms
yum-config-manager --add-repo http://$MY_REPO/repo/rhaos-beta
##yum-config-manager --add-repo http://$MY_REPO/repo/rhel-server-rhscl-7-rpms
##yum-config-manager --add-repo http://$MY_REPO/repo/rhel-7-server-optional-rpms
```
##### # add the repo cert to the pki store (for disconnected installs)
```
wget http://$MY_REPO/repo/$MY_REPO.crt && mv -f $MY_REPO.crt /etc/pki/ca-trust/source/anchors && restorecon /etc/pki/ca-trust/source/anchors/$MY_REPO.crt && update-ca-trust
```
##### # if installing beta repo, disable gpgcheck
```
echo gpgcheck=0 >> /etc/yum.repos.d/repo.home.nicknach.net_repo_rhaos-beta.repo
```
##### # install some general pre-req packages
``` 
yum install -y yum-utils wget git net-tools bind-utils iptables-services bridge-utils bash-completion nfs-utils dstat mlocate screen
```
##### # install docker
```
yum install -y docker crio
```
##### # enable container runtime
```
systemctl enable docker --now
systemctl enable crio cri-tools --now
```
##### # install gluster packages 
```
yum install -y cns-deploy heketi-client
```
##### # make sure your nodes are up-to-date
```
yum -y update
```
#### # done with prep.sh
##### # install openshift client package (oc)
```
yum install -y atomic-openshift-clients
```
#### # now run the prep.sh script on all hosts (using ansible)
###### # if on AWS, use --private-key=your_key.pem
```
ansible "*" -m script -a prep.sh
```
###### # reboot if necessary
```
ansible "*" -m script -a "reboot"
```
##### # install openshift-ansible and dependencies 
```
yum install -y openshift-ansible-playbooks
```
##### # now create your ansible hosts (inventory) file 
###### # (see below link for creating this file)
https://raw.githubusercontent.com/nnachefski/ocpstuff/master/install/generate-ansible-inventory.sh
##### # run the pre-req check
```
ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/prerequisites.yml
```
##### # now run the ansible playbook to deploy
```
ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/deploy_cluster.yml
```
###### # --private-key ~/.ssh/nick-west2.pem

##### # during the install, do these commands in separate terminals to trouble shoot any issues
```
watch oc get pods -owide --all-namespaces

# and

oc get events -owide --all-namespaces -w
###### # this only works after the API becomes available
# and

watch oc get pv

# and

journalctl -xlf
```
###### # verify the install was successful (oc get nodes)
### # Now run through the post-deployment steps
#### # https://github.com/nnachefski/ocpstuff/blob/master/install/post-deployment.md

