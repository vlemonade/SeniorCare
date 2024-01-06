function openModal() {
    document.getElementById("addSeniorModal").style.display = "flex";
  }

function closeModal() {
    document.querySelector('.error-message').innerHTML = '';
    document.querySelector('.result-message').innerHTML = '';
    document.getElementById('oscaIdInput').value = '';
    document.getElementById("addSeniorModal").style.display = "none";
  }

  $(document).ready(function() {
    $('#addSeniorForm').submit(function(event) {
        event.preventDefault();

        $('.error-message').html('');
        $('.result-message').html('');

        var formData = $(this).serialize();

        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: formData,
            dataType: 'json',  
            success: function(response) {
                if (response.result.includes('NOT FOUND')) {
                    $('.error-message').html(response.result);
                } else {
                    $('.result-message').html(response.result);

                    if (response.view_info_link) {
                        $('.result-message').append('<a class="info-link" href="' + response.view_info_link + '">View Info</a>');
                    }
                }
            },
            error: function(error) {
                console.log('Error:', error);
            }
        });
    });
});