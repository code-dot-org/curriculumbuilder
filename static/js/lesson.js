
$(document).ready(function () {

    // add checkboxes to lists in the prep section
    var count = 1;
    $(".prep ul li:visible").each(function (li) {
        $(this).prepend('<input type="checkbox" class="todo" name="' + (count++) + '"/>');
    });

    // read the current/previous setting
    var $todos = $(".todo");
    $todos.each(function () {
        var todo = localStorage.getItem($(this).attr('name') + window.location.pathname);
        if (todo && todo == "true") {
            $(this).prop('checked', todo);
        }
    });
    $todos.change(function () {
        localStorage.setItem($(this).attr("name") + window.location.pathname, $(this).prop('checked'));
    });

    // Settings toggles

    // read the current/previous setting
    $settings = $('.settings input');
    $settings.each(function () {
        var setting = localStorage.getItem($(this).attr('name'));
        if (setting == undefined) {
            $(this).prop('checked', true);
        } else if (setting == "true") {
            $(this).prop('checked', setting);
        } else {
            $('.admonition.' + $(this).attr('name')).toggle($(this).prop('checked'));
        }
    });
    $settings.change(function () {
        $('.admonition.' + $(this).attr('name')).toggle($(this).prop('checked'));
        localStorage.setItem($(this).attr("name"), $(this).prop('checked'));
    });

    $('.tiplink i').click(function () {
        var $the_tip = $($(this).parent().attr('href'));
        $the_tip.parent().toggle(true);
    });

    // Add tooltip toggles to vocab
    $('.vocab').each(function () {
        $(this).attr('data-toggle', 'tooltip');
        $(this).attr('data-placement', 'bottom');
    });
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    });

    // Publish button
    $("#publish_this").click(function () {
        $('#publish_this').html("Publishing...").removeClass('btn-warning btn-success').addClass('btn-primary');
        var pk = $(this).attr('data-pk');
        var type = $(this).attr('data-type');
        $('#progress_spinner').addClass('fa fa-cog fa-spin');
        $.ajax({
            type: "POST",
            url: "/publish/",
            data: {pk: pk, type: type},
            timeout: 9999999
        }).done(function (response) {
            $("#publish_this").addClass('btn-success').text("Success");
            $("#publish_results").text(JSON.stringify(response, undefined, 2));
            $('#progress_spinner').removeClass('fa fa-cog fa-spin');
        }).fail(function (response) {
            $("#publish_this").addClass('btn-warning').text("Failed");
            $("#publish_results").text(JSON.stringify(response, undefined, 2));
            $('#progress_spinner').removeClass('fa fa-cog fa-spin');
        });
    });

    var isFeedbackActive = false;

    $('#feedbackFrame').load(function () {
        if ($(this).attr('src')) {
            isFeedbackActive = !isFeedbackActive;
            if (!isFeedbackActive) {
                $('#feedbackModal').modal('toggle');
            }
        }
    });


    $('#feedbackModal').on('shown.bs.modal', function () {
        if (!isFeedbackActive) {
            $(this).find('iframe').attr('src', "{{ lesson.feedback_link|safe }}&embedded=true");
        }

        //$(this).find('.modal-body').css({
        //    'max-height':'100%'
        //});
    });
});