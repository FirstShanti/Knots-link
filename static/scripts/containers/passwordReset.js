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
            let headers = {"X-CSRFToken": ``}
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
        this.requiredFields = [this.$refs.password, this.$refs.repeat_password]
        this.requiredFields.forEach(field => {
            field.type = 'password'
        })
    },
    delimiters: ['{', '}']
}

createApp(PasswordReset).mount('#passwordReset')