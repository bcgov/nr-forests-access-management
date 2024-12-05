type InputType = {
    id: string;
    isValid: boolean;
    errorMsg: string;
};

export type TextInputType = {
    value: string;
} & InputType;
