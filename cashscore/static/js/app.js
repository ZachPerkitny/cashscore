$(document).ready(function() {
    $('[data-popover]').on('click', function(e) {
        e.preventDefault();
        var popover = $($(this).data('popover'));
        popover.toggleClass('open');
        e.stopImmediatePropagation();
    });

    $(document).on('click', function(e) {
        if($('.popover.open').length > 0) {
            $('.popover').removeClass('open');
        }
    });
});
