const Base = {
    data () {
        return {
            store,
        }
    },
    methods: {
        toProfile: () => {
            window.location.replace(window.location.origin + `/knot/${store.state.username}`);
        },
        logOut: async () => {
            let data = await request('DELETE', `/api/v1/authenticate`)
            removeFromStorage('auth', 'LOCAL')
            updateCookies('access_token_cookie')
            window.location.replace(window.location.origin + '/log_in')
        }
    },
    mounted() {
        store.getStateFromStorage()
    },
    delimiters: ['{', '}']
}

createApp(Base).mount('#base')