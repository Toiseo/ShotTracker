function displayImage(imgEl, arrayBuf) {

    // https://gist.github.com/harun/825eb53168a3ed9ec4e51de3ecba0801
    const arrayBufferView = new Uint8Array( arrayBuf );
    const blob = new Blob( [ arrayBufferView ], { type: "image/jpeg" } );
    const urlCreator = window.URL || window.webkitURL;
    const imageUrl = urlCreator.createObjectURL( blob );
    imgEl.src = imageUrl;
}


var socket = io();
const targetImage = document.getElementById("createdTargetImage");
const captureRefButton = document.getElementById("captureRefButton");
const drawContoursButton = document.getElementById("drawContours");

drawContoursButton.addEventListener("click", function() {
    socket.emit('drawContours');
});

captureRefButton.addEventListener("click", function() {
    socket.emit('recaptureRefImage');
});

socket.on('refImage', function(data) {
    displayImage(targetImage, data);
});

socket.on('updateCreatedTarget', function(data) {
    if (data) {
        displayImage(targetImage, data);
    } else {
        targetImage.src = "../static/Target.png"; // Reset to default image if no data
    }
});