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
})

validationInputLength = function (element_display, min, max, input_length) {
    if (input_length === 0) {
        element_display.fadeOut(2000);
    } else if (input_length < min) {
        element_display.text(`${input_length}/${min}`)
        element_display.addClass('invalid_input')
        element_display.show()
    } else if (input_length > max) {
        element_display.text(`${input_length}/${max}`)
        element_display.addClass('invalid_input')
        element_display.show()
    } else {
        element_display.text(`${input_length}/${max}`)
        element_display.addClass('valid_input')
        element_display.removeClass('invalid_input')
        element_display.fadeOut(2000);
    }
}

