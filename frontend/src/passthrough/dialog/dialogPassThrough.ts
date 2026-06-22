export const DIALOG_PASS_THROUGH = {
    root: { class: "fam-dialog-root" },
    header: { class: "fam-dialog-header" },
    title: { class: "fam-dialog-title" },
    content: { class: "fam-dialog-content" },
    footer: { class: "fam-dialog-footer" },
    headerActions: { class: "fam-dialog-header-actions" },
    pcCloseButton: {
        root: {
            class: "fam-dialog-close-button",
        },
    },
};

export const DYNAMIC_DIALOG_PASS_THROUGH = {
    root: { class: "fam-dialog-root" },
    header: { class: "fam-dialog-header" },
    title: { class: "fam-dialog-title" },
    content: { class: "fam-dialog-content" },
    footer: { class: "fam-dialog-footer" },
    headerActions: { class: "fam-dialog-header-actions" },
    pcCloseButton: {
        root: {
            class: "fam-dialog-close-button fam-dynamic-dialog-close-button",
        },
    },
};

export const CONFIRM_DIALOG_PASS_THROUGH = {
    root: { class: "fam-dialog-root fam-confirm-dialog-root" },
    header: { class: "fam-dialog-header" },
    title: { class: "fam-dialog-title" },
    content: { class: "fam-dialog-content" },
    footer: { class: "fam-dialog-footer" },
    headerActions: { class: "fam-dialog-header-actions" },
    pcCloseButton: {
        root: {
            class: "fam-dialog-close-button",
        },
    },
    pcRejectButton: {
        root: { class: "fam-confirm-dialog-reject p-button-outlined" },
        label: { class: "fam-confirm-dialog-button-label" },
    },
    pcAcceptButton: {
        root: { class: "fam-confirm-dialog-accept p-button-danger" },
        label: { class: "fam-confirm-dialog-button-label" },
    },
};
