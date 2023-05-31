/* eslint-disable no-undef */
/* eslint-disable no-unused-vars */
/// <reference types="cypress" />

declare namespace Cypress {
  interface Chainable {
    /**
     * Custom command to select DOM element by data-testid attribute.
     *
     * @param selector {string} - The data-testid attribute of the object to be selected
     * @example
     * cy.getByDataTest('main')
     */
    getByDataTest(selector: string): Chainable<JQuery<HTMLElement>>

    /**
     * Custom command to log in on app.
     *
     * @example
     * cy.login()
     */
    login(): void
  }
}
