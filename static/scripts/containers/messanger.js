var receivedAudio = new Audio('/static/audio/received.mp3');
var sendAudio = new Audio('/static/audio/send.mp3');
receivedAudio.volume = 0.2;
sendAudio.volume = 0.2;

let window_size = $( window ).height()
let book_pc_size = (window_size - window_size%3) / 1.5

$('.book_pc').css('height', `${book_pc_size}px`)
$('.chats_list').css('height', `${book_pc_size}px`)
$('.vl').css('height', `${book_pc_size}px`)


const Messanger = {
    data () {
        return {
            store,
            chats: [],
            activeChat: undefined,
            chatsData: {},
            msgDrafts: {},
            dayDate: '',
            loading: true,
            sidebarChatsOpen: false,
            isMobile: false
        }
    },
    sockets: {
        connect() {
            // joinRoom(this.$socket, this.activeChat)
        },
        disconnect() {
            reconnect(this.$socket)
        },
        message(data) {
            const msg = data.message
            const receiver = data.data.receiver
            if (store.state.username != msg.author_username) {
                receivedAudio.play()
                msg.side = 'left'
            }
            let chatFromList = _.find(this.chats, {'uuid': receiver})
            let chatIndex = _.indexOf(this.chats, chatFromList)
            this.chats[chatIndex].last_msg = msg
            this.chatsData[receiver].chatMsgs.push(msg)
            this.chatsData[receiver].unread_msgs += msg.side == 'left' ? 1 : 0
            this.chats = _.orderBy(this.chats, ['edited'], ['desc'])
            if (this.activeChat == receiver && msg.side == 'right') {
                this.scrollMsgsList(true)
            }
        },
        status(data) {
            if (!data.status) {
                Base.methods.logOut()
            } else if (!_.isEmpty(data.message)) {
                console.error(data.message)
            }
        }
    },
    methods: {
        async getChats() {
            let data = await request('GET', '/api/v1/chat')
            let chatsData = {}
            this.chats = data
            this.activeChat = !!this.activeChat ? this.activeChat : _.get(_.first(data), 'uuid')
            Object.values(data).map((chat, idx) => {
                chatsData[chat.uuid] = {
                    'uuid': chat.uuid,
                    'nextPage': 1,
                    'prevPage': null,
                    'chatMsgs': [],
                    'unread_msgs': chat.unread_msgs
                }
            })
            this.chatsData = chatsData
        },
        async getMessages(getOldMsgs=false) {
            let headers = {
                'receiver': this.activeChat,
                'page': _.get(this.chatsData[this.activeChat], 'nextPage', 1)
            }
            let isNextPage = _.isNumber(this.chatsData[this.activeChat]?.nextPage)
            let isFirstRequest = _.isNull(this.chatsData[this.activeChat]?.prevPage)
            if (getOldMsgs && isNextPage || isNextPage && isFirstRequest) {
                this.loading = true
                let chatData = await request('GET', '/api/v1/messages', headers)
                let oldMsgs = this.chatsData[this.activeChat].chatMsgs
                let newMsgs = _.sortBy(chatData.msgs.filter(msg => !oldMsgs.map(m => m.uuid).includes(msg.uuid)), 'created')
                let prevDay = null;
                newMsgs.forEach((msg, idx) => {
                    let date = new Date(msg.created);
                    let day = date.getDay()
                    let previousMonthDate = _.find(oldMsgs, {'monthDate': date.format("dd.mm.yy")})
                    if (prevDay == null || prevDay != day || !!previousMonthDate) {
                        _.get(previousMonthDate, 'monthDate') ? delete previousMonthDate.monthDate : null 
                        msg.monthDate = date.format("dd.mm.yy")
                        prevDay = day
                    }
                })
                this.chatsData[this.activeChat].chatMsgs = [...newMsgs, ...oldMsgs]
                this.chatsData[this.activeChat].prevPage = this.chatsData[this.activeChat].nextPage
                this.chatsData[this.activeChat].nextPage = chatData.nextPage
                this.chatsData[this.activeChat].unread_msgs = this.chatsData[this.activeChat].chatMsgs.filter(msg => msg.side == 'left' && !msg.is_read).length
            }
            this.loading = false
        },
        async handleMsgsListScroll(event) {
            let scrollMax = event.target.scrollHeight - event.target.clientTop
            if (this.$refs.msgs_list_container.scrollTop == 0 && this.chatsData[this.activeChat].scrollPosition > 0) {
                await this.getMessages(true)
                scrollMax = event.target.scrollHeight - event.target.clientTop
                this.chatsData[this.activeChat].scrollPosition = scrollMax - this.chatsData[this.activeChat].scrollMaxPosition - 50
                this.chatsData[this.activeChat].scrollMaxPosition = scrollMax
                this.scrollMsgsList()
            } else {
                this.chatsData[this.activeChat].scrollPosition = event.target.scrollTop == 0 ? this.chatsData[this.activeChat].scrollMaxPosition : event.target.scrollTop
                this.chatsData[this.activeChat].scrollMaxPosition = scrollMax
            }
            Array.from(this.$refs[`msgs_list_container`].children).reverse().map(el => {
                if (Utils.isElementInView(el, true)) {
                    setTimeout(() => {
                        this.readMsg(el.id)
                    }, 4000)
                }
            })
        },
        scrollMsgsList(newMsg=false) {
            let scrollMax = this.$refs.msgs_list_container.scrollHeight - this.$refs.msgs_list_container.clientTop
            if (this.chatsData[this.activeChat].scrollPosition != undefined && !newMsg) {
                this.$nextTick(() => {
                    this.$refs.msgs_list_container.scrollTop = this.chatsData[this.activeChat].scrollPosition
                });
            } else {
                this.$nextTick(() => {
                    this.$refs.msgs_list_container.scrollTop = scrollMax
                    this.chatsData[this.activeChat].scrollPosition = scrollMax
                });
            }
        },
        handleSendMsg(event) {
            if (!_.isEmpty(this.msgDrafts[this.activeChat])) {
                sendText(this.$socket, this.activeChat, this.msgDrafts[this.activeChat])
                sendAudio.play()
                this.msgDrafts[this.activeChat] = ''
            }
        },
        async readMsg(_msg) {
            let msg = _msg
            if (typeof(_msg) == 'string') {
                msg = _.find(this.chatsData[this.activeChat].chatMsgs, {'uuid': _msg})
            }
            if (!!msg && !msg.loading && msg.side == 'left' && !msg.is_read) {
                let params = {
                    'uuid': msg.uuid,
                    'parameter': MSG_PARAMETERS['UPDATE'],
                    'data': JSON.stringify({
                        'is_read': true
                    })
                }
                msg.loading = true
                let data = await request('POST', '/api/v1/messages', params)
                if (data.message == 'ok') {
                    msg.is_read = true
                    this.chatsData[this.activeChat].unread_msgs -= 1
                }
                msg.loading = false
            }
        },
        handleInputActive() {
            let msgsCopy = [...this.chatsData[this.activeChat].chatMsgs].reverse()
            msgsCopy.forEach(msg => {
                setTimeout(() => {
                    this.readMsg(msg)
                }, 500)
            });
        },
    },
    async mounted() {
        this.isMobile = isMobile()
        await this.getChats()
        if (!!_.get(this.$refs.selectedChat, 'attributes.anotherUser.value', undefined)) {
            this.activeChat = this.$refs.selectedChat.attributes.anotherUser.value
        }
        joinRoom(this.$socket, getFromStorage('uuid'))
    },
    watch: {
        chats(newChats, oldChats) {
            console.log('newChats')
        },
        chatsData(newChatsData, oldChatsData) {
            console.log('newChatsData: ')
        },
        async activeChat(newActiveChat, oldActiveChat) {
            await this.getMessages()
            if (_.get(this.chatsData, `${newActiveChat}.chatMsgs.length`, []) > 0) {
                this.scrollMsgsList()
            }
        },
    },
    delimiters: ['{', '}']
}

const MessangerApp = createApp(Messanger).use(VueSocketio, SocketInstance)

MessangerApp.config.globalProperties.$filters = {
    monthDate(value) {
        return !!value && value.format("dd.m.yy")
    },
    msgTime(value) {
        return moment(value).format('HH:MM')
    },
    truncate(value) {
        const maxlength = 30
        return (!_.isEmpty(value) && value.length > maxlength) ?
            value.slice(0, maxlength - 1) + '…' : value;
    }
}

MessangerApp.mount('#messanger')
