/* javascript to accompany upload-sdf.html */
$(document).ready(function() {
    $('#submit_sdf').on('click', function(e) {
        e.preventDefault();
        var molName = $('#mol-name').val().trim();
        var sdfFile = $('#sdf-file')[0].files[0];
        var regex = /^[a-zA-Z0-9_\-]+$/;
        if (!molName.match(regex)) {
            alert('Invalid molecule name');
            return;
        }
        var formData = new FormData();
        formData.append('mol-name', molName);
        formData.append('sdf-file', sdfFile);
        var progressBar = $('#progress-bar');
        var progressContainer = $('#progress-container');
        var progressStatus = $('#progress-status');
        $.ajax({
            url: '/upload_form.html',
            type: 'POST',
            xhr: function() {
                var xhr = $.ajaxSettings.xhr();
                xhr.upload.onprogress = function(e) {
                    var progress = Math.floor(e.loaded / e.total * 100);
                    progressBar.width(progress + '%');
                    progressStatus.text(progress + '%');
                };
                return xhr;
            },
            data: formData,
            processData: false,
            contentType: false,
            beforeSend: function() {
                progressBar.width('0%');
                progressStatus.text('0%');
                progressContainer.show();
            },
            success: function(response) {
                progressBar.width('100%');
                progressStatus.text('100%');
                setTimeout(function() {
                    progressContainer.hide();
                }, 1000);
                alert("Molecule Added!");
            },
            error: function(xhr, status, error) {
                progressBar.width('0%');
                progressStatus.text('0%');
                setTimeout(function() {
                    progressContainer.hide();
                }, 1000);
                if (xhr.status === 400) {
                    alert("Submission Invalid.");
                } else {
                    alert("Error: " + error);
                }
                console.log(xhr.responseText);
            }
        });
    });
});


