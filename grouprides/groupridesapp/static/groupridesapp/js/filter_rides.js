$(document).ready(function() {
    var anchor = $('#ride-clear-button');
    var divs = $('div.shadow-parent > div > div.relative > select');
    var url = window.location.href;
    var a = url.indexOf("?");
    var b =  url.substring(a);
    var c = url.replace(b,"");

    divs.addClass("shadow");
    anchor.attr("href", c);
})