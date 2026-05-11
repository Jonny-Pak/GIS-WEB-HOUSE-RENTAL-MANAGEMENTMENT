document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.toggle-password').forEach(button => {
        button.addEventListener('click', function () {
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');
            if (input && icon) {
                if (input.type === 'password') {
                    input.type = 'text';
                    icon.classList.remove('bi-eye');
                    icon.classList.add('bi-eye-slash');
                } else {
                    input.type = 'password';
                    icon.classList.remove('bi-eye-slash');
                    icon.classList.add('bi-eye');
                }
            }
        });
    });

    // Remove default border radius on the right side of the password inputs
    document.querySelectorAll('.input-group .register-input').forEach(input => {
        input.style.borderTopRightRadius = '0';
        input.style.borderBottomRightRadius = '0';
        input.style.borderRight = 'none';
    });
});
