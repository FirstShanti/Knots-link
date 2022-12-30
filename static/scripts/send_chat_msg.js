var socket;
let window_size = $( window ).height()
let book_pc_size = (window_size - window_size%3) / 1.5
let prevDay = null;
var receivedAudio = new Audio('/static/audio/received.mp3');
var sendAudio = new Audio('/static/audio/send.mp3');
receivedAudio.volume = 0.2;
sendAudio.volume = 0.2;

$('.book_pc').css('height', `${book_pc_size}px`)
$('.chats_list').css('height', `${book_pc_size}px`)
$('.vl').css('height', `${book_pc_size}px`)

$(document).ready(function() {
    let root_url = $('#form_send_msg').attr('root_url')
    let chat_id = ''
    let chat_username = ''
    let to = $('.message_container').attr('username')
    let to_prev = ''
    let page = $('#page').attr('page')
    let url = '/api/v1/chat'
    let chat_active = ''
    get_chat_id()
    let isMute = false
    
    $('#mute').on('click', function() {
        isMute = !isMute
        receivedAudio.volume = isMute ? 0 : 0.2
        sendAudio.volume = isMute ? 0 : 0.2
    })

    $('.room_info').on('click', function() {
        $(to_prev).removeClass('current_chat_room')
        to = $(this).attr('value')
        leaveRoom(chat_id, socket.id)
        get_chat_id()
        joinRoom(chat_id, socket.id)
        get_msgs(true)
        $(this).addClass('current_chat_room')
        to_prev = this
        $(".book_pc").animate({scrollTop:9999}, 800);
    })


    function get_chat_id() {
        $.ajax({
            cache: false,
            url: '/api/v1/chat',
            type: 'POST',
            headers: {'username': to},
            dataType: 'json',
            // beforeSend: function(){
            //     $("#chat_loader").show();
            // },
            async: false,
            success: function (response) {   
                chat_id = response.chat_id
                chat_username = response.chat_username
            },
            error: function(error) {
                console.log(error);
            }
        })
    }

    socket = io.connect(root_url,
        {
            headers: {
                "access_token_cookie": getFromStorage('auth').access_token_cookie
            }
        }
    );

    socket.on('connect', function() {
        $('#form_send_msg').on('click', function(e) {
            e.preventDefault();
        })
        if (!!chat_id) {
            if (!!to_prev) {
                $(to_prev).removeClass('current_chat_room')
            }
            let selectedRoom = Array.from(document.querySelectorAll(`.room_info[value="${chat_username}"]`))
            $(selectedRoom[0]).addClass('current_chat_room')
            to_prev = selectedRoom[0]
            joinRoom(chat_id, socket.id)
        }
    });

    socket.on('status', ({status}) => {
        if (!status) {
            window.location.replace(window.location.origin + `/log_in`);
        }
    })

    // Trigger 'join' event
    function joinRoom(chat_id, socket_id) {
        let type = 'service'
        socket.emit('join', {chat_id, socket_id, type})
    }

    function sendText(chat_id, socket_id, msg) {
        let type = 'msg'
        socket.emit('text', {chat_id, socket_id, msg, type})
    }


    function leaveRoom(room, socket_id) {
        let type = 'service'
        socket.send('leave', {chat_id, socket_id, type})
    }

    socket.on('message', ({data, messages}) => {
        if (data.type == 'service' & data.socket_id != socket.id) {
            $('.book_pc').append(`<div class="text-muted">${data.msg}</div>`);
        } else {
            if ( data.type == 'msg' ) {
                update_msgs(messages, false)
                if (messages[0].author_username == to && !isMute) {
                    receivedAudio.play()
                }
                $(`.room_last_msg#${to}`).text(truncate(data.msg, 30))
                $(".book_pc").animate({scrollTop:9999}, 800);
            }
        }
        return false;
    });

    function get_msgs(clear) {
        $.getJSON(
            '/api/v1/chat',
            {chat_id, page, 'another_username': to},
            function(response) {
                update_msgs(response.messages, clear)
                $(".loader").hide();
            }
        )}

    function get_msg_html(side, msg, date) {
        return `
            <div class='msg_container ${side}'>
                <div class='msg_${side}'>
                    <div>${msg}</div>
                    <div style="font-size: 10px; color: grey; float: ${side}">${date}</div>
            </div></div>`
    }

    function update_msgs(messages, clear=false) {
        var prev_content = $('.book_pc')
        if (clear) {
            prev_content.empty()
        }
        for (var i in messages) {
            let date = new Date(messages[i].created * 1000);
            let day = date.getDay()

            let msg_content = messages[i].text
            let msg_date = date.format("HH:MM")

            if (!prevDay || prevDay != day) {
                prev_content.append(
                    `<div class='new-date'>
                        ${date.format("dd.m.yy")}
                    </div>`
                )
                prevDay = day
            }

            if ( messages[i].author_username == to ) {
                prev_content.append(get_msg_html('left', msg_content, msg_date));
            } else {
                prev_content.append(get_msg_html('right', msg_content, msg_date));  
            }
        }
    }

    get_msgs(false)
    $(".book_pc").animate({scrollTop:9999}, 800);

    $('button.send_message_button').on('click', () => {
        var msg = $('#message_textarea').val()
        if ( msg ) {
            sendAudio.play()
            sendText(chat_id, socket.id, msg)
            $('#message_textarea').val('');
        } else {
            // change input dic to red color VALIDATION
        }
    });

    function truncate(str, maxlength) {
    return (str.length > maxlength) ?
        str.slice(0, maxlength - 1) + '…' : str;
    }

})


// // Пример отправки GET запроса:
async function getData(url = '', chat_id = '', page = 1, username = '') {
  // Default options are marked with *
  const response = await fetch(url, {
    method: 'GET', // *GET, POST, PUT, DELETE, etc.
    mode: 'cors', // no-cors, *cors, same-origin
    cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
    credentials: 'same-origin', // include, *same-origin, omit
    headers: {
      'Content-Type': 'application/json',
      'chat_id': chat_id,
      'another_username': username,
      'page': page,
      // 'Content-Type': 'application/x-www-form-urlencoded',
    },
    redirect: 'follow', // manual, *follow, error
    referrerPolicy: 'no-referrer', // no-referrer, *client
  });
  return await response.json(); // parses JSON response into native JavaScript objects
}


// // Пример отправки POST запроса:
// async function postData(url = '', data = {}) {
//   // Default options are marked with *
//   const response = await fetch(url, {
//     method: 'POST', // *GET, POST, PUT, DELETE, etc.
//     mode: 'cors', // no-cors, *cors, same-origin
//     cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
//     credentials: 'same-origin', // include, *same-origin, omit
//     headers: {
//       'Content-Type': 'application/json'
//       // 'Content-Type': 'application/x-www-form-urlencoded',
//     },
//     redirect: 'follow', // manual, *follow, error
//     referrerPolicy: 'no-referrer', // no-referrer, *client
//     body: JSON.stringify(data) // body data type must match "Content-Type" header
//   });
//   return await response.json(); // parses JSON response into native JavaScript objects
// }

