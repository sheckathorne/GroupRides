$(document).ready(function() {
    console.log('hello')
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