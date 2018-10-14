### # Make a prep.sh script on the ansible control host (can be master node).
##### # set these variables ###
```
export ROOT_DOMAIN=ocp.nicknach.net
export APPS_DOMAIN=apps.$ROOT_DOMAIN
export LDAP_SERVER=gw.home.nicknach.net
export ANSIBLE_HOST_KEY_CHECKING=False
#export SRC_REPO=repo.home.nicknach.net
export SRC_REPO=registry.access.redhat.com
export OCP_VER=v3.11
export RHN_ID=nnachefs@redhat.com
export RHN_PASSWD=
export RHN_POOL=8a85f98260c27fc50160c323263339ff
```
##### # copy and paste the script below to generate the prep.sh file
```
cat <<EOF > prep.sh

export ROOT_DOMAIN=$ROOT_DOMAIN
export APPS_DOMAIN=$APPS_DOMAIN
export LDAP_SERVER=$LDAP_SERVER
export ANSIBLE_HOST_KEY_CHECKING=False
export SRC_REPO=$SRC_REPO
export OCP_VER=$OCP_VER
export RHN_ID=$RHN_ID
export RHN_PASSWD=$RHN_PASSWD 
export RHN_POOL=$RHN_POOL

echo ROOT_DOMAIN=$ROOT_DOMAIN >> /etc/environment
echo APPS_DOMAIN=$APPS_DOMAIN >> /etc/environment
echo LDAP_SERVER=$LDAP_SERVER >> /etc/environment
echo ANSIBLE_HOST_KEY_CHECKING=False >> /etc/environment
echo SRC_REPO=$SRC_REPO >> /etc/environment
echo OCP_VER=$OCP_VER >> /etc/environment
echo RHN_ID=$RHN_ID >> /etc/environment
echo RHN_PASSWD=$RHN_PASSWD >> /etc/environment
echo RHN_POOL=$RHN_POOL >> /etc/environment
## install sub manager
yum install -d1 -y -q subscription-manager yum-utils wget
## setup repos with RHN
subscription-manager register --username=$RHN_ID --password $RHN_PASSWD --force
subscription-manager attach --pool=$RHN_POOL
subscription-manager repos --disable="*"
subscription-manager repos --enable=rhel-7-server-extras-rpms --enable=rhel-7-fast-datapath-rpms --enable=rhel-7-server-ansible-2.6-rpms --enable=rh-gluster-3-client-for-rhel-7-server-rpms --enable=rhel-7-server-ose-3.11-rpms
## OR add your internal repos (for disconnected installs)
#rm -rf /etc/yum.repos.d/* && yum clean all
#yum-config-manager --add-repo http://$SRC_REPO/repo/rhel-7-server-ose-3.11-rpms
#yum-config-manager --add-repo http://$SRC_REPO/repo/rhel-7-fast-datapath-rpms
#yum-config-manager --add-repo http://$SRC_REPO/repo/rhel-7-server-rpms
#yum-config-manager --add-repo http://$SRC_REPO/repo/rhel-7-server-extras-rpms
#yum-config-manager --add-repo http://$SRC_REPO/repo/rh-gluster-3-client-for-rhel-7-server-rpms
#yum-config-manager --add-repo http://$SRC_REPO/repo/rhel-7-server-ansible-2.6-rpms
##yum-config-manager --add-repo http://$SRC_REPO/repo/rhaos-beta
##yum-config-manager --add-repo http://$SRC_REPO/repo/rhel-server-rhscl-7-rpms
##yum-config-manager --add-repo http://$SRC_REPO/repo/rhel-7-server-optional-rpms
## add the repo cert to the pki store (for disconnected installs)
#wget http://$SRC_REPO/repo/$SRC_REPO.crt && mv -f $SRC_REPO.crt /etc/pki/ca-trust/source/anchors && restorecon /etc/pki/ca-trust/source/anchors/$SRC_REPO.crt && update-ca-trust
## if installing beta repo, disable gpgcheck
#echo gpgcheck=0 >> /etc/yum.repos.d/repo.home.nicknach.net_repo_rhaos-beta.repo
## install some general pre-req packages
yum install -d1 -y yum-utils wget git net-tools bind-utils iptables-services bridge-utils bash-completion nfs-utils dstat mlocate screen
## install openshift client package (oc)
yum install -d1 -y atomic-openshift-clients
## install container runtime
yum install -d1 -y docker crio cri-tools podman
## enable container runtime
systemctl enable docker --now
systemctl enable crio --now
## set the repo
#sed -i "s/registry.access.redhat.com'/registry.access.redhat.com\', \'repo.home.nicknach.net\'/" /etc/containers/registries.conf && systemctl restart docker && systemctl restart crio
## install gluster packages 
yum install -d1 -y cns-deploy heketi-client
## make sure your nodes are up-to-date
yum -d1 -y update

EOF
```
#### # done with prep.sh
##### # now make it executable 
```
chmod +x prep.sh
```
##### # run the prep.sh script manually on the ansible control host
```
./prep.sh
```
##### # install 'openshift-ansible' package and dependencies 
```
yum install -d1 -y openshift-ansible-playbooks
```
##### # now create your ansible hosts (inventory) file 
###### # (see below link for creating this file)
https://raw.githubusercontent.com/nnachefski/ocpstuff/master/install/generate-ansible-inventory.sh
##### # use the new inventory file to run the prep.sh script on all hosts (using ansible)
###### # if on AWS, use --private-key=your_key.pem
```
ansible "*" -m script -a prep.sh
```
###### # reboot if necessary
```
#ansible "*" -m script -a "reboot"
```
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

# and

watch oc get pv

# and

journalctl -xlf
```
###### # verify the install was successful (oc get nodes)
### # Now run through the post-deployment steps
#### # https://github.com/nnachefski/ocpstuff/blob/master/install/post-deployment.md

