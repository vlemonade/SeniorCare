function toggle() {
    var blur = document.getElementById('blur');
    blur.classList.toggle('active');

    var popup = document.getElementById('popup');
    popup.classList.toggle('active');
}

function cancel() {
    var blur = document.getElementById('blur');
    blur.classList.remove('active');

    var additionalPopup = document.getElementById('additional-popup');
    additionalPopup.style.display = 'none';
}


document.getElementById('ok-btn').addEventListener('click', function () {
    if (validateInputs()) {
        saveAllowance(function (success) {
            if (success) {
                var blur = document.getElementById('blur');
                const cameraPageUrl = blur.getAttribute('data-camera-url');
                window.location.href = cameraPageUrl;
            } else {
                console.error('Failed to save allowance.');
            }
        });
    } else {
        openWarningPopup();
    }
});

function openWarningPopup() {
    var warningPopup = document.getElementById('warning-popup');
    var additionalPopup = document.getElementById('additional-popup');

    additionalPopup.style.display = 'none';
    warningPopup.style.display = 'block';
}
function closeWarningPopup() {
    var blur = document.getElementById('blur');
    blur.classList.remove('active');

    var warningPopup = document.getElementById('warning-popup');
    warningPopup.style.display = 'none';
}

function validateInputs() {
    var allowanceTypeElement = document.getElementById('allowanceType');
    var allowanceAmount = document.getElementById('allowanceAmount').value;

    if (!allowanceTypeElement.value || !allowanceAmount) {
        return false;
    }

    return true;
}

function saveAllowance(callback) {
    var allowanceTypeElement = document.getElementById('allowanceType');
    var allowanceType = allowanceTypeElement.options[allowanceTypeElement.selectedIndex].value;

    var allowanceAmount = document.getElementById('allowanceAmount').value;

    var csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

    var xhr = new XMLHttpRequest();
    xhr.open('POST', saveAllowanceUrl, true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

    var data = 'allowanceType=' + encodeURIComponent(allowanceType) +
               '&allowanceAmount=' + encodeURIComponent(allowanceAmount) +
               '&csrfmiddlewaretoken=' + encodeURIComponent(csrfToken);

    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.status === 'success') {
                    callback(true);
                } else {
                    callback(false);
                    console.error('Failed to save allowance.');
                }
            }
        }
    };

    xhr.send(data);
}


function toggleAdditionalPopup() {
    var blur = document.getElementById('blur');
    var additionalPopup = document.getElementById('additional-popup');
    blur.classList.toggle('active');
    additionalPopup.style.display = additionalPopup.style.display === 'none' ? 'block' : 'none';
}


