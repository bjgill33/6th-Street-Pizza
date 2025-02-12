<script>
    function validatePaymentForm() {
        let isValid = true;
        
        let email = document.getElementById("email");
        let fullName = document.getElementById("fullName");
        let phone = document.getElementById("phone");
        let address = document.getElementById("address");
        let city = document.getElementById("city");
        let state = document.getElementById("state");
        let zip = document.getElementById("zip");

        let emailError = document.getElementById("emailError");
        let fullNameError = document.getElementById("fullNameError");
        let phoneError = document.getElementById("phoneError");
        let addressError = document.getElementById("addressError");
        let cityError = document.getElementById("cityError");
        let stateError = document.getElementById("stateError");
        let zipError = document.getElementById("zipError");

        // Reset errors
        emailError.textContent = "";
        fullNameError.textContent = "";
        phoneError.textContent = "";
        addressError.textContent = "";
        cityError.textContent = "";
        stateError.textContent = "";
        zipError.textContent = "";

        // Email validation
        if (email.value.trim() === "") {
            emailError.textContent = "Email is required.";
            emailError.style.color = "red";
            isValid = false;
        } else if (!/\S+@\S+\.\S+/.test(email.value)) {
            emailError.textContent = "Invalid email format.";
            emailError.style.color = "red";
            isValid = false;
        }

        // Full Name validation
        if (fullName.value.trim() === "") {
            fullNameError.textContent = "Full name is required.";
            fullNameError.style.color = "red";
            isValid = false;
        }

        // Phone validation (Only numbers & length check)
        if (phone.value.trim() === "") {
            phoneError.textContent = "Phone number is required.";
            phoneError.style.color = "red";
            isValid = false;
        } else if (!/^\d{10}$/.test(phone.value)) {
            phoneError.textContent = "Enter a valid 10-digit phone number.";
            phoneError.style.color = "red";
            isValid = false;
        }

        // Address validation
        if (address.value.trim() === "") {
            addressError.textContent = "Address is required.";
            addressError.style.color = "red";
            isValid = false;
        }

        // City validation
        if (city.value.trim() === "") {
            cityError.textContent = "City is required.";
            cityError.style.color = "red";
            isValid = false;
        }

        // State validation
        if (state.value.trim() === "") {
            stateError.textContent = "State selection is required.";
            stateError.style.color = "red";
            isValid = false;
        }

        // Zip code validation (Only numbers & length check)
        if (zip.value.trim() === "") {
            zipError.textContent = "Zip code is required.";
            zipError.style.color = "red";
            isValid = false;
        } else if (!/^\d{5}$/.test(zip.value)) {
            zipError.textContent = "Enter a valid 5-digit zip code.";
            zipError.style.color = "red";
            isValid = false;
        }

        return isValid;
    }
</script>
