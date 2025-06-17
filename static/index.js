function displayImage(imgEl, arrayBuf) {

    // https://gist.github.com/harun/825eb53168a3ed9ec4e51de3ecba0801
    const arrayBufferView = new Uint8Array( arrayBuf );
    const blob = new Blob( [ arrayBufferView ], { type: "image/jpeg" } );
    const urlCreator = window.URL || window.webkitURL;
    const imageUrl = urlCreator.createObjectURL( blob );
    imgEl.src = imageUrl;
}

const targetImage = document.getElementById("targetImage");
const diffImage = document.getElementById("diffImage");
const scoreImage = document.getElementById("scoreImage");

const acceptText = document.getElementById("acceptText");
const acceptShotButton = document.getElementById("acceptShotButton");
const rejectShotButton = document.getElementById("rejectShotButton");

const restartServerButton = document.getElementById("restartServerButton");

var numberOfPlayers = 2;
var turn = numberOfPlayers; 

var p1 = "Alfred"
var p2 = "Pappa"

var lastPoint = null;

defaultTurnText = document.getElementById("player" + turn + "Name");
var defaultTurnColor = defaultTurnText.style.color;
var defaultTurnFontSize = defaultTurnText.style.fontSize;

switch_turn();


function switch_turn() {
    var lastTurnText = document.getElementById("player" + turn + "Name");
    if (turn === numberOfPlayers) {
        turn = 1;
    } else {
        turn++;
    }
    var turnText = document.getElementById("player" + turn + "Name");
    turnText.style.color = "lime";
    turnText.style.fontSize = "1.5em";
    lastTurnText.style.color = defaultTurnColor
    lastTurnText.style.fontSize = defaultTurnFontSize;

}

function updateTotalScore(player) {
    switch (player) {
        case 1:
            var player1 = document.getElementById("player1");
            var totalScoreP1 = document.getElementById("totalScoreP1");
            var points1 = player1.querySelectorAll("p");
            var totalScore1 = 0;
            for (var i = 0; i < points1.length; i++) {
                totalScore1 += parseInt(points1[i].textContent, 10);
            }
            totalScoreP1.textContent = "Total: " + totalScore1;
            break;
        case 2:
            var player2 = document.getElementById("player2");
            var totalScoreP2 = document.getElementById("totalScoreP2");
            var points2 = player2.querySelectorAll("p");
            var totalScore2 = 0;
            for (var i = 0; i < points2.length; i++) {
                totalScore2 += parseInt(points2[i].textContent, 10);
            }
            totalScoreP2.textContent = "Total: " + totalScore2;
            break;
        default:
            console.error("Invalid player number");
            break;
    }
}

function clear_points(){
    var player1 = document.getElementById("player1");
    var points1 = player1.querySelectorAll("p");
    for (var i = 0; i < points1.length; i++) {
        points1[i].remove();
    }
    var player2 = document.getElementById("player2");
    var points2 = player2.querySelectorAll("p");
    for (var i = 0; i < points2.length; i++) {
        points2[i].remove();
    }
    scoreImage.src = "../static/Target.png"
    updateTotalScore(1);
    updateTotalScore(2);
    lastPoint = null;
}

function add_point(player, point) {
    switch (player) {
        case 1:
            var player1 = document.getElementById("player1");
            var newPoint1 = document.createElement("p");
            newPoint1.textContent = point;
            lastPoint = newPoint1;
            player1.insertBefore(newPoint1, player1.lastElementChild);
            updateTotalScore(1);
            break;
        case 2:
            var player2 = document.getElementById("player2");
            var newPoint2 = document.createElement("p");
            newPoint2.textContent = point;
            lastPoint = newPoint2;
            player2.insertBefore(newPoint2, player2.lastElementChild);
            updateTotalScore(2);
            break;
        default:
            console.error("usch och blä")
            break;
    }
}

focusSlider = document.getElementById("focusSlider");
let previousValue = focusSlider.value;

focusSlider.addEventListener('change', () => {
    if (focusSlider.value !== previousValue) {
      socket.emit('setFocus', focusSlider.value);
      previousValue = focusSlider.value;
    }
  });

document.getElementById("clearPointsButton").addEventListener("click", function() {
    clear_points();
});
document.getElementById("addPointButton").addEventListener("click", function() {
    add_point(turn, 5);
});

document.getElementById("switchTurnButton").addEventListener("click", function() {
    switch_turn();
});

document.getElementById("captureRefButton").addEventListener("click", function() {
    socket.emit('recaptureRefImage');
});

acceptShotButton.addEventListener("click", function() {
    socket.emit('acceptShot');
    acceptShotButton.style.display = "none";
    rejectShotButton.style.display = "none";
    acceptText.style.display = "none";
}
);
rejectShotButton.addEventListener("click", function() {
    socket.emit('rejectShot');
    acceptShotButton.style.display = "none";
    rejectShotButton.style.display = "none";
    acceptText.style.display = "none";
    for (let i = 0; i < numberOfPlayers; i++) {
        updateTotalScore(i + 1);
    }
    if (lastPoint) {
        lastPoint.remove();
        lastPoint = null;
    }
}
);

restartServerButton.addEventListener("click", function() {
    socket.emit('restartServer');
    acceptShotButton.style.display = "none";
    rejectShotButton.style.display = "none";
    acceptText.style.display = "none";
    clear_points();
    scoreImage.src = "../static/Target.png";
});


const statusConnectedEl = document.getElementById("statusConnected");
const statusDisconnectedEl = document.getElementById("statusDisconnected");
var socket = io();
socket.on('connect', function() {
    statusConnectedEl.style.display = "block";
    statusDisconnectedEl.style.display = "none";

    socket.emit('requestRefImage');
});

socket.on('disconnect', function() {
    statusConnectedEl.style.display = "none";
    statusDisconnectedEl.style.display = "block";
});

socket.on('consoleLog', function(data) {
    console.log("[Server Log]", data.message);
});

socket.on('consoleError', function(data) {
    console.error("[Server Error]", data.message);
});

socket.on('refImage', function(data) {
    displayImage(targetImage, data);
});

socket.on('diffImage', function(data) {
    displayImage(diffImage, data);
});

socket.on('shotDetected', function(data) {
    score = data;
    add_point(turn, score);
    switch_turn();
    console.log("Shot detected with score:", score);
    acceptShotButton.style.display = "inline-block";
    rejectShotButton.style.display = "inline-block";
    acceptText.style.display = "inline-block";
});

socket.on('scoreImage', function(data) {
    displayImage(scoreImage, data);   
});