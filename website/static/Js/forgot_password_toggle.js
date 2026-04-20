function togglePassword(inputId, eyeId) {
    const input = document.getElementById(inputId);
    const eye = document.getElementById(eyeId);
    if (input.type === "password") {
        input.type = "text";
        eye.classList.remove("bi-eye-slash");
        eye.classList.add("bi-eye");
        eye.style.color = '#007bff';
    } else {
        input.type = "password";
        eye.classList.remove("bi-eye");
        eye.classList.add("bi-eye-slash");
        eye.style.color = '#888';
    }
}
