Procedure to re-generate the data locally:

node generate-data.js > data.sql
check into git and push


Procedure to load the data into FAM Test environment:

- Connect to AWS Console
- Go to EC2 instance fam_util_ec2_host
- Connect -> Session Manager -> Connect to start Unix session

cd /tmp
sudo yum install git
git clone https://github.com/bcgov/nr-forests-access-management.git
cd nr-forests*
git checkout <branch with revised data.sql>
cd scripts/load-test-data-gen
psql -h test-fam-cluster.cluster-cbsbrkv1tjh1.ca-central-1.rds.amazonaws.com -p 5432 -U sysadmin famdb < data.sql
(Get password from AWS SecretManager for famdb-master-creds-up-glider)

Notes:
- Tried to use curl to get the data.sql file but had problems with it being in dos format with special characters at start. So used git instead.
- Have to use sysadmin user, as the fam_proxy_api user doesn't have enough permissions.
- Could skip uploading file in git if installed node on the fam_util_ec2_host but I didn't want to go that far.
- The data generation is designed to be rerunnable - it deletes all generated data (while avoiding deleting manually created data)
- It will probably have issues with deleting manually-created data linking to the generated data - Need to address that.

