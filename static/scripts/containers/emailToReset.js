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
            let headers = {"X-CSRFToken": ``}
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
        this.requiredFields = [this.$refs.email]
        this.headers = {"X-CSRFToken": `${this.csrf}`}
    },
    delimiters: ['{', '}']
}

createApp(EmailToReset).mount('#emailToReset')