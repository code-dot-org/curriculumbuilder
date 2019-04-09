$(function () {
    // Build Table of Contents
    $('#toc' + lesson_title).toc({
        'selectors': 'h2,h3', //elements to use as headings
        'container': '#' + lesson_title + 'content', //element to find all selectors in
        'exclude': '.stage_guide h2, .stage_guide h3', //selectors to exclude
        'smoothScrolling': false, //enable or disable smooth scrolling on click
        'prefix': lesson_title, //prefix for anchor tags and class names
        'onHighlight': function (el) {
        }, //called when a new section is highlighted
        'highlightOnScroll': true, //add class to heading that is currently in focus
        'highlightOffset': 100, //offset to trigger the next headline
        'anchorName': function (i, heading, prefix) { //custom function for anchor name
            return prefix + i;
        },
        'headerText': function (i, heading, $heading) { //custom function building the header-item text
            return $heading.text();
        },
        'itemClass': function (i, heading, $heading, prefix) { // custom function for item class
            return $heading[0].tagName.toLowerCase();
        }
    });

    // Format the prep section with checkboxes
    var count = 1;
    $(".prep ul li:visible").each(function (li) {
        $(this).before('<input type="checkbox" class="todo" name="' + (count++) + '"/>');
    });
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

    // Add tooltip toggles to vocab
    $('.vocab').each(function () {
        $(this).attr('data-toggle', 'tooltip');
        $(this).attr('data-placement', 'bottom');
    });
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    });

    // Convert streaming responses to formattable JSON
    function parseResponse(responseText) {
        var responses = responseText.split("\n");
        var response = [];
        for (var i in responses) {
            if (responses[i] != "") {
                response.push(JSON.parse(responses[i]));
            }
        }
        return response
    }

    // Strip answer key links
    $('.key').html("<p><em>View on Code Studio to access answer key(s)</em></p>")

    function toggleCollapse(event, ui) {
        if ($(ui.newPanel).length === 0) {
            $(ui.oldPanel).addClass("collapsed");
            $(ui.oldPanel).siblings().removeClass("collapsed");
        } else {
            $(ui.newPanel).removeClass("collapsed");
            $(ui.newPanel).siblings().removeClass("collapsed");
        }
    }

    // Code Studio pullthrough
    $('.stage_guide').each(function () {
        var start = parseInt($(this).attr('data-start'));
        var end = parseInt($(this).attr('data-end'));


        if ($('.stage_guide_hidden').children().length > 0) {
            if (start) {
                var tab, tabs, chunk, panel, current_named, last_named;
                $(this).append('<div class="stage-chunk named-False always-on-False"><h3><i class="fa fa-desktop"></i> Code Studio levels</h3><ul></ul></div>');
                chunk = $(this).find('.stage-chunk');
                tabs = $(chunk).find('ul');
                if (end) {
                    for (var i = start; i <= end; i++) {
                        tab = $('.stage_guide_hidden .stage-chunk li[data-level=' + i + ']');
                        panel = $('.stage_guide_hidden .stage-chunk .level-panel[data-level=' + i + ']');
                        current_named = $(tab).data('named');

                        // If this is a named level, or the first in an unnamed chunk, start a new chunk
                        if (last_named == 'True' || last_named != current_named) {
                            $(this).append('<div class="stage-chunk named-False always-on-False"><ul></ul></div>');
                            chunk = $(chunk).next('.stage-chunk');
                            tabs = $(chunk).find('ul');
                        }

                        // If this is the first in an unnamed chunk, add "Levels" header
                        if (last_named != current_named && current_named == 'False') {
                            $(tabs).append('<li class="chunk-header">Levels</li>');
                        }

                        $(tab).appendTo(tabs);
                        $(panel).appendTo(chunk);
                        if (current_named == 'True') {
                            $(chunk).removeClass("named-False always-on-False");
                            $(chunk).addClass("named-True always-on-True");
                        }
                        last_named = current_named;
                    }
                } else {
                    tab = $('.stage_guide_hidden .stage-chunk li[data-level=' + start + ']');
                    panel = $('.stage_guide_hidden .stage-chunk .level-panel[data-level=' + start + ']');

                    if ($(tab).data('named') == 'True') {
                        $(chunk).removeClass("named-False always-on-False");
                        $(chunk).addClass("named-True always-on-True");
                    } else {
                        $(tabs).append('<li class="chunk-header">Levels</li>');
                    }

                    $(tab).appendTo(tabs);
                    $(panel).appendTo(chunk);
                }
            } else {
                $(this).append('<h3><i class="fa fa-desktop"></i> Code Studio levels</h3>');
                $('.stage_guide_hidden .stage-chunk').appendTo(this);
            }
            // Add base urls to links coming from Code Studio

            $(this).find('a').not('[href^="http"],[href^="https"],[href^="//"],[href^="#"]').each(function () {
                $(this).attr('href', "//studio.code.org" + $(this).attr('href'));
            });
        }
    });

    $('.stage_guide_hidden').remove();

    $(".always-on-False").tabs({
        collapsible: true,
        active: false,
        classes: {"ui-tabs-panel": "ui-corner-all"},
        activate: toggleCollapse
    }).each(function () {
        $(this).children(".ui-tabs-panel").first().addClass("collapsed");
    });

    $(".always-on-True").tabs({
        collapsible: true,
        classes: {"ui-tabs-panel": "ui-corner-all"},
        activate: toggleCollapse
    });


});