(function () {
  function generateQrCodes() {
    if (typeof QRCode === 'undefined') {
      document.querySelectorAll('.donation-qr').forEach(function (el) {
        el.innerHTML = '<span class="donation-qr-error">QR unavailable</span>';
      });
      return;
    }

    document.querySelectorAll('.donation-qr[data-qr]').forEach(function (el) {
      var value = el.getAttribute('data-qr');
      if (!value || el.getAttribute('data-qr-ready') === '1') return;

      el.innerHTML = '';
      try {
        new QRCode(el, {
          text: value,
          width: 148,
          height: 148,
          colorDark: '#09090b',
          colorLight: '#ffffff',
          correctLevel: QRCode.CorrectLevel.M
        });
        el.setAttribute('data-qr-ready', '1');
      } catch (err) {
        el.innerHTML = '<span class="donation-qr-error">QR error</span>';
      }
    });
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }

    return new Promise(function (resolve, reject) {
      var textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.setAttribute('readonly', '');
      textarea.style.position = 'fixed';
      textarea.style.left = '-9999px';
      document.body.appendChild(textarea);
      textarea.select();
      try {
        var ok = document.execCommand('copy');
        document.body.removeChild(textarea);
        if (ok) resolve();
        else reject(new Error('copy failed'));
      } catch (err) {
        document.body.removeChild(textarea);
        reject(err);
      }
    });
  }

  function bindCopyButtons() {
    document.querySelectorAll('.donation-btn-copy[data-copy]').forEach(function (btn) {
      var resetTimer = null;

      btn.addEventListener('click', function () {
        var address = btn.getAttribute('data-copy');
        if (!address) return;

        copyText(address)
          .then(function () {
            var original = btn.getAttribute('data-label') || btn.textContent;
            btn.setAttribute('data-label', original);
            btn.textContent = 'Copied!';
            btn.classList.add('is-copied');
            btn.setAttribute('aria-live', 'polite');

            if (resetTimer) clearTimeout(resetTimer);
            resetTimer = setTimeout(function () {
              btn.textContent = btn.getAttribute('data-label') || 'Copy Address';
              btn.classList.remove('is-copied');
            }, 2000);
          })
          .catch(function () {
            btn.textContent = 'Copy failed';
            setTimeout(function () {
              btn.textContent = btn.getAttribute('data-label') || 'Copy Address';
            }, 2000);
          });
      });
    });
  }

  function init() {
    if (!document.querySelector('.support-page')) return;
    generateQrCodes();
    bindCopyButtons();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
