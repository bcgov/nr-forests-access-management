/**
 * This aws-exports is the configuration for Amplify library to communicate with AWS Cognito.
 * It uses generated (different in each environment) "env.json" static file that is
 * being loaded and stored in user's browser storage at run time. (See env.js at index.html)
 *
 * A note for purpose of using optional ("env?.") is that this is not to skip values when "env"
 * is not loaded. When there is no "env.json" loaded yet, the error message is strange; so give it
 * optional "?" simply let the Amplify to throw more meaningful error.
 */

const rawEnv = window.localStorage.getItem("env_data");
if (!rawEnv) {
    throw new Error("Missing env_data in localStorage");
}
const env = JSON.parse(rawEnv);

const verificationMethods: "code" | "token" = "code";

const config = {
    Auth: {
        Cognito: {
            userPoolId: env.fam_user_pool_id.value,
            userPoolClientId: env.fam_console_web_client_id.value, // This is App Client Id
            loginWith: {
                oauth: {
                    domain: `${env.fam_cognito_domain.value}.auth.ca-central-1.amazoncognito.com`,
                    scopes: ["openid"],
                    redirectSignIn: [
                        `${env.front_end_redirect_base_url.value}/authCallback`,
                    ], // For some reason, vue nested path (/cognito/callback) does not work yet.
                    redirectSignOut: [
                        `${env.frontend_logout_chain_url.value}${env.front_end_redirect_base_url.value}`,
                    ],
                    responseType: verificationMethods,
                },
            },
        },
    },
};

export default config;
