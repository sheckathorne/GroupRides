function showHelpText(el, url) {
    el.show();
    el.text(url);
    el.attr("href")

}

function hideOrShowFields(arr, action) {
    if ( action === "hide" ) {
        arr.forEach(item => {
            item.field.hide()
        })
    } else if ( action === "show") {
        arr.forEach(item => {
            item.field.show()
        })
    }
}

function hideOrShowOneField(arr, fieldName, action) {
    item = arr.find(item => item.name === fieldName)

    if ( action === "hide" ) {
        item.field.hide()
    } else if ( action === "show") {
        item.field.show()
    }
}

var conditional_fields = [
    { name: "club", field: $("#div_id_club") },
    { name: "weekdays", field: $('#div_id_weekdays') }
];

hideOrShowFields(conditional_fields, "hide");

$(document).ready(function() {
    var option = $('#event_create_route').find(':selected');
    var url = option.data('url');
    var help_text = $('#route_url_id');

    if ( url && url.length > 0 ) {
        help_text.show();
        help_text.text(url);
        help_text.attr("href", url);
    } else {
        help_text.hide();
    }


    if ( $("#event_create_privacy").val() === "5" ) {
        hideOrShowOneField(conditional_fields, "club", "show");
    } else {
        hideOrShowOneField(conditional_fields, "club", "hide");
    }

    console.log($("#event_create_frequency").val())

    if ( ["7","14"].includes($("#event_create_frequency").val()) ) {
        hideOrShowOneField(conditional_fields, "weekdays", "show");
    } else {
        hideOrShowOneField(conditional_fields, "weekdays", "hide");
    }
})

$("#event_create_privacy").change(function() {
    if ($(this).val() === "5") {
        hideOrShowOneField(conditional_fields, "club", "show");
    } else {
        hideOrShowOneField(conditional_fields, "club", "hide");
    }
});

$("#event_create_frequency").change(function() {
    if (["7", "14"].includes($(this).val())) {
        hideOrShowOneField(conditional_fields, "weekdays", "show");
    } else {
        hideOrShowOneField(conditional_fields, "weekdays", "hide");
    }
});

$("#event_create_route").on('change', function() {
    var option = $(this).find(':selected');
    var url = option.data('url');
    var help_text = $('#route_url_id');

    if ( url && url.length > 0 ) {
        help_text.show();
        help_text.attr("href", url);
        help_text.text(url);
    } else {
        help_text.hide();
    }
})