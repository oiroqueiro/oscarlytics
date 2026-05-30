// File: static/js/theme_switch.js

document.addEventListener('DOMContentLoaded', () => {
  var darkMode = false;

  if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    darkMode = true;
  }

  if (localStorage.getItem('theme') === 'dark') {
    darkMode = true;
  } else if (localStorage.getItem('theme') === 'light') {
    darkMode = false;
  }

  if (darkMode) {
    document.body.classList.toggle('dark');
  }

  var themeSwitch = document.querySelectorAll('.theme-switcher');
  [].forEach.call(themeSwitch, function (ts) {
    ts.addEventListener('click', () => {
      document.body.classList.toggle('dark');
      localStorage.setItem(
        'theme',
        document.body.classList.contains('dark') ? 'dark' : 'light'
      );
    });
  });
});

