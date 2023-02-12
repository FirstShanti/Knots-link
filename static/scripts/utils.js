// button to top
$(function() {
	$(window).scroll(function() {
		if($(this).scrollTop() > 250) {
			$('#toTop').fadeIn();
		} else {
			$('#toTop').fadeOut();
		}
	});
	$('#toTop').click(function() {
		$('body,html').animate({scrollTop:0}, 800);
	});
	
});

// category move
$(document).ready(function() {
	let navButton = $("button#dropdownMenuButton")
	if (!!navButton) {
		$("button#dropdownMenuButton").click(function(){
			var mrValue = parseInt($("#category-value-select").css('margin-right'))
			var menuDisplay = String($(".dropdown-menu").css('display'))
			if (menuDisplay == 'none') {
				if (mrValue <= 45) {
					$("#category-value-select").css('margin-right', '+=45')
				}
			} else {
				if (mrValue > 0) {
					$("#category-value-select").css('margin-right', '0')
				}
			}
		});
		$(document).click(function(){
			var menuDisplay = String($(".dropdown-menu").css('display'))
			var mrValue = parseInt($("#category-value-select").css('margin-right'))
			if (menuDisplay == 'none' && mrValue > 0) {
				$("#category-value-select").css('margin-right', '0')
			}
		})
	}
});

// validate_form_input_length
$(function(){
    if (window.CKEDITOR) {
        var desc = CKEDITOR.instances['body'];
        desc.on('change', function () {
            var ckeditor_input_length = $(this.getData()).text().length
            var elem_w_min_max_length = $(`#form_${this.name}_input_length_display`)
            min = $(elem_w_min_max_length).attr('min')
            max = $(elem_w_min_max_length).attr('max')
            var ckeditor_validate_display = $('small#ckeditor_validate')
            if ( !ckeditor_validate_display.length ) {
                $('span#cke_1_bottom').append('<small id="ckeditor_validate"></small>')
                var ckeditor_validate_display = $('small#ckeditor_validate')
            }
            validationInputLength(ckeditor_validate_display, min, max, ckeditor_input_length)
        })
    }
    $('input, #title, #preview, #tags').on('keyup change', function () {
        var elem_w_min_max_length = $(`#form_${this.name}_input_length_display`)
        min = $(elem_w_min_max_length).attr('min')
        max = $(elem_w_min_max_length).attr('max')
        input_length = $(this).val().length
        $(`span#form_${this.name}_model_errors`).fadeOut(1000)
        validationInputLength(elem_w_min_max_length, min, max, input_length)
    })
})

validationInputLength = function (element_display, min, max, input_length) {
    if (input_length === 0) {
        element_display.fadeOut(2000);
        // downHeight(element_display, 2) // d
    } else if (input_length < min) {
        element_display.text(`${input_length}/${min}`)
        element_display.addClass('invalid_input')
        element_display.fadeIn(500)
        // upHeight(element_display, 2, 10) // d
    } else if (input_length > max) {
        element_display.text(`${input_length}/${max}`)
        element_display.addClass('invalid_input')
        element_display.fadeIn(500)
        // upHeight(element_display, 2, 10) // d
    } else {
        element_display.text(`${input_length}/${max}`)
        element_display.addClass('valid_input')
        element_display.removeClass('invalid_input')
        element_display.fadeOut(2000);
        // downHeight(element_display, 2) // d
    }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function downHeight(element, time) {
    var height = element.height()
    var ms = (time * 1000) /  height
    for (var i = (height * 10); i >= 1; i--) {
        element.height(i/10)
        // element.css('opacity', `${1 - (1 / i)}`)
        sleep(ms)
    }
    element.height(0)
}

function upHeight(element, time, height) {
    var ms = (time * 10000) /  (height * 10)
    for (var i = 1; i <= (height * 10); i++) {
        element.height(i/10)
        // element.css('opacity', `${0 + (1 / i)}`)
        sleep(ms)
    }
}
// end

const request = async (method, url, headers, params, with_auth) => {
    let host = window.location.origin
    new_url = new URL(`${host}${url}`)
    headers = {...headers, apiRequest: true}
    const requestOptions = {
        method: method,
        headers: headers,
    };
    // if (with_auth) {
    //     requestOptions.headers = {
    //         ...headers,
    //         'Authorization': `Bearer ${_.get(getFromStorage('token'), access_token)}`
    //     }
    // }
    if (method == 'POST' && !_.isEmpty(params)) {
        requestOptions.body = JSON.stringify(params)
        requestOptions.headers = {
            ...requestOptions.headers,
            'Content-Type': 'application/json'
        }
    } else if (method == 'GET' && !_.isEmpty(params)) {
        new_url.search = new URLSearchParams(params).toString()
    }
    let response = await fetch(new_url, requestOptions)
        .then(async response => {
            let data = await response.json();
            // // check for error response
            if (!response.ok) {
                // get error message from body or default to response statusText
                data.message = (data && data.message) || response.statusText;
                // return Promise.reject(error);
            }
            if (response.status == 403) {
                redirect_to_login()
            }
            return Promise.resolve(data)
        })
        .catch(error => {
            return error;
        });
    return response
}

const updateCookies = (key, maxAge) => {
    const auth = getFromStorage('auth', type='LOCAL')
    if (!!auth) {
        Object.keys(auth).filter(k => key ? k == key : true).map(k => document.cookie = `${k}=${auth[k]}; max-age=${maxAge || 2592000}`)
    } else {
        document.cookie = `${key}=; max-age=${maxAge || 2592000}; path=/`
    }
}

// const isAuth = () => {
//     const auth = getFromStorage('auth', type='LOCAL')
//     const now = moment.utc().unix()
//     return !!auth && auth.expired_at > now
// }

const redirect_to_login = (event) => {
    let host = window.location.origin
    window.location.replace(host + '/log_in');
}

function playNotification() {                 
    /* Audio link for notification */ 
    var mp3 = '<source src="./static/audio/notification1.mp3" type="audio/mpeg">'; 
    document.getElementById("sound").innerHTML =  
    '<audio autoplay="autoplay">' + mp3 + "</audio>"; 
}

function Utils() {

}

Utils.prototype = {
    constructor: Utils,
    isElementInView: function (element, fullyInView) {

        var pageTop = element.parentElement.offsetTop;
        var pageBottom = pageTop + $(window).height();
        var elementTop = $(element).offset().top;
        var elementBottom = elementTop + $(element).height();

        if (fullyInView === true) {
            return ((pageTop < elementTop) && (pageBottom > elementBottom));
        } else {
            return ((elementTop <= pageBottom) && (elementBottom >= pageTop));
        }
    }
};

var Utils = new Utils();