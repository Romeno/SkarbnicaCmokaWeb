var base_height = $('.news')[0].offsetHeight * 0.45;


var elements = $('.news-text > a');
var heights = $('.news-text-wrapper');

    for (var i=0;i<elements.length;i++) {
        var text = elements[i].innerText;
        var L = text.length - 1;
        while (heights[i].offsetHeight >= base_height) {
            elements[i].innerText = text.substring(0, L) + '...';
            L -= 5;
        }
    }
