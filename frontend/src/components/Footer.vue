<script setup lang="ts">
</script>

<template>
  <footer class="app-footer" id="footer">
    <div class="container">
      <div class="clearfix row">
        <div class="col-xs-12 col-sm-12 col-md-6">
          <ul class="gov-links">
            <li><a href="#">Home</a></li>
            <li><a href="http://www2.gov.bc.ca/gov/content/home/copyright" target="_blank" rel="noopener">Copyright</a></li>
            <li><a href="http://www2.gov.bc.ca/gov/content/home/disclaimer" target="_blank" rel="noopener">Disclaimer</a></li>
            <li><a href="http://www2.gov.bc.ca/gov/content/home/privacy" target="_blank" rel="noopener">Privacy</a></li>
            <li><a href="http://www2.gov.bc.ca/gov/content/home/accessibility" target="_blank" rel="noopener">Accessibility</a></li>
            <li>
              <a class="small-screen feedback-link" href="mailto:Fom.Admin@gov.bc.ca">Feedback</a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </footer>
</template>

<style lang="scss" scoped>
  @import "@/assets/styles/base.scss";

  .app-footer {
    border-top: 4px solid $gold;
    background: $footer-bg;
    color: $footer-color;

    .container {
      padding-top: 1.5rem;
      padding-right: 1.5rem;
      padding-bottom: 1.5rem;
      padding-left: 1.5rem;
      .gov-links {
        text-align: left;
      }
    }

  }
</style>
