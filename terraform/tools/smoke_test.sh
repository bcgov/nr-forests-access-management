shopt -s lastpipe
terragrunt run-all output > output.txt
fam_api_base_url=$(awk -F= '/fam_api_base_url/ { gsub(" ","",$2);print $2 }' output.txt)
fam_api_base_url=$(sed 's/^"//' <<< $fam_api_base_url)
fam_api_base_url=$(sed 's/"$//' <<< $fam_api_base_url)
smoke_test_url="$fam_api_base_url/smoke_test"
echo "Smoke test URL: [$smoke_test_url]"
curl --silent --show-error --fail $smoke_test_url