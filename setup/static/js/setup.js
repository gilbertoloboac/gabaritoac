document.addEventListener('DOMContentLoaded', function () {
  var revealElements = document.querySelectorAll('[data-reveal]');
  if (!revealElements.length) return;

  var animMap = {
    'fade-in-up': 'fade-in-up 0.6s ease-out both',
    'fade-in': 'fade-in 0.5s ease-out both',
    'scale-in': 'scale-in 0.5s ease-out both',
  };

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        var el = entry.target;
        var type = el.getAttribute('data-reveal') || 'fade-in-up';
        var delay = el.getAttribute('data-delay') || '0';
        el.style.opacity = '0';
        el.style.animation = animMap[type] || animMap['fade-in-up'];
        el.style.animationDelay = delay + 'ms';
        el.classList.add('revealed');
        observer.unobserve(el);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  revealElements.forEach(function (el) { observer.observe(el); });
});
