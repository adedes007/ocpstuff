curl http://satellite.home.nicknach.net/pub/bootstrap.py > bootstrap.py && chmod +x bootstrap.py && ./bootstrap.py -l admin -o nicknach -a ocp-node -s satellite.home.nicknach.net -L home -g ocp-nodes -p welcome1 --skip-puppet --force

subscription-manager repos --disable nicknach_epel_epel

subscription-manager repos --disable nicknach_nvidia_cuda
