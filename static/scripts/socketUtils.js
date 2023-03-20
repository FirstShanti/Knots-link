joinRoom = (socket, receiver) => {
    let type = 'service'
    let token = getCookie('access_token_cookie') || ''
    socket.emit('join', {receiver, 'socket_id': socket.id, type, token})
}

sendText = (socket, receiver, msg) => {
    let type = 'msg'
    let token = getCookie('access_token_cookie') || ''
    if (socket.connected) {
        socket.emit('text', {receiver, 'socket_id': socket.id, msg, type, token})
    }
}

reconnect = (socket) => {
    let waitReconnect = setInterval(() => {
        if (socket.connected) {
            clearInterval(waitReconnect)
            joinRoom(socket, this.activeChat)
        } else {
            socket.connect();
        }
    }, 5000)
}

const SocketInstance = io.connect(window.location.href,
    {
        headers: {
            "access_token_cookie": getCookie('access_token_cookie') || ''
        }
    }
)