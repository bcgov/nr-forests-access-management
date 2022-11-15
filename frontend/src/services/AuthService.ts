import router from '@/router';
import { readonly, ref } from 'vue';
import { Auth } from 'aws-amplify';

const state = ref({
    famUser: localStorage.getItem('famUser')? JSON.parse(localStorage.getItem('famUser') as string): undefined,
})

// functions

function isLoggedIn(): boolean {
    const loggedIn = !!state.value.famUser?.token; // TODO check if token expired later?
    return loggedIn;
}

async function login() {
    /*
        See Aws-Amplify documenation: 
        https://docs.amplify.aws/lib/auth/social/q/platform/js/
        https://docs.amplify.aws/lib/auth/advanced/q/platform/js/#identity-pool-federation
    */
    Auth.federatedSignIn();
}

async function logout() {
    state.value.famUser = null;
    localStorage.removeItem('famUser');
    // TODO: Probably need to call Amplify library for sign out from Cognito?
    router.push('/');
}

async function handlePostLogin() {
    return Auth.currentAuthenticatedUser()
        .then(userData => {
            console.log("userData: ", userData)

            const famUser = {
                username: userData.username,
                token: 'token' // TODO to be retrived.
            };
            state.value.famUser = famUser;
            localStorage.setItem('famUser', JSON.stringify(famUser));
            console.log("famUser set: ", localStorage.getItem('famUser'))
            return userData;
        })
        .catch((error) => console.log('Not signed in'));
}

// -----

const methods = {
    login,
    handlePostLogin,
    logout
}

const getters = {
    isLoggedIn
}

export default {
    state: readonly(state), // readonly to prevent direct state change; force it through methods if needed to.
    methods,
    getters 
}