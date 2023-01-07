const request = async (method, url, headers, params, with_auth) => {
    let host = window.location.origin
    new_url = new URL(`${host}${url}`)
    headers = {...headers, apiRequest: true}
    const requestOptions = {
        method: method,
        headers: headers,
    };
    if (with_auth) {
        requestOptions.headers = {
            ...headers,
            'Authorization': `Bearer ${_.get(getFromStorage('token'), access_token)}`
        }
    }
    if (method == 'POST' && !_.isEmpty(params)) {
        requestOptions.body = JSON.stringify(params)
        requestOptions.headers = {
            ...requestOptions.headers,
            'Content-Type': 'application/json'
        }
    } else if (method == 'GET' && !_.isEmpty(params)) {
        new_url.search = new URLSearchParams(params).toString()
    }
    let response = await fetch(new_url, requestOptions)
        .then(async response => {
            let data = await response.json();
            // // check for error response
            if (!response.ok) {
                // get error message from body or default to response statusText
                data.message = (data && data.message) || response.statusText;
                // return Promise.reject(error);
            }
            return Promise.resolve(data)
        })
        .catch(error => {
            return error;
        });
    return response
}

const updateCookies = (key, maxAge) => {
    const auth = getFromStorage('auth', type='LOCAL')
    if (!!auth) {
        Object.keys(auth).filter(k => key ? k == key : true).map(k => document.cookie = `${k}=${auth[k]}; max-age=${maxAge || 2592000}`)
    } else {
        document.cookie = `${key}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/`
    }
}

// const isAuth = () => {
//     const auth = getFromStorage('auth', type='LOCAL')
//     const now = moment.utc().unix()
//     return !!auth && auth.expired_at > now
// }

const redirect_to_login = (event) => {
    let host = window.location.origin
    window.location.replace(host + '/log_in');
}