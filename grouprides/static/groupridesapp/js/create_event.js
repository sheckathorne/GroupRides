$(document).ready(function(){
    console.log("window loaded")
    console.log($("#event_create_privacy").val())
    if ($("#event_create_privacy").val() === "4") {
        conditional_fields.show();
    } else {
        conditional_fields.hide();
    }
})

var conditional_fields = $("#div_id_club");
conditional_fields.hide();

$("#event_create_privacy").change(function() {
    console.log($(this).val())
    if ($(this).val() === "4") {
        conditional_fields.show();
    } else {
        conditional_fields.hide();
    }
});