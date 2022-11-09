const config = {
    aws_cognito_region: 'ca-central-1',
    aws_user_pools_id: 'ca-central-1_5BOn4rGL8',
    aws_user_pools_web_client_id: '26tltjjfe7ktm4bte7av998d78', // This is App Client Id
    aws_mandatory_sign_in: 'enable',
    oauth: {
      domain: 'dev-fam-user-pool-domain.auth.ca-central-1.amazoncognito.com',
      scope: ['openid'],
      redirectSignIn: 'http://localhost:3000/cognito/callback',
      redirectSignOut: 'http://localhost:3000/cognito/logout',
      responseType: 'code',
    },
    federationTarget: 'COGNITO_USER_POOLS',
  };
  
  export default config;
