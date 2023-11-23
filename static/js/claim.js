function toggle() {
    var blur = document.getElementById('blur');
    blur.classList.toggle('active')
    var popup = document.getElementById('popup');
    popup.classList.toggle('active')
}

function cancel() {
    var blur = document.getElementById('blur');
    blur.classList.remove('active');

    var additionalPopup = document.getElementById('additional-popup');
    additionalPopup.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function () {
const yesButton = document.querySelector('.btn-Yes');
const okButton = document.getElementById('ok-btn');
const blur = document.getElementById('blur');
const popup = document.getElementById('popup');
const additionalPopup = document.getElementById('additional-popup');

yesButton.addEventListener('click', function () {
    popup.classList.remove('active');
    additionalPopup.style.display = 'block';
});

okButton.addEventListener('click', function () {
    additionalPopup.style.display = 'none';
    const cameraPageUrl = blur.getAttribute('data-camera-url');
    window.location.href = cameraPageUrl;
});
});