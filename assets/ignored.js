var elems = document.querySelectorAll('.carousel');
var instances = M.Carousel.init(elems);

function SelectionBorder () {

    $('.face-selection').removeAttr('style');
    this.style = 'outline: solid; outline-color: red; outline-width: 4px;';

}

$(document).on('click', '.face-selection', SelectionBorder);