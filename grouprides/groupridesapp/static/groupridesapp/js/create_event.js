function showHelpText(el, url) {
    el.show();
    el.text(url);
    el.attr("href")

}

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


    if ($("#event_create_privacy").val() === "5") {
        conditional_fields.show();
    } else {
        conditional_fields.hide();
    }
})

var conditional_fields = $("#div_id_club");
conditional_fields.hide();

$("#event_create_privacy").change(function() {
    if ($(this).val() === "5") {
        conditional_fields.show();
    } else {
        conditional_fields.hide();
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