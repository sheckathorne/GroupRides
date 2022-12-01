$(document).ready(function() {
    if ($("#route_create_shared").prop("checked")) {
        conditional_fields.show();
    } else {
        conditional_fields.hide();
    }
})

var conditional_fields = $("#div_id_club");
conditional_fields.hide();

$("#route_create_shared").change(function() {
    if (this.checked) {
        conditional_fields.show();
    } else {
        conditional_fields.hide();
    }
});