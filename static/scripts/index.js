const { createApp } = Vue
const { reactive } = Vue

const pathName = window.location.pathname
const store = reactive({
    state: {
        isAuth: false,
        username: '',
    },
    getStateFromStorage() {
        const state = getFromStorage('state')
        const access_token = getFromStorage('access_token_cookie', 'COOKIES')
        if (!!state) {
            this.state = state
        }
        if (!access_token) {
            this.state = {
                isAuth: false,
                username: '',
            }
        } 
        // else {
        //     window.location.replace(window.location.origin + `/log_in`);
        // }
    },
    setState(state) {
        this.state = {...this.state, ...state}
        setInStorage('state', this.state)
    }
})

const redirect_to_login = (event) => {
    let host = window.location.origin
    window.location.replace(host + '/log_in');
}

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

const Login = {
    data() {
        return {
            store,
            username: '',
            password: '',
            error: '',
            requiredFields: [],
            passwordEyeOpen: true
        }
    },
    methods: {
        authenticate: async function (event) {
            this.error = ''
            event.preventDefault()
            let host = window.location.origin
            let fieldsValid = this.requiredFields.map(field => this.checkForInput(field))
            if (!_.every(fieldsValid)) return
            let credentials = {
                'username': this.username,
                'password': this.password
            }
            let headers = {'X-CSRFToken': this.csrf}
            let data = await request('POST', `/api/v1/authenticate`, headers, credentials)
            if (!_.isEmpty(data.message)) {
                this.error = data.message
                this.$refs.errors.classList.remove('disabled')
                return
            }
            const {username, ...rest} = data
            setInStorage('auth', rest, 'LOCAL')
            updateCookies('access_token_cookie')
            store.setState({
                isAuth: true,
                username: this.username
            })
            if (_.get(data, 'access_token_cookie')) {
                window.location.replace(host);
            }
        },
        checkForInput: function(input) {
            if (input.value == "") {
                input.classList.add("input_incorrect");
                if (input.name == 'password') {
                    this.$refs.passwordEye.classList.add('input_incorrect')
                }
                if (this.error) {
                    this.error += ` and ${input.placeholder}.`
                } else {
                    this.$refs.errors.classList.remove('disabled')
                    this.error = `Please enter your ${input.placeholder}`
                }
                return false
            }
            return true
        },
        resetInput: function(event) {
            event.target.classList.remove("input_incorrect")
            this.$refs.errors.classList.add('disabled')
            this.error = ''
            if (event.target.name == 'password') {
                this.$refs.passwordEye.classList.remove('input_incorrect')
            }
        },
        switchPasswordEye: function(event) {
            this.$refs.password.type = this.passwordEyeOpen ? 'text' : 'password'
            this.passwordEyeOpen = !this.passwordEyeOpen
        }
    },
    mounted() {
        this.username = this.$refs.username.value
        this.password = this.$refs.password.value
        this.requiredFields = [
            this.$refs.username,
            this.$refs.password
        ]
        this.$refs.password.classList.add('passwordInput')
        this.$refs.password.type = 'password'
        store.setState({
            isAuth: false,
            username: ''
        })
        removeFromStorage('auth', 'LOCAL')
    },
    delimiters: ['{', '}']
}

const EmailToReset = {
    data() {
        return {
            email: '',
            error: '',
            loading: false
        }
    },
    methods: {
        checkEmail: async function(event) {
            event.preventDefault()
            let fieldsValid = this.requiredFields.map(field => this.checkForInput(field))
            if (!_.every(fieldsValid)) return
            this.loading = true
            this.$refs.interactive.classList.add('mute')
            let headers = {"X-CSRFToken": `${this.csrf}`}
            let params = {'process': 'check_email', 'email': this.$refs.email.value}
            let data = await request('GET', `/api/v1/authenticate`, headers, params)
            this.loading = false
            this.$refs.interactive.classList.remove('mute')
            if (!_.isEmpty(data.message)) {
                switch (data.status) {
                    case 404:
                        this.error = "We weren't able to identify you by provided email."
                    default:
                        this.error = data.message
                }
                this.$refs.errors.classList.remove('disabled')
            } else {
                this.$refs.emailForm.classList.add('disabled')
                this.$refs.sentResetEmail.classList.remove('disabled')
            }
        },
        checkForInput: function(input){
            if (input.value == "") {
                input.classList.add("input_incorrect") ;
                if (this.error) {
                } else {
                    this.$refs.errors.classList.remove('disabled')
                    this.error = `Please enter your ${input.placeholder}`
                }
                return false
            }
            return true
        },
        redirect_to_login: redirect_to_login
    },
    mounted() {
        this.csrf = this.$refs.csrf.value
        this.requiredFields = [this.$refs.email]
        this.headers = {"X-CSRFToken": `${this.csrf}`}
    },
    delimiters: ['{', '}']
}

const PasswordReset = {
    data() {
        return {
            password: '',
            password2: '',
            csrf: '',
            error: '',
            passwordEyeOpen: true
        }
    },
    methods: {
        submitPasswordReset: async function(event) {
            event.preventDefault()
            this.password = this.$refs.password.value
            this.password2 = this.$refs.repeat_password.value
            let fieldsValid = this.requiredFields.map(field => this.checkForInput(field))
            if (!_.every(fieldsValid)) return
            let headers = {"X-CSRFToken": `${this.csrf}`}
            let params = {'password': this.password, 'repeat_password': this.password2}
            let data = await request('POST', `/api/v1/authenticate`, headers, params)
            if (!_.isEmpty(data.message)) {
                switch (data.status) {
                    case 404:
                        this.error = "We weren't able to find user."
                    default:
                        this.error = data.message
                }
                this.$refs.errors.classList.remove('disabled')
            } else {
                this.$refs.passForm.classList.add('disabled')
                this.$refs.sentResetEmail.classList.remove('disabled')
            }
        },
        checkForInput: function(input){
            if (input.value == "") {
                input.classList.add("input_incorrect");
                if (this.error) {
                    this.error += ` and ${input.placeholder}.`
                } else {
                    this.$refs.errors.classList.remove('disabled')
                    this.error = `Please enter your ${input.placeholder}`
                }
                return false
            } else if (!_.isEqual(this.password, input.value, this.password2)) {
                input.classList.add("input_incorrect");
                this.error = 'Passwords must be equal'
                this.$refs.errors.classList.remove('disabled')
                return false
            }
            return true
        },
        switchPasswordEye: function(event) {
            this.requiredFields.forEach(field => field.type = this.passwordEyeOpen ? 'text' : 'password')
            this.passwordEyeOpen = !this.passwordEyeOpen
        },
        resetInput: function(event) {
            event.target.classList.remove("input_incorrect")
            this.$refs.errors.classList.add('disabled')
            this.error = ''
        },
    },
    mounted() {
        this.csrf = this.$refs.csrf.value
        this.requiredFields = [this.$refs.password, this.$refs.repeat_password]
        this.requiredFields.forEach(field => {
            field.type = 'password'
        })
    },
    delimiters: ['{', '}']
}

const Posts = {
    data() {
        return {}
    },
    async created() {
        await this.getPosts()
    },
    methods: {
        getPosts: async () => {
            let data = await request('GET', window.location.href, with_auth=true)
        }
    }
}

const Messanger = {
    data() {
        return {
            store
        }
    }
}

const Knots = {
    data() {
        return {
            message: 'Hello Vue!',
            test: 'testwwww'
        }
    },
    delimiters: ['{', '}']
}

// const CreatePost = {
//     data() {
//         return {}
//     },
//     delimiters: ['{', '}']
// }

// createApp(CreatePost).mount('#createPost')
createApp(Messanger).mount('#messanger')
createApp(Login).mount('#login')
createApp(EmailToReset).mount('#emailToReset')
createApp(PasswordReset).mount('#passwordReset')
createApp(Knots).mount('#app')
createApp(Base).mount('#base')
// createApp(Posts).mount('#posts')