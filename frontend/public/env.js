fetch('/env.json', { cache: 'no-store'})
    .then((res) => res.json())
    .then((data) => {
        window.localStorage.setItem('env_data', JSON.stringify(data));
    });
