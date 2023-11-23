document.addEventListener('DOMContentLoaded', function () {
    const progressTXT = document.getElementById('progress-txt');
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const captureButton = document.getElementById('capture-btn');  
    const retakeButton = document.getElementById('retake-btn');
    const submitLink = document.getElementById('submit-btn');
    const popup = document.getElementById('confirmation-popup');
    const popupYesButton = document.getElementById('popup-yes-button');
    const popupCancelButton = document.getElementById('popup-cancel-button');
    const cancelButton = document.getElementById('cancel-btn');
    let capturedImage;  
    const seniorId = document.body.dataset.seniorId;

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
        })
        .catch(function (err) {
            console.log("An error occurred: " + err);
        });

    captureButton.addEventListener('click', function () {
        video.pause();
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
        capturedImage = canvas.toDataURL('image/jpeg');  

        retakeButton.style.display = 'block';
        submitLink.style.display = 'block';

        captureButton.style.display = 'none';
    });

    cancelButton.addEventListener('click', function () {
        window.location.href = `/claim_detail_page/${seniorId}/`;
    });

    retakeButton.addEventListener('click', function () {
        video.play();

        retakeButton.style.display = 'none';
        submitLink.style.display = 'none';
        captureButton.style.display = 'block';

    });

    submitLink.addEventListener('click', function (event) {
        event.preventDefault();
        progressTXT.textContent = 'Please wait, we are processing your image..';

        const csrfTokenElement = document.getElementsByName("csrfmiddlewaretoken")[0];
        if (csrfTokenElement) {
            const csrfToken = csrfTokenElement.value;

            console.log(csrfToken);

            fetch(`/facial_recognition/${seniorId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",  
                    "X-CSRFToken": csrfToken,
                },
                body: `captured_image=${encodeURIComponent(capturedImage)}`, 
            })
            .then(response => response.json())
            .then(data => {
                if (data.match) {
                    window.location.href = `/match/${seniorId}/`;
                } else {
                    popup.style.display = 'block';
                }
            })
            .catch(error => {
                console.error("Error during fetch:", error);
            });
        } else {
            console.error("CSRF token element not found.");
        }

    });

    popupYesButton.addEventListener('click', function () {
        popup.style.display = 'none';
        progressTXT.textContent = 'Let\'s try again! Make sure that your face is visible.';
        
        video.play();
        retakeButton.style.display = 'none';
        submitLink.style.display = 'none';
        captureButton.style.display = 'block';
    });

    popupCancelButton.addEventListener('click', function () {
        popup.style.display = 'none';
        window.location.href = `/claim_detail_page/${seniorId}/`;
    });
});
