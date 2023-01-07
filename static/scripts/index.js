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
createApp(Knots).mount('#app')
