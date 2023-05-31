// @ts-check
/// <reference path="../global.d.ts" />

Cypress.Commands.add('getByDataTest', (selector) => cy.get(`[data-cy=${selector}]`));

Cypress.Commands.add('login', () => {
    cy.get('[id="landing-idir-button"]').click();
    cy.wait(8000);
    cy.origin('https://logontest7.gov.bc.ca', () => {
        cy.get('input[name=user]').type(Cypress.env('username'), { delay: 50, log: false });
        cy.get('input[name=password]').type(Cypress.env('password'), { delay: 50, log: false });
        cy.get('input[name=btnSubmit]').click();
    });
});