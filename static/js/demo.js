/**
 * Demo scripts for the authentication pages (login / register).
 *
 * The lockout countdown and the password visibility toggles are currently
 * wired inline in the auth templates. This file is the home for any additional
 * demo / page-specific behaviour added to the auth screens later.
 */
(function () {
  'use strict';

  window.DH = window.DH || {};
  window.DH.demo = window.DH.demo || {};

  window.DH.demo.init = function () {
    // Demo hook: runs once the auth screen has finished loading.
    if (window.console && window.console.debug) {
      window.console.debug('Auth screen initialised');
    }
  };

  document.addEventListener('DOMContentLoaded', function () {
    window.DH.demo.init();
  });
})();
