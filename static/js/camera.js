document.addEventListener("DOMContentLoaded", function () {
    var video = document.getElementById("live-camera-feed");

    document.getElementById("capture-button").addEventListener("click", function () {
        video.pause();

        document.getElementById("retake-button").style.display = "block";
        document.getElementById("upload-button").style.display = "block";

        document.getElementById("capture-button").style.display = "none";
        document.getElementById("cancel-button").style.display = "none";

        document.getElementById("captured-image").src = "";
    });

    document.getElementById("upload-button").addEventListener("click", function () {

        var canvas = document.createElement("canvas");
        var context = canvas.getContext("2d");
        canvas.width = 300;
        canvas.height = 300;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        var imageDataUrl = canvas.toDataURL("image/jpeg");

        fetch("/capture_image/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                image_data: imageDataUrl,
            }),
        })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                var seniorImageElements = document.getElementsByName("senior_image");
                if (seniorImageElements.length > 0) {
                    seniorImageElements[0].value = data.image_path;
                } else {
                    console.error("No element with name 'senior_image' found.");
                }

                document.getElementById("captured-image").src = data.image_path;

                var currentDate = new Date();
                var formattedDate = currentDate.toISOString().slice(0, 10); 
            
            
                saveAndDownloadImage(imageDataUrl, "seniorcare" + formattedDate);

                document.getElementById("retake-button").style.display = "block";
                document.getElementById("upload-button").style.display = "block";

                window.close();
            })
            .catch(function (error) {
                console.log(error);
            });
    });

    document.getElementById("retake-button").addEventListener("click", function () {
        video.play();

        document.getElementById("retake-button").style.display = "none";
        document.getElementById("upload-button").style.display = "none";

        document.getElementById("capture-button").style.display = "block";
        document.getElementById("cancel-button").style.display = "block";

        document.getElementById("captured-image").src = "";
    });

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
        })
        .catch(function (error) {
            console.log("Error accessing camera:", error);
        });
});


function saveAndDownloadImage(dataURL, fileName) {
    var link = document.createElement('a');
    link.href = dataURL;
    link.download = fileName + '.png'; 
   
    document.body.appendChild(link);
    link.click();

    document.body.removeChild(link);
}



