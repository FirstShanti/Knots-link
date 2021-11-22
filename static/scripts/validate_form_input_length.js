$(function(){
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
    $('input, #title, #preview, #tags').on('keyup change', function () {
        var elem_w_min_max_length = $(`#form_${this.name}_input_length_display`)
        min = $(elem_w_min_max_length).attr('min')
        max = $(elem_w_min_max_length).attr('max')
        input_length = $(this).val().length
        validationInputLength(elem_w_min_max_length, min, max, input_length)
    })
    // $( "select#category option:selected" ).on('click', function() {
    //     console.log(this)
    //     this.selected = 'selected'
    // })
    // $('select#category').on('change', function() {
    //     let value = this.value
    //     // console.log(value)
    //     // console.log(this)
    //     // console.log(this.children.length)
    //     for (let i = 0; i < this.children.length; i++) {
    //         // console.log(i)
    //         if (this.children[i].value == value) {
    //             console.log(this.children[i].selected)
    //             console.log('change')
    //             this.children[i].selected = 'selected'
    //             // let  elem = $(`select#category option[value=${value}]`)
    //             // elem.prop('selected', true);
    //             // console.log(this.children[i])
    //             // this.children[i].prop('selected', true);
    //         } else {
    //             console.log('delete')
    //             delete this.children[i].selected
    //         }
    //     }
    //     // console.log(value)
    //     // // console.log(this.option[value=value])
    //     // console.log(elem)
    // })
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