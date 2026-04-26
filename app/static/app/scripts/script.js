document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.nav-tab[data-tab]').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      tab.classList.add('active');
      const target = document.getElementById(tab.getAttribute('data-tab') + '-tab');
      if (target) target.classList.add('active');
    });
  });
});
