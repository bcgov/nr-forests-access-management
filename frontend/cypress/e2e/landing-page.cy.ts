describe('Landing Page spec', () => {
  it('should load', () => {
    cy.visit('/', { timeout: 15000 });
    cy.get('[id="landing-logo-img"]', { withinSubject: null }).should('exist');
    cy.get('[id="landing-title"]').should('be.visible').contains('Welcome to FAM')
    cy.get('[id="landing-subtitle"]').should('be.visible').contains('Forestry Access Management')
    cy.get('[id="landing-desc"]').should('be.visible').contains('Grant access to your users')
    cy.get('[id="landing-idir-button"]').should('be.visible').should('be.enabled').contains('Login with IDIR')
    cy.get('[id="landing-bceid-button"]').should('be.visible').should('be.disabled').contains('Login with Business BCeID')
    cy.get('[id="landing-idir-button"]').click();
    //After login button click, it should be redirected
    cy.url()
      .should('not.contain', '/;');
  })
});