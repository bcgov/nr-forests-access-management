<script setup lang="ts">
</script>

<template>
  <footer class="app-footer" id="footer">
    <div>
      <div class="clearfix row">
        <div class="col-xs-12 col-sm-12 col-md-12">
          <ul class="gov-links">
            <li><a href="#" title="Home" @click="$router.push({ name: 'home' })">Home</a></li>
            <li><a href="http://www2.gov.bc.ca/gov/content/home/copyright" target="_blank" rel="noopener">Copyright</a></li>
            <li><a href="http://www2.gov.bc.ca/gov/content/home/disclaimer" target="_blank" rel="noopener">Disclaimer</a></li>
            <li><a href="http://www2.gov.bc.ca/gov/content/home/privacy" target="_blank" rel="noopener">Privacy</a></li>
            <li><a href="http://www2.gov.bc.ca/gov/content/home/accessibility" target="_blank" rel="noopener">Accessibility</a></li>
            <li>
              <a href="mailto:SIBIFSAF@Victoria1.gov.bc.ca">Contact Us</a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </footer>
</template>

<style lang="scss" scoped>
  @import "./footer.scss";
</style>
