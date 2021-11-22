var socket;
let window_size = $( window ).height()
let book_pc_size = (window_size - window_size%3) / 1.5
$('.book_pc').css('height', `${book_pc_size}px`)
$('.chats_list').css('height', `${book_pc_size}px`)
$('.vl').css('height', `${book_pc_size}px`)

$(document).ready(function() {
    let root_url = $('#form_send_msg').attr('root_url')
    let chat_id = ''
    let to = $('.message_container').attr('username')
    let to_prev = ''
    let page = $('#page').attr('page')
    let url = '/api/v1/chat'
    let chat_active = ''
    get_chat_id()

    $('.room_info').click(function() {
        if (to_prev) {
            $(to_prev).removeClass('current_chat_room')
        }
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
            beforeSend: function(){
                $("#loader").show();
            },
            async: false,
            success: function (response) {   
                chat_id = response.chat_id
                console.log('chat_id: ', chat_id)
            },
            error: function(error) {
                console.log(error);
            }
        })
    }

    socket = io.connect(root_url);

    socket.on('connect', function() {
        $('#form_send_msg').click(function(e) {
            e.preventDefault();
        })
        joinRoom(chat_id, socket.id)
    })

    // Trigger 'join' event
    function joinRoom(chat_id, socket_id) {
        let type = 'service'
        socket.emit('join', {chat_id, socket_id, type})
    }

    function sendText(chat_id, socket_id, msg) {
        let type = 'msg'
        socket.emit('text', {chat_id, socket_id, msg, type})
        // console.log('sended')
    }


    function leaveRoom(room, socket_id) {
        let type = 'service'
        socket.send('leave', {chat_id, socket_id, type})
    }

    socket.on('message', data => {
        if (data.type == 'service' & data.socket_id != socket.id) {
            $('.book_pc').append(`<div class="text-muted">${data.msg}</div>`);
        } else {
            if ( data.type == 'msg' ) {
                var myAudio = new Audio('/static/audio/notification3.mp3');
                myAudio.volume = 0.2;
                if ( data.socket_id == socket.id ) {
                    $('.book_pc').append(`<div class='msg_container right'><div class='msg_right'>${data.msg}</div></div>`);
                    $(".book_pc").animate({scrollTop:9999}, 800);
                } else {
                    $('.book_pc').append(`<div class='msg_container left'><div class='msg_left'>${data.msg}</div></div>`);
                    myAudio.play();
                    $(".book_pc").animate({scrollTop:9999}, 800);
                }
            }
        } 
        return false;
    });

    function get_msgs(clear) {
        console.log('in get')
        $.getJSON(
            '/api/v1/chat',
            {chat_id, page, 'another_username': to},
            function(response) {
                update_msgs(response, clear)
            }
        )}

    function update_msgs(response, clear=false) {
        var prev_content = $('.book_pc')
        if (clear) {
            prev_content.empty()        }
        for (var i in response.data) {
            if ( response.data[i].author_username == to ) {
                prev_content.append(`<div class='msg_container left'><div class='msg_left'>${response.data[i].text}</div></div>`);
                // $(".book_pc").animate({scrollTop:9999}, 800);
            } else {
                prev_content.append(`<div class='msg_container right'><div class='msg_right'>${response.data[i].text}</div></div>`);  
                // $(".book_pc").animate({scrollTop:9999}, 800);
            }
        }
    }

    get_msgs(false)
    $(".book_pc").animate({scrollTop:9999}, 800);

    // var get = getData('/api/v1/chat', chat_id, page, to)
    //     .then((data) => {
    //         console.log(data['data'])
    //         return data['data']; // JSON data parsed by `response.json()` call

    //       })
    //     .then((data) => {
    //         var prev_content = $('.book_pc').val()
    //         // ${Date.parse(msgs[i].createdAt)}: 
    //         for (var i in data) {
    //             if ( data[i].msg != 'new Knot conected' ) {
    //                 prev_content += `<div class="msg_left">
    //                                 ${data[i].msg}
    //                             </div>` 
    //             }
    //         }
    //         $('.book_pc').empty().append(prev_content)
    //         $('#message_textarea').val()
    //         $(".book_pc").animate({scrollTop:9999}, 800);
    //     })
    // }
    // get.then((data) => {
    //     console.log('response data: ', data)
    //     updatePosts(data)
    // })
    // updatePosts(getData)

    $('button.send_message_button').on('click', () => {
        var msg = $('#message_textarea').val()
        if ( msg ) {
            sendText(chat_id, socket.id, msg)
            $('#message_textarea').val('');
        } else {
            // change input dic to red color VALIDATION
        }
    });

})


// // Пример отправки GET запроса:
async function getData(url = '', chat_id = '', page = 1, username = '') {
  // Default options are marked with *
  // console.log('send get request: ', url, chat_id, page, username)
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

