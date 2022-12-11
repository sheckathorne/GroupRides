$(document).ready(function() {
    var parent_div = $('#ride-filter-parent')
    var url = window.location.href;
    var a = url.indexOf("?");
    var b =  url.substring(a);
    var c = url.replace(b,"");
    parent_div.append("<div class='col-lg-1 col-md-6'><a class='btn btn-outline-primary w-100 mb-2' href='" + c + "'>Clear</a></div>")
})