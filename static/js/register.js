function showConfirmation() {
    var confirmationPopup = document.getElementById('confirmation-popup');
    if (confirmationPopup) {
        confirmationPopup.style.display = 'block';
    } else {
        console.error("Confirmation popup element not found");
    }
}

function checkOSCAID() {
    const oscaIdInput = document.getElementById('id_osca_id');
    const warningMessage = document.getElementById('form-warning-message');

    if (oscaIdInput && warningMessage) {
        const oscaId = oscaIdInput.value;

        return fetch(`/check_osca_id/?osca_id=${oscaId}`)
            .then(response => response.json())
            .then(data => {
                if (data.is_taken) {
                    warningMessage.innerText = "Oops! It looks like this OSCA ID is already registered.";
                    warningMessage.style.display = 'block';
                    return false;
                } else {
                    return true;
                }
            })
            .catch(error => {
                console.error("Error during OSCA ID check:", error);
                return false;
            });
    } else {
        console.error("OSCA ID input or warning message element not found");
        return false;
    }
}

function areRequiredInputsFilled() {
    const requiredInputs = document.querySelectorAll('[required]');

    for (const input of requiredInputs) {
        if (!input.value.trim()) {
            return false;
        }
    }
    return true;
}

function submitForm() {
    const form = document.getElementById('registrationForm');
    const warningMessage = document.getElementById('form-warning-message');

    if (form) {
        if (form.checkValidity() && areRequiredInputsFilled()) {
            checkOSCAID().then((isOSCAIdAvailable) => {
                if (isOSCAIdAvailable) {
                    form.submit();
                } else {
                    hideConfirmation();
                }
            });
        } else {
            if (warningMessage) {
                warningMessage.innerText = "Please fill out all the required fields!";
                warningMessage.style.display = 'block';
            } else {
                console.error("Warning message element not found");
            }
            hideConfirmation();
            console.error("Form is not valid or required inputs are not filled");
        }
    } else {
        console.error("Form not found");
    }
}

function hideConfirmation() {
    var confirmationPopup = document.getElementById('confirmation-popup');
    if (confirmationPopup) {
        confirmationPopup.style.display = 'none';
    } else {
        console.error("Confirmation popup element not found");
    }
}
