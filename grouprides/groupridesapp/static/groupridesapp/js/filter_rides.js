$(document).ready(function() {
    var anchor = $('#ride-clear-button');
    var url = window.location.href;
    var a = url.indexOf("?");
    var b =  url.substring(a);
    var c = url.replace(b,"");

    anchor.attr("href", c);
})