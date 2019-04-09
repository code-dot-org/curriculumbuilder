// Cookies break the PDF generator, so we only use them when viewed by an admin.
// This pulls the Django CSRF token cookie so we can make ajax calls (used for self publishing)

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(function () {

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

    // Publish to curriculum.code.org
    $("#publish_this").click(function () {
        $('#publish_this').html("Publishing...").removeClass('btn-warning btn-success').addClass('btn-primary');
        var pk = $(this).attr('data-pk');
        var type = $(this).attr('data-type');
        var lessons = $('#include_lessons').prop('checked');
        $('#progress_spinner').addClass('fa fa-cog fa-spin');

        // Streaming results
        var params = "pk=" + pk + "&type=" + type + "&lessons=" + lessons;
        var client = new XMLHttpRequest();
        client.open('GET', '/publish/?' + params, true);
        client.setRequestHeader("Content-type", "application/json; charset=utf-8");
        client.onprogress = function () {
            var response = parseResponse(this.responseText);
            $("#publish_results").text(JSON.stringify(response, null, 2));
            console.log(this.responseText);
        };
        client.upload.addEventListener('error', function (event) {
            var response = parseResponse(this.responseText);
            $("#publish_this").addClass('btn-warning').text("Failed");
            $("#publish_results").text(JSON.stringify(response, null, 2));
            $('#progress_spinner').removeClass('fa fa-cog fa-spin');
        });

        client.addEventListener('readystatechange', function (e) {
            if (this.readyState == 4) {
                console.log(this.status);
                var response = parseResponse(this.responseText);
                if (this.status == 200) {
                    $("#publish_this").addClass('btn-success').text("Success");
                    $("#publish_results").text(JSON.stringify(response, null, 2));
                    $("#publish_results").append('\nFinished');
                    $('#progress_spinner').removeClass('fa fa-cog fa-spin');
                } else {
                    $("#publish_this").addClass('btn-warning').text("Failed");
                    $("#publish_results").text(JSON.stringify(response, null, 2));
                    $("#publish_results").append('\nFailed');
                    $('#progress_spinner').removeClass('fa fa-cog fa-spin');
                }
            }
        });
        client.send();
    });

    // Publish PDFs
    $("#publish_pdfs").click(function () {
        $('#publish_pdfs').html("Publishing...").removeClass('btn-warning btn-success').addClass('btn-primary');
        var pk = $(this).attr('data-pk');
        var type = $(this).attr('data-type');
        $('#progress_spinner_pdf').addClass('fa fa-cog fa-spin');

        // Switch to streaming results
        var params = "pk=" + pk + "&type=" + type + "&pdf=true";
        var pdf_client = new XMLHttpRequest();
        pdf_client.open('GET', '/publish/?' + params, true);
        pdf_client.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        pdf_client.onprogress = function () {
            var response = parseResponse(this.responseText);
            $("#publish_results_pdf").text(JSON.stringify(response, null, 2));
            console.log(this.responseText);
        };
        pdf_client.upload.addEventListener('error', function (event) {
            var response = parseResponse(this.responseText);
            $("#publish_pdfs").addClass('btn-warning').text("Failed");
            $("#publish_results_pdf").text(JSON.stringify(response, undefined, 2));
            $('#progress_spinner_pdf').removeClass('fa fa-cog fa-spin');
        });

        pdf_client.addEventListener('readystatechange', function (e) {
            if (this.readyState == 4) {
                var response = parseResponse(this.responseText);
                console.log(this.status);
                if (this.status == 200) {
                    $("#publish_pdfs").addClass('btn-success').text("Success");
                    $("#publish_results_pdf").text(JSON.stringify(response, undefined, 2));
                    $("#publish_results_pdf").append('\nFinished');
                    $('#progress_spinner_pdf').removeClass('fa fa-cog fa-spin');
                } else {
                    $("#publish_pdfs").addClass('btn-warning').text("Failed");
                    $("#publish_results_pdf").text(JSON.stringify(response, null, 2));
                    $("#publish_results_pdf").append('\nFailed');
                    $('#progress_spinner_pdf').removeClass('fa fa-cog fa-spin');
                }
            }
        });
        pdf_client.send();

        // Clone
        $("#clone_this").click(function () {
            $('#clone_this').html("Cloning...").removeClass('btn-warning btn-success').addClass('btn-primary');
            var pk = $(this).attr('data-pk');
            var type = $(this).attr('data-type');
            var children = $('#clone_children').prop('checked');
            $('#clone_spinner').addClass('fa fa-cog fa-spin');

            $.ajax({
                type: "POST",
                url: "/clone/",
                data: {pk: pk, type: type, children: children},
                timeout: 9999999
            }).done(function (response) {
                $("#clone_this").addClass('btn-success').text("Success");
                $("#clone_results").text(JSON.stringify(response, undefined, 2));
                $('#clone_spinner').removeClass('fa fa-cog fa-spin');
                if (response.hasOwnProperty('redirect_url')) {
                    setTimeout(function () {
                        window.location.href = response.redirect_url;
                    }, 500);
                }
            }).fail(function (response) {
                $("#clone_this").addClass('btn-warning').text("Failed");
                $("#clone_results").text(JSON.stringify(response, undefined, 2));
                $('#clone_spinner').removeClass('fa fa-cog fa-spin');
            });
        });

        // Get Code Studio Details
        $("#get_stage_details").click(function () {
            $('#get_stage_details').html("Getting Stage Details...").removeClass('btn-warning btn-success').addClass('btn-primary');
            var pk = $(this).attr('data-pk');
            $('#stage_progress_spinner').addClass('fa fa-cog fa-spin');
            $.ajax({
                type: "POST",
                url: "/get_stage_details/",
                data: {pk: pk},
                timeout: 9999999
            }).done(function (response) {
                $("#get_stage_details").addClass('btn-success').text("Success");
                $('#stage_progress_spinner').removeClass('fa fa-cog fa-spin');
                location.reload();
            }).fail(function (response) {
                $("#get_stage_details").addClass('btn-warning').text("Failed");
                $("#stage_details_results").text(JSON.stringify(response, undefined, 2));
                $('#stage_progress_spinner').removeClass('fa fa-cog fa-spin');
            });
        });
    });
});