$(document).ready(function () {
  const openCameraBtn = $("#openCameraBtn");
  const closeModalBtn = $("#closeModal");
  const cameraModal = $("#cameraModal");
  const cameraVideo = $("#cameraVideo")[0];
  const captureBtn = $("#captureBtn");
  const seniorImage = $("#seniorImage")[0];
  const temporaryImageInput = $("#temporaryImageInput");
  let seniors = {
    id: $('#updateForm input[name="senior_id"]').val(),
};

  let mediaStream;
  let temporaryImageDataUrl;

  openCameraBtn.on("click", function () {
      cameraModal.show();

      navigator.mediaDevices
          .getUserMedia({ video: true })
          .then((stream) => {
              mediaStream = stream;
              cameraVideo.srcObject = stream;
          })
          .catch((error) => {
              console.error("Error accessing camera:", error);
          });
  });

  closeModalBtn.on("click", function () {
      cameraModal.hide();

      if (mediaStream) {
          mediaStream.getTracks().forEach((track) => {
              track.stop();
          });
      }
  });

  captureBtn.on("click", function () {
      const canvas = document.createElement("canvas");
      canvas.width = cameraVideo.videoWidth;
      canvas.height = cameraVideo.videoHeight;
      const context = canvas.getContext("2d");
      context.drawImage(cameraVideo, 0, 0, canvas.width, canvas.height);

      new Promise((resolve) => {
          canvas.toBlob(resolve, "image/png");
      }).then((blob) => {
          const reader = new FileReader();
          reader.onloadend = function () {
              temporaryImageDataUrl = reader.result;

              temporaryImageInput.val(temporaryImageDataUrl);

              seniorImage.src = temporaryImageDataUrl;

              cameraModal.hide();

              if (mediaStream) {
                  mediaStream.getTracks().forEach((track) => {
                      track.stop();
                  });
              }
          };
          reader.readAsDataURL(blob);
      });
  });

  $(".cancel-btn").on("click", function (event) {
    event.preventDefault();

    if (seniors && seniors.id) {
        cameraModal.hide();

        if (mediaStream) {
            mediaStream.getTracks().forEach((track) => {
                track.stop();
            });
        }

        window.location.href = "/update_viewinfo_page/" + seniors.id;
    } else {
        console.error("Seniors or seniors.id is undefined.");
    }
});
  $("#updateForm").submit(function (event) {
      if (temporaryImageDataUrl) {
          $("#senior_image").val(temporaryImageDataUrl);
      }

      return true;
  });
});
