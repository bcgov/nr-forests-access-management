import router from '@/router';
import { EnvironmentSettings } from '@/services/EnvironmentSettings';
import { reactive, readonly } from 'vue';

const envSettings = new EnvironmentSettings();
const famCognitoRedirectUrl = envSettings.getFamCognitoRedirectUrl();

// Auth state from localStorage
const state = reactive({
    famUser: localStorage.getItem('famUser')? JSON.parse(localStorage.getItem('famUser') as string): undefined,
})

// functions 
async function login() {
    console.log("logging in...")
    // TODO: Use Amplify library to connect to aws for redirect and sign in.
    const famUser = {name: 'fake_user'};

    // update famUser state
    state.famUser = famUser;

    // store user details and jwt in local storage to keep user logged in between page refreshes
    localStorage.setItem('famUser', JSON.stringify(famUser));
    router.push('/');
}

async function logout() {
    state.famUser = null;
    localStorage.removeItem('famUser');
    router.push('/');
}

const methods = {
    login,
    logout
}

export default {
    state: readonly(state), // readonly to prevent direct state change; force it through methods if needed to.
    methods 
}