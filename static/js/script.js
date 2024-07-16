

function checkEmail() {
    var email = document.getElementById('email').value;
    var user_id = document.getElementById('user_id') ? document.getElementById('user_id').value : '';
s
    fetch('/check_email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'email=' + encodeURIComponent(email) + '&user_id=' + encodeURIComponent(user_id)
    })
    .then(response => response.json())
    .then(data => {
        if (data.exists) {
            alert('Email já registrado. Por favor, use outro email.');
        }
    })
    .catch(error => console.error('Error:', error));
}

{% endblock %}
