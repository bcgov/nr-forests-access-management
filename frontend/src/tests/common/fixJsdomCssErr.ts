//fix "Could not parse CSS stylesheet" with the primevue styling
//https://github.com/primefaces/primevue/issues/4512
//https://stackoverflow.com/questions/69906136/console-error-error-could-not-parse-css-stylesheet/69958999#69958999
export const fixJsdomCssErr = () => {
const originalConsoleError = console.error;
const jsDomCssError = 'Error: Could not parse CSS stylesheet';
console.error = (...params) => {
    if (!params.find((p) => p.toString().includes(jsDomCssError))) {
        originalConsoleError(...params);
    }
};
}