import router from '@/router';
import { reactive, readonly } from 'vue';

// Auth state from localStorage
const state = reactive({
    famUser: localStorage.getItem('famUser')? JSON.parse(localStorage.getItem('famUser') as string): undefined,
})

// functions

function isLoggedIn(): boolean {
    const loggedIn = !!state.famUser?.token; // TODO check if token expired later?
    return loggedIn;
}

async function login() {
    /*
        TODO: Use Amplify library to connect to aws for redirect and sign in 
        to get user token and inject it for 'famUser'.
    */
    const famUser = {
        name: 'fake_user',
        token: 'fake_token'
    };

    // update famUser state
    state.famUser = famUser;

    // store user details and jwt in local storage to keep user logged in between page refreshes
    localStorage.setItem('famUser', JSON.stringify(famUser));
    router.push('/');
}

async function logout() {
    state.famUser = null;
    localStorage.removeItem('famUser');
    // TODO: Probably need to call Amplify library for sign out from Cognito?
    router.push('/');
}

// -----

const methods = {
    login,
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