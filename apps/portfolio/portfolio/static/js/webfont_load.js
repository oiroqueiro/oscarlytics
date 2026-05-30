  WebFont.load({
    google: {
      api: 'https://fonts.googleapis.com/css2',
      families: ['Poppins:wght@400;500;600&display=swap'],
      version: 2
    },
    active: () => {sessionStorage.fontsLoaded = true}
  });
