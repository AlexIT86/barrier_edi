// Auto-dismiss bootstrap alerts after 5 seconds
(function () {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach((el) => {
    setTimeout(() => {
      if (window.bootstrap && bootstrap.Alert) {
        const alert = new bootstrap.Alert(el);
        try { alert.close(); } catch (e) {}
      } else {
        el.classList.add('d-none');
      }
    }, 5000);
  });
})();

// Simple confirm helper for delete actions
document.addEventListener('click', function (e) {
  const target = e.target;
  if (target && target.matches('[data-confirm]')) {
    const msg = target.getAttribute('data-confirm') || 'Ești sigur?';
    if (!confirm(msg)) {
      e.preventDefault();
      e.stopPropagation();
    }
  }
});

// Sidebar toggle
(function(){
  const sidebar = document.getElementById('sidebar');
  const toggle = document.getElementById('sidebarToggle');
  const wrapper = document.querySelector('.content-wrapper');
  if (!sidebar || !toggle || !wrapper) return;

  function setCollapsed(collapsed){
    if (collapsed) {
      sidebar.classList.add('collapsed');
      wrapper.classList.add('collapsed');
      if (window.innerWidth < 992) sidebar.classList.remove('show');
    } else {
      sidebar.classList.remove('collapsed');
      wrapper.classList.remove('collapsed');
      if (window.innerWidth < 992) sidebar.classList.add('show');
    }
  }

  // initial state for mobile
  if (window.innerWidth < 992) setCollapsed(true);

  toggle.addEventListener('click', function(){
    const isCollapsed = sidebar.classList.contains('collapsed');
    setCollapsed(!isCollapsed);
  });

  window.addEventListener('resize', function(){
    if (window.innerWidth < 992) setCollapsed(true);
    else setCollapsed(false);
  });
})();
