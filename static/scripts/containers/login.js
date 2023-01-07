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

createApp(Login).mount('#login')