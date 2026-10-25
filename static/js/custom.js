/**
 * Custom JavaScript shared across the ProjectV3 Mood Tracker templates.
 *
 * Shared helpers live here. Page-specific behaviour should be added inside
 * the `{% block extra_js %}` of the individual templates instead of growing
 * this file.
 */
(function () {
  'use strict';

  window.DH = window.DH || {};
  window.DH.custom = window.DH.custom || {};

  /**
   * Read a value from a browser cookie.
   */
  window.DH.custom.getCookie = function (name) {
    var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
  };

  /**
   * Read the Django CSRF token from the csrftoken cookie.
   */
  window.DH.custom.getCsrfToken = function () {
    return window.DH.custom.getCookie('csrftoken');
  };

  /**
   * Fetch JSON from a Django AJAX endpoint, attaching the CSRF token.
   */
  window.DH.custom.fetchJson = function (url, options) {
    var settings = Object.assign({
      credentials: 'same-origin',
      headers: {
        'X-CSRFToken': window.DH.custom.getCsrfToken(),
        'Content-Type': 'application/json',
      },
    }, options || {});

    return fetch(url, settings).then(function (response) {
      return response.json().then(function (data) {
        return { response: response, data: data };
      });
    });
  };
})();
