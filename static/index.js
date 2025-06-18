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

const openCameraSettingsButton = document.getElementById("openCameraSettingsButton");
const closeCameraSettingsButton = document.getElementById("closeCameraSettingsButton");
const cameraSettings = document.querySelector(".cameraSettings");
const applyCameraSettingsButton = document.getElementById("applyCameraSettings");

const restartServerButton = document.getElementById("restartServerButton");

const exposureSettingsContainer = document.getElementById("exposureSettings");
const exposureRangeSelector = document.getElementById("exposureRange");
const customExposureContainer = document.getElementById("customExposureContainer");
const customExposureRangeMin = document.getElementById("minExposureRange");
const customExposureRangeMax = document.getElementById("maxExposureRange");
const exposureSlider = document.getElementById("exposureSlider");

customExposureRangeMin.value = exposureSlider.min;
customExposureRangeMax.value = exposureSlider.max;

var numberOfPlayers = 2;
var turn = numberOfPlayers; 

let players = [
    { name: "Player 1", points: [] },
    { name: "Player 2", points: [] },
    { name: "Player 3", points: [] }

];
let currentPlayerIndex = 0;
let lastPoint = null;

const playerNameEl = document.getElementById("playerName");
const totalScoreEl = document.getElementById("totalScore");
const playerPointsContainer = document.getElementById("player");

exposureRangeSelector.addEventListener("change", function() {
    const selectedValue = exposureRangeSelector.value;
    if (selectedValue === "Custom") {
        customExposureContainer.style.display = "flex";
        updateExposureSliderRange();
    } else if (selectedValue === "Windows") {
        customExposureContainer.style.display = "none";
        exposureSlider.min = -13;
        exposureSlider.max = 0;
        document.getElementById("exposureValueText").textContent = exposureSlider.value;
    } else if (selectedValue === "Linux") {
        customExposureContainer.style.display = "none";
        exposureSlider.min = 0;
        exposureSlider.max = 10000;
        document.getElementById("exposureValueText").textContent = exposureSlider.value;
    }
});
customExposureRangeMin.addEventListener("input", updateExposureSliderRange);
customExposureRangeMax.addEventListener("input", updateExposureSliderRange);


document.getElementById("autoExposure").addEventListener("change", function() {
    if (this.checked) {
        exposureSettingsContainer.style.display = "none";
        customExposureContainer.style.display = "none";
    }
    else {
        exposureSettingsContainer.style.display = "flex";
        if (exposureRangeSelector.value === "Custom") {
            customExposureContainer.style.display = "flex";
            updateExposureSliderRange();
        } else {
            customExposureContainer.style.display = "none";
        }
    }
});

function clearPlayerPointsUI() {
    Array.from(playerPointsContainer.querySelectorAll("p")).forEach(p => p.remove());
}

function renderCurrentPlayer() {
    const player = players[currentPlayerIndex];
    playerNameEl.textContent = player.name;
    totalScoreEl.textContent = "Total: " + player.points.reduce((a, b) => a + b, 0);
    clearPlayerPointsUI();
    player.points.forEach(point => {
        const p = document.createElement("p");
        p.textContent = point;
        playerPointsContainer.insertBefore(p, totalScoreEl.nextSibling);
    });
}

function switch_turn() {
    currentPlayerIndex = (currentPlayerIndex + 1) % players.length;
    renderCurrentPlayer();
}

function add_player(name) {
    players.push({ name: name, points: [] });
}

function add_point(point) {
    const player = players[currentPlayerIndex];
    player.points.push(point);
    lastPoint = { playerIndex: currentPlayerIndex, pointIndex: player.points.length - 1 };
    renderCurrentPlayer();
}

function updateExposureSliderRange() {
    let minValue = parseInt(customExposureRangeMin.value);
    let maxValue = parseInt(customExposureRangeMax.value);
    if (isNaN(minValue)) minValue = 0;
    if (isNaN(maxValue)) maxValue = 255;
    if (minValue > maxValue) {
        minValue = maxValue;
        customExposureRangeMin.value = minValue;
    }
    if (maxValue < minValue) {
        maxValue = minValue;
        customExposureRangeMax.value = maxValue;
    }
    exposureSlider.min = minValue;
    exposureSlider.max = maxValue;
    if (parseInt(exposureSlider.value) < minValue) exposureSlider.value = minValue;
    if (parseInt(exposureSlider.value) > maxValue) exposureSlider.value = maxValue;
    document.getElementById("exposureValueText").textContent = exposureSlider.value;
}

function requestCameraSettings() {
    socket.emit('requestCameraSettings');
}

function updateCameraSettings() {
    socket.emit('updateCameraSettings', {
        focus: Number(focusSlider.value),
        autoFocus: document.getElementById("autoFocus").checked ? 1 : 0,
        exposure: Number(exposureSlider.value),
        autoExposure: document.getElementById("autoExposure").checked ? 1 : 0
    });
}

function remove_last_point() {
    if (lastPoint && players[lastPoint.playerIndex].points.length > 0) {
        players[lastPoint.playerIndex].points.splice(lastPoint.pointIndex, 1);
        renderCurrentPlayer();
        lastPoint = null;
    }
}

function clear_points() {
    players.forEach(player => player.points = []);
    renderCurrentPlayer();
    scoreImage.src = "../static/Target.png";
    lastPoint = null;
}

focusSlider = document.getElementById("focusSlider");
let previousValue = focusSlider.value;
focusSlider.addEventListener('change', () => {
    if (focusSlider.value !== previousValue) {
        socket.emit('setFocus', focusSlider.value);
        previousValue = focusSlider.value;
    }
});

exposureSlider.addEventListener('input', function() {
    document.getElementById("exposureValueText").textContent = exposureSlider.value;
});
openCameraSettingsButton.addEventListener("click", function() {
    cameraSettings.style.display = "flex";
    openCameraSettingsButton.style.display = "none";
}
);
closeCameraSettingsButton.addEventListener("click", function() {
    cameraSettings.style.display = "none";
    openCameraSettingsButton.style.display = "flex";
    updateCameraSettings();
    socket.emit('recaptureRefImage');
}
);

applyCameraSettingsButton.addEventListener("click", function() {
    updateCameraSettings();
    socket.emit('recaptureRefImage');
});


document.getElementById("clearPointsButton").addEventListener("click", clear_points);
document.getElementById("addPointButton").addEventListener("click", function() {
    add_point(5);
});
document.getElementById("switchTurnButton").addEventListener("click", switch_turn);
document.getElementById("captureRefButton").addEventListener("click", function() {
    socket.emit('recaptureRefImage');
});
acceptShotButton.addEventListener("click", function() {
    socket.emit('acceptShot');
    acceptShotButton.style.display = "none";
    rejectShotButton.style.display = "none";
    acceptText.style.display = "none";
});
rejectShotButton.addEventListener("click", function() {
    socket.emit('rejectShot');
    acceptShotButton.style.display = "none";
    rejectShotButton.style.display = "none";
    acceptText.style.display = "none";
    remove_last_point();
});
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

requestCameraSettings();
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
socket.on('cameraSettings', function(data) {
    focusSlider.value = data.focus;
    document.getElementById("autoFocus").checked = data.autoFocus;
    exposureSlider.value = data.exposure;
    document.getElementById("autoExposure").checked = data.autoExposure;
    if (data.autoExposure) {
        exposureSettingsContainer.style.display = "none";
        customExposureContainer.style.display = "none";
    } else {
        exposureSettingsContainer.style.display = "flex";
    }
});

socket.on('shotDetected', function(data) {
    let score = data;
    add_point(score);
    switch_turn();
    console.log("Shot detected with score:", score);
    acceptShotButton.style.display = "inline-block";
    rejectShotButton.style.display = "inline-block";
    acceptText.style.display = "inline-block";
});
socket.on('scoreImage', function(data) {
    displayImage(scoreImage, data);   
});


function displayImage(imgEl, arrayBuf) {
    const arrayBufferView = new Uint8Array(arrayBuf);
    const blob = new Blob([arrayBufferView], { type: "image/jpeg" });
    const urlCreator = window.URL || window.webkitURL;
    const imageUrl = urlCreator.createObjectURL(blob);
    imgEl.src = imageUrl;
}

renderCurrentPlayer();