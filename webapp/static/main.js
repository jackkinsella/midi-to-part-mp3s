$(function() {
    'use strict';
    // Drop Zone from https://bootsnipp.com/snippets/D7MvX
    // UPLOAD CLASS DEFINITION
    // ======================

    var dropZone = document.getElementById('drop-zone');
    var uploadForm = document.getElementById('js-upload-form');

    var startUpload = function() {
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
            success: function(data) {
                var obj = JSON.parse(data);
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
            error: function(data){
                $('#js-upload-submit').prop('disabled', false)
            }
        });
    }

    uploadForm.addEventListener('submit', function(e) {
        var uploadFiles = document.getElementById('js-upload-files').files;
        e.preventDefault()

        startUpload()
    })

    dropZone.ondrop = function(e) {
        e.preventDefault();
        this.className = 'upload-drop-zone';
        document.getElementById('js-upload-files').files = e.dataTransfer.files

        startUpload()
    }

    dropZone.ondragover = function() {
        this.className = 'upload-drop-zone drop';
        return false;
    }

    dropZone.ondragleave = function() {
        this.className = 'upload-drop-zone';
        return false;
    }

    $('#btDownload').click(function() {
        $(this).prop('disabled', true);

        // Triggering file download from here: http://www.alexhadik.com/blog/2016/7/7/l8ztp8kr5lbctf5qns4l8t3646npqh
        let url = 'download'
        let downloadFormData = new FormData();
        $("#soprano-tracks :input").each(function(i, val) { downloadFormData.append('soprano', val.value) })
        $("#alto-tracks :input").each(function(i, val) { downloadFormData.append('alto', val.value) })
        $("#tenor-tracks :input").each(function(i, val) { downloadFormData.append('tenor', val.value) })
        $("#bass-tracks :input").each(function(i, val) { downloadFormData.append('bass', val.value) })
        if ($('#instrument-selector option:selected').val() != '-1') {
            downloadFormData.append('instrument', $('#instrument-selector option:selected').val())
        }
        downloadFormData.append('musicxml', window.musicXml)
        let xhr = new XMLHttpRequest();
        //set the request type to post and the destination url to '/convert'
        xhr.open('POST', url);
        //set the reponse type to blob since that's what we're expecting back
        xhr.responseType = 'blob';
        xhr.send(downloadFormData);
        xhr.onload = function(e) {
            if (this.status == 200) {
                // Create a new Blob object using the 
                //response data of the onload object
                var blob = new Blob([this.response], { type: 'application/zip' });
                //Create a link element, hide it, direct 
                //it towards the blob, and then 'click' it programatically
                let a = document.createElement("a");
                a.style = "display: none";
                document.body.appendChild(a);
                //Create a DOMString representing the blob 
                //and point the link element towards it
                let url = window.URL.createObjectURL(blob);
                a.href = url;
                a.download = 'part-mp3s.zip';
                //programatically click the link to trigger the download
                a.click();
                //release the reference to the file by revoking the Object URL
                window.URL.revokeObjectURL(url);
            } else {
                //deal with your error state here
            }
            $('#btDownload').prop('disabled', false);
        };
    });
});

function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
}

function drop(ev) {
    ev.preventDefault();
    let data = ev.dataTransfer.getData("text");
    ev.target.appendChild(document.getElementById(data));
}