function showConfirmation() {
  var confirmationPopup = document.getElementById("confirmation-popup");
  if (confirmationPopup) {
    confirmationPopup.style.display = "block";
  } else {
    console.error("Confirmation popup element not found");
  }
}

function hideConfirmation() {
  var confirmationPopup = document.getElementById("confirmation-popup");
  if (confirmationPopup) {
    confirmationPopup.style.display = "none";
  } else {
    console.error("Confirmation popup element not found");
  }
}
