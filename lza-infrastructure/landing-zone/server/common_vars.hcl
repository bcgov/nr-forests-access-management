

inputs = {
  # Cognito App Clients common vars.
  idp_logout_chain_dev_url = "https://logontest7.gov.bc.ca/clp-cgi/logoff.cgi?retnow=1&returl=https://dev.loginproxy.gov.bc.ca/auth/realms/standard/protocol/openid-connect/logout?redirect_uri="
  idp_logout_chain_test_url = "https://logontest7.gov.bc.ca/clp-cgi/logoff.cgi?retnow=1&returl=https://test.loginproxy.gov.bc.ca/auth/realms/standard/protocol/openid-connect/logout?redirect_uri="
  idp_logout_chain_prod_url = "https://logon7.gov.bc.ca/clp-cgi/logoff.cgi?retnow=1&returl=https://loginproxy.gov.bc.ca/auth/realms/standard/protocol/openid-connect/logout?redirect_uri="
  idp_logout_chain_tools_url = "https://logontest7.gov.bc.ca/clp-cgi/logoff.cgi?retnow=1&returl=https://dev.loginproxy.gov.bc.ca/auth/realms/standard/protocol/openid-connect/logout?redirect_uri="

  # # Forest Clients API Search common configs.
  # forest_client_api_test_base_url = "https://nr-forest-client-api-test.api.gov.bc.ca"
  # forest_client_api_prod_base_url = "https://nr-forest-client-api-prod.api.gov.bc.ca"
}