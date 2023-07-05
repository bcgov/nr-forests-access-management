shopt -s lastpipe
terragrunt run-all output > output.txt
fam_api_base_url1=$(awk -F= '/fam_api_base_url/ { gsub(" ","",$2);print $2 }' output.txt)
fam_api_base_url2=$(sed 's/^"//' <<< $fam_api_base_url1)
fam_api_base_url3=$(sed 's/"$//' <<< $fam_api_base_url2)
smoke_test_url="$fam_api_base_url3/smoke_test"
echo "Smoke test URL: [$smoke_test_url]"
curl --silent --show-error --fail $smoke_test_url