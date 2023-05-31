describe('Landing Page spec', () => {

  let landingPageData: {
    title: string,
    subtitle: string,
    description: string,
    idir: string,
    bceid: string
  };

  beforeEach(() => {
    cy.visit('/', { timeout: 5000 });
    cy.wait(2 * 1000);

    // Load test data
    cy.fixture('landing-page').then((textData) => {
      landingPageData = textData;
    });
  });

  it('should load correctly', () => {
    cy.getByDataTest('landing-logo-img').should('exist');
    cy.getByDataTest('landing-title').should('be.visible').contains(landingPageData.title)
    cy.getByDataTest('landing-subtitle').should('be.visible').contains(landingPageData.subtitle)
    cy.getByDataTest('landing-desc').should('be.visible').contains(landingPageData.description)
    cy.getByDataTest('landing-idir-button').should('be.visible').should('be.enabled').contains(landingPageData.idir)
    cy.getByDataTest('landing-bceid-button').should('be.visible').should('be.disabled').contains(landingPageData.bceid)
  });

  it('should log in and be redirected to the select application page', () => {
    cy.login();
    cy.wait(3000);
    cy.url()
      .should('be.equal', `${Cypress.config("baseUrl")}/application`)
  })
});