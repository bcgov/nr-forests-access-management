const NAVIGATION_PATH_KEY = 'NAVIGATION_PATH_KEY';

export const setNavigationPath = (path: string) => {
    localStorage.setItem(NAVIGATION_PATH_KEY, path)
};

export const getNavigationPath = () => {
    return localStorage.getItem(NAVIGATION_PATH_KEY);
};

export const removeNavigationPath = () => {
    localStorage.removeItem(NAVIGATION_PATH_KEY)
}