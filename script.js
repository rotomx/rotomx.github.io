(() => {
  // scroll reveal
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        e.target.classList.add('in');
        io.unobserve(e.target);
      }
    });
  }, { threshold: .12 });
  document.querySelectorAll('.reveal').forEach((el) => io.observe(el));

  // mobile menu toggle
  const toggle = document.getElementById('navtoggle');
  const links = document.getElementById('navlinks');
  const setOpen = (open) => {
    links.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', String(open));
  };
  if (toggle && links) {
    toggle.addEventListener('click', () => setOpen(!links.classList.contains('open')));
    links.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => setOpen(false)));
  }
})();
