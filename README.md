# EmotiAI
Emotion classification based on conversational data

brew install buildpacks/tap/pack

### Access services
- Grafana: http://localhost:3000 with `username/password` is `admin/admin`
- Kibana: http://localhost:5601 with `username/password` is `elastic/changeme`
- Jaeger: http://localhost:16686

### Deploy jenkins on GCE using Ansible
- Add services account and generate key as json file, then put it into /secrets folder
- Run `gcloud auth application-default login`
- Then `ansible-playbook -i inventory deploy_jenkins/create_compute_instance.yaml`