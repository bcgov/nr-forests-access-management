#!/bin/sh
set -eu

flyway migrate -user=postgres -password=test -url='jdbc:postgresql://localhost/fam' -placeholders.auth_lambda_db_user=fam_auth_lambda -placeholders.auth_lambda_db_password=test -placeholders.api_db_username=fam_proxy_api -placeholders.api_db_password=test -placeholders.client_id_fam_console='26tltjjfe7ktm4bte7av998d78' -placeholders.client_id_fom_public='2c7lo6rqp983km60u3p3heqeds' -placeholders.client_id_fom_ministry='gsbm3p62isc2ju807f0imu29s'