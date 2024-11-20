import { EnvironmentSettings } from "@/services/EnvironmentSettings";
import { selectedApp } from "@/store/ApplicationState";

export const isProdAppSelectedOnProdEnv = () => {
    const isProdEnvironment = new EnvironmentSettings().isProdEnvironment();
    const isSelectedAppProd = selectedApp.value?.env === "PROD";
    return isProdEnvironment && isSelectedAppProd;
};
