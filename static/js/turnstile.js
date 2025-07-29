window.addEventListener('DOMContentLoaded', () => {
  const submitBtn = document.querySelector('.turnstile button[type="submit"]');
  if (submitBtn) {
    submitBtn.disabled = true;
  }
});



  function enableSubmit() {
  const submitButton = document.querySelector('.turnstile button[type="submit"]');
  if (submitButton) {
    submitButton.disabled = false;
  }
}
