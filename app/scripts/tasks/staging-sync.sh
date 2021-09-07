#!/bin/bash
# Sync prod actionstep data to staging
set -e
echo -e "\nPulling paralegal info from actionstep"
./manage.py migrate_actionstep_paralegals
echo -e "\nPulling filenote info from actionstep"
./manage.py migrate_actionstep_filenotes
echo -e "\nPulling email info from actionstep"
./manage.py migrate_actionstep_emails
echo -e "\nObsfucating all personally identifiable information."
./manage.py obsfucate_actionstep_data
