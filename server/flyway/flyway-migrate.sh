#!/bin/sh
set -eu

flyway migrate -user=postgres -password=test -url='jdbc:postgresql://localhost/' -placeholders.api_db_username=fam_proxy_api -placeholders.api_db_password=test