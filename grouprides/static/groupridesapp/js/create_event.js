$(document).ready(function() {
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

$("#event_create_route").change(function() {
    var url = `$(this).prop("data-url")
    console.log(url)
})