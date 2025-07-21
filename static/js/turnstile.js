  document.body.addEventListener('htmx:afterSwap', function(evt) {
    // If Turnstile is present and the widget is not rendered yet
    if (typeof turnstile !== 'undefined') {
      document.querySelectorAll('.cf-turnstile').forEach((el) => {
        if (!el.hasAttribute('data-rendered')) {
          turnstile.render(el, {
            sitekey: el.getAttribute('data-sitekey')
          });
          el.setAttribute('data-rendered', 'true');
        }
      });
    }
  });
