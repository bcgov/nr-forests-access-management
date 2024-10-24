import type { AxiosError } from "axios";

export const formatAxiosError = (err: AxiosError): string =>
    `${err.response?.status}: ${err.message}`;
