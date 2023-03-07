fetch('/env.json')
    .then((res) => res.json())
    .then((data) => {
        window.localStorage.setItem('env_data', JSON.stringify(data));
    });
