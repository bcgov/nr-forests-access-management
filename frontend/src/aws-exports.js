/**
 * This aws-exports is the configuration for Amplify library to communicate with AWS Cognito.
 * It uses generated (different in each environment) "env.json" static file that is
 * being loaded and stored in user's browser storage at run time. (See env.js at index.html)
 *
 * A note for purpose of using optional ("env?.") is that this is not to skip values when "env"
 * is not loaded. When there is no "env.json" loaded yet, the error message is strange; so give it
 * optional "?" simply let the Amplify to throw more meaningful error.
 */
const env = JSON.parse(window.localStorage.getItem("env_data"));

const config = {
    aws_cognito_region: env?.fam_cognito_region.value,
    aws_user_pools_id: env?.fam_user_pool_id.value,
    aws_user_pools_web_client_id: env?.fam_console_web_client_id.value, // This is App Client Id
    aws_mandatory_sign_in: "enable",
    oauth: {
        domain: `${env?.fam_cognito_domain.value}.auth.ca-central-1.amazoncognito.com`,
        scope: ["openid"],
        redirectSignIn: `${env?.front_end_redirect_base_url.value}/authCallback`, // For some reason, vue nested path (/cognito/callback) does not work yet.
        redirectSignOut: `${env?.frontend_logout_chain_url.value}${env?.front_end_redirect_base_url.value}`,
        responseType: "code",
    },
    federationTarget: "COGNITO_USER_POOLS",
};

export default config;
