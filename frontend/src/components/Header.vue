<script setup lang="ts">
</script>

<template>
  <header class="app-header" id="header">
    <nav class="navbar navbar-expand-md justify-content-between">
      <a class="navbar-brand" title="Forest Access Management" href="https://www2.gov.bc.ca" style="margin-right: 0;">
        <img
            class="nav-logo img-fluid d-none d-sm-block"
            src="@/assets/images/17_gov3_bc_logo.svg"
            width="152" height="55"
            alt="B.C. Government Logo">
      </a>

      <button class="navbar-toggler" type="button" title="Toggle Main Navigation"
        aria-controls="navbarNav" 
        aria-expanded="false" 
        aria-label="Toggle navigation"
        data-toggle="collapse"
        data-target="#navbarNav">
        <em class="material-icons">menu</em>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav">
          <li class="nav-item">
            <a class="nav-link" title="Logout">
              <span>Logout</span>
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" title="About Us">
              <span>About</span>
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" title="Contact Us">
              <span>Contact Us</span>
            </a>
          </li>
        </ul>
      </div>
    </nav>
  </header>

  <div class="wrapper">
    
    <nav>
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/application">Select Application</RouterLink>
      <RouterLink to="/manage">Manage Access</RouterLink>
      <RouterLink to="/about">About</RouterLink>
    </nav>
  </div>

</template>

<style lang="scss" scoped>
  @import "@/assets/styles/base.scss";

.app-header {
  @include clearfix;

  position: relative;
  padding: 0;
  border-bottom: 2px solid $gold;
  background: $header-bg;
  color: $header-font-color;
  z-index: 1005;
}

// Navbar Toggle Button
.navbar-toggler {
  margin-right: 0.5rem;
  padding: 0.5rem 0.4rem;
  border: 2px solid $gold;
  color: $gold;
  font-size: medium;
  font-weight: 600;
  outline: none; // override user agent stylesheet default

  &:hover {
    cursor: pointer;
  }

  &.collapsed {
    border: 2px solid transparent;
    color: #fff;
  }

  i {
    float: left;
    margin-top: -0.25rem;
    margin-bottom: -0.25rem;

    + span {
      display: none;
      margin-top: 1px;
      margin-left: 0.25rem;
      font-size: $mn-font-size;
      font-weight: 700;
      vertical-align: top;
    }
  }
}

@media (min-width: 420px) {
  .navbar-toggler {
    i {
      + span {
        display: inline-block;
      }
    }
  }
}

// NAVBAR
.navbar {
  padding: 0;
  background-color: $header-bg;
  z-index: 1000;

  .navbar-nav {
    margin-top: 0.5rem;

    .nav-link {
      position: relative;
      z-index: 1001; // +1 to keep above dropdown menus
      padding: 0.875rem 1rem;
      border-top: 1px solid $mn-border-color;
      color: $mn-color;
      text-transform: uppercase;
      white-space: nowrap;
      font-size: $mn-font-size;
      font-weight: 700;
      cursor: pointer;
    }

    .dropdown {
      &.show {
        .dropdown-toggle {
          color: $gold;
        }
      }
    }

    .dropdown-menu {
      margin-top: -0.4rem;
      padding-top: 0;
      border: none;
      border-radius: 0;
      background-color: transparent;

      .dropdown-item {
        padding: 0.5rem 1rem;
        color: $mn-color;
        font-size: $mn-dropdown-menu-size;
        white-space: normal;
        cursor: pointer;

        strong {
          font-weight: 600;
          transition: color 0.2s ease-out;
        }

        .dd-item-desc {
          display: block;
          font-size: small;
          opacity: 0.5;
          transition: opacity 0.2s ease-out;
        }

        &:focus,
        &:hover {
          background: transparent;

          strong {
            color: $mn-hover-color;
          }

          .dd-item-desc {
            opacity: 1;
          }
        }
      }
    }
  }

  .navbar-environment {
    padding: 0 2rem;
    font-weight: 700;
    font-size: 2rem;
    background-color: #063;
    border-radius: 1.5rem;
  }

  .navbar-collapse {
    overflow: hidden;
  }

  @media screen and (max-width: 440px) {
    .navbar-environment {
      padding: 0 1em;
      font-size: 1em;
    }
  }
}

@media (min-width: 768px) {
  .navbar {
    background: transparent;

    .navbar-nav {
      margin-top: 0;

      .nav-link {
        height: 4.2rem; // 60px to match the branding height
        padding: 0.5rem 0.75rem !important;
        border-top: none;

        span {
          margin-top: 0.9rem;
          display: inline-block;
        }

        &:hover {
          background-color: #002663;
        }
      }

      > li {
        .dropdown-menu {
          margin: 0;
          padding: 0.5rem;
          min-width: 16rem;
          background-color: #002663;

          &.dm-sm {
            min-width: 12rem;
          }

          .dropdown-item {
            padding: 0.5rem;
          }
        }

        &.dropdown {
          &.show {
            .dropdown-toggle {
              color: $mn-color;
            }

            .dropdown-menu {
              display: none;
            }
          }

          &:hover {
            > a,
            > a:hover,
            > a:focus {
              background-color: #002663;
              border: none;
            }

            .dropdown-menu {
              display: block;
            }
          }
        }
      }
    }
  }

  .navbar-collapse {
    flex-grow: 0;
  }
}

// Navbar Brand
.navbar-brand {
  height: 3.4375rem;
  background-image: url("../../assets/images/bcgov-header-vert-SM.png");
  background-position: 8px center;
  background-repeat: no-repeat;
  white-space: normal;
}

.navbar-brand__title {
  margin-top: 0.35rem;
  margin-left: 75px;
  display: inline-block;
  color: #fff;
  line-height: 1.1rem;
  font-size: 0.875rem;

  .wb {
    display: block;
  }
}

.navbar-brand__version {
  margin-top: -0.1rem;
  display: inline-block;
  color: $gold;
  font-size: 0.5rem;
  font-weight: 700;
  vertical-align: top;
}

@media (min-width: 1200px) {
  .navbar-brand {
    height: 4.2rem;
    background-image: url("../../assets/images/bcgov-header-vert-MD.png");
    background-position: 10px center;
  }

  .navbar-brand__title {
    margin-left: 88px;
    margin-top: 0.65rem;
    line-height: 1.2rem;
    font-size: 1rem;
    font-weight: 400;
  }

  .navbar-brand__version {
    font-size: 0.6rem;
  }
}


  // header {
  //   line-height: 1.5;
  //   max-height: 100vh;
  // }

  // .logo {
  //   display: block;
  //   margin: 0 auto 2rem;
  // }

  // nav {
  //   width: 100%;
  //   font-size: 12px;
  //   text-align: center;
  //   margin-top: 2rem;
  // }

  // nav a.router-link-exact-active {
  //   color: var(--color-text);
  // }

  // nav a.router-link-exact-active:hover {
  //   background-color: transparent;
  // }

  // nav a {
  //   display: inline-block;
  //   padding: 0 1rem;
  //   border-left: 1px solid var(--color-border);
  // }

  // nav a:first-of-type {
  //   border: 0;
  // }

  // @media (min-width: 1024px) {
  //   header {
  //     display: flex;
  //     place-items: center;
  //     padding-right: calc(var(--section-gap) / 2);
  //   }

  //   .logo {
  //     margin: 0 2rem 0 0;
  //   }

  //   header .wrapper {
  //     display: flex;
  //     place-items: flex-start;
  //     flex-wrap: wrap;
  //   }

  //   nav {
  //     text-align: left;
  //     margin-left: -1rem;
  //     font-size: 1rem;

  //     padding: 1rem 0;
  //     margin-top: 1rem;
  //   }
  // }
</style>
