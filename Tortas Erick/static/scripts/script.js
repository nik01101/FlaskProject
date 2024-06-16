document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registration-form');

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        // Obtener los valores de los campos del formulario
        const firstName = document.getElementById('first-name').value.trim();
        const lastName = document.getElementById('last-name').value.trim();
        const email = document.getElementById('email').value.trim();
        const phoneNumber = document.getElementById('phone-number').value.trim();

        // Validación básica
        if (firstName && lastName && email && phoneNumber) {
            // Aquí puedes agregar código para enviar los datos a tu servidor si es necesario
            alert('Registro exitoso!');
            window.location.href = 'index.html';
        } else {
            alert('Completa este campo');
        }
    });
});
