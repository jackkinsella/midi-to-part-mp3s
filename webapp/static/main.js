$(function () {
    'use strict';
    // Drop Zone from https://bootsnipp.com/snippets/D7MvX
    // UPLOAD CLASS DEFINITION
    // ======================

    var dropZone = document.getElementById('drop-zone');
    var uploadForm = document.getElementById('js-upload-form');

    var startUpload = function () {
        $('#js-upload-submit').prop('disabled', true)
        console.log($('#js-upload-form')[0])
        let formData = new FormData($('#js-upload-form')[0]);
        $.ajax({
            type: "POST",
            url: "/midi-info",
            enctype: 'multipart/form-data',
            data: formData,
            contentType: false,
            cache: false,
            processData: false,
            success: function (response) {
                var obj = JSON.parse(response);
                $('#score-view').text('')
                var osmd = new opensheetmusicdisplay.OpenSheetMusicDisplay("score-view");
                window.musicXml = obj.musicxml
                osmd.load(obj.musicxml)
                osmd.render()
                $('#midi-track-list').text('')
                var i;
                for (i = 0; i < obj.parts.length; i++) {
                    $('#midi-track-list').append(
                        '<li class="list-group-item" draggable="true" ondragstart="drag(event)" id="' +
                        obj.parts[i] + '">Track ' + (i + 1) + ' (' + obj.parts[i] + ')' +
                        '<input type="hidden" name="trackId" value="' + i + '"></li>');
                }
            },
            error: function (data) {
                $('#js-upload-submit').prop('disabled', false)
            }
        });
    }

    uploadForm.addEventListener('submit', function (event) {
        var uploadFiles = document.getElementById('js-upload-files').files;
        event.preventDefault()

        startUpload()
    })

    dropZone.ondrop = function (event) {
        event.preventDefault();
        this.className = 'upload-drop-zone';
        document.getElementById('js-upload-files').files = event.dataTransfer.files

        startUpload()
    }

    dropZone.ondragover = function () {
        this.className = 'upload-drop-zone drop';
        return false;
    }

    dropZone.ondragleave = function () {
        this.className = 'upload-drop-zone';
        return false;
    }

    $('#btDownload').click(function () {
        $(this).prop('disabled', true);

        // Triggering file download from here: http://www.alexhadik.com/blog/2016/7/7/l8ztp8kr5lbctf5qns4l8t3646npqh
        let url = 'download'
        let downloadFormData = new FormData();
        $("#soprano-tracks :input").each(function (i, val) { downloadFormData.append('soprano', val.value) })
        $("#alto-tracks :input").each(function (i, val) { downloadFormData.append('alto', val.value) })
        $("#tenor-tracks :input").each(function (i, val) { downloadFormData.append('tenor', val.value) })
        $("#bass-tracks :input").each(function (i, val) { downloadFormData.append('bass', val.value) })
        if ($('#instrument-selector option:selected').val() != '-1') {
            downloadFormData.append('instrument', $('#instrument-selector option:selected').val())
        }
        downloadFormData.append('musicxml', window.musicXml)
        $.ajax(
            {
                type: "POST",
                url: url,
                data: downloadFormData,
                enctype: 'multipart/form-data',
                contentType: false,
                cache: false,
                processData: false,
                xhrFields:{
                    responseType: 'blob'
                },
                success: function (data) {
                    createBlobAndTriggerDownload(data, 'part-mp3s.zip', 'application/zip')
                    $('#btDownload').prop('disabled', false);
                },
                error: function (jqXHR, textStatus) {
                    $('#errorMessage').text("The download could not be initiated (HTTP error code " + jqXHR.status + ", text status '" + textStatus + "')")
                    $('#btDownload').prop('disabled', false);
                }
            }
        );
    });
});

/**
 * Encapsulates the feature to trigger a download for a blob object.
 * 
 * Constructs a blob object utilizing the response data of the onload object.
 * This done using a "virtual" html link element that is hidden and clicked programmatically.
 * 
 * By encapsulating the blob in a DOMString and pointing the link to it,
 * the browser will react as if clicked on a regular file download link.
 * 
 * Source: http://www.alexhadik.com/blog/2016/7/7/l8ztp8kr5lbctf5qns4l8t3646npqh
 */
function createBlobAndTriggerDownload(response, fileName, mediaType) {
    var blob = new Blob([response], { type: mediaType });
    let a = document.createElement("a");
    a.style = "display: none";
    document.body.appendChild(a);
    let url = window.URL.createObjectURL(blob);
    a.href = url;
    a.download = fileName;
    a.click();
    window.URL.revokeObjectURL(url);
}

function allowDrop(event) {
    event.preventDefault();
}

function drag(event) {
    event.dataTransfer.setData("text", event.target.id);
}

function drop(event) {
    event.preventDefault();
    let data = event.dataTransfer.getData("text");
    event.target.appendChild(document.getElementById(data));
}