if (!$) {
    $ = django.jQuery;
}

$(window).on('load', function () {
    $('input').phoenix();
    $('textarea').phoenix();
    $('#_form').submit(function (e) {
        $('input').phoenix('remove');
        $('textarea').phoenix();
    });
});
