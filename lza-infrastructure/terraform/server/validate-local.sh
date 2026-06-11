#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

artifacts=(
  "fam_auth_function.zip"
  "fam-ui-api.zip"
  "fam-admin-management-api.zip"
)

created_artifacts=()

cleanup() {
  for artifact in "${created_artifacts[@]}"; do
    rm -f "$artifact"
  done
}

trap cleanup EXIT

for artifact in "${artifacts[@]}"; do
  if [[ ! -f "$artifact" ]]; then
    printf 'local validate placeholder\n' > "$artifact"
    created_artifacts+=("$artifact")
  fi
done

terraform init -backend=false
terraform validate
