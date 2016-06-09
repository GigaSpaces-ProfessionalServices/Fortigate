#!/usr/bin/env bash

cfy deployments  delete -d fortinet 
cfy blueprints   delete -b fortinet 

cfy blueprints upload -b fortinet -p fortinet-blueprint.yaml
cfy deployments create -b fortinet -d fortinet
cfy executions start -d  fortinet -w install -l
cfy executions list | grep fortinet
