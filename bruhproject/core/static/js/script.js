$(document).ready(function () {
    $('.variant').click(function () {
        $("select[name=chosen_variant] option[value=" + $(this).attr('data-variantid') + "]").attr('selected', 'selected')
        if ($('.hider').hasClass('bi-chevron-up')) {
            $('.hider').switchClass('bi-chevron-up', 'bi-dash-lg', 5000, 'easeInOutQuad')
            $('.form-group').toggle('blind', 500)
        }
        $('.betbutton').prop('disabled',false)
    })
    $('.betform').submit(function () {
        $('#id_chosen_variant').prop('disabled', false);
    })
    $('.hider').click(function () {
        $(this).hasClass('bi-dash-lg') ? $(this).switchClass('bi-dash-lg', 'bi-chevron-up', 1000, 'easeInOutQuad') : $(this).switchClass('bi-chevron-up', 'bi-dash-lg', 5000, 'easeInOutQuad')
        $('.form-group').toggle('blind', 500)
    })

    $(window).scroll(function () {
        var w = $(window).width();
        if (w < 768) {
            $('#top-button').hide();
        } else {
            var e = $(window).scrollTop();
            e > 150 ? $('#top-button').fadeIn() : $('#top-button').fadeOut();
        }
    });
})