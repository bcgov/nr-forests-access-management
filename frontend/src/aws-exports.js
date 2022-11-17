const env = JSON.parse(window.localStorage.getItem('env_data'))

const config = {
    aws_cognito_region: env.fam_cognito_region.value,
    aws_user_pools_id: env.fam_user_pool_id.value,
    aws_user_pools_web_client_id: env.fam_console_web_client_id.value, // This is App Client Id
    aws_mandatory_sign_in: 'enable',
    oauth: {
      domain: `${env.fam_cognito_domain.value}.auth.ca-central-1.amazoncognito.com`,
      scope: ['openid'],
      redirectSignIn: 'http://localhost:5173/authCallback', // For some reason, vue nested path (/cognito/callback) does not work yet.
      redirectSignOut: 'http://localhost:5173/authLogout',
      responseType: 'code',
    },
    federationTarget: 'COGNITO_USER_POOLS',
  };
  
  export default config;
