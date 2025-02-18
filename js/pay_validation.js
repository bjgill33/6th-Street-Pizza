document.addEventListener("DOMContentLoaded", function () {
    const fields = ["email", "fullName", "phone", "address", "city", "state", "zip", "cardNumber", "expiryDate", "cvv"];
    
    fields.forEach(field => {
        let input = document.getElementById(field);
        if (input) {
            input.addEventListener("input", function () {
                clearErrorMessage(input);
                validateInput({ target: input });
            });
        }
    });

    
    document.getElementById("paymentForm").addEventListener("submit", handleFormSubmit(validateCheckoutForm));
    document.getElementById("deliveryAddressForm").addEventListener("submit", handleFormSubmit(validateAddressForm));
});

function handleFormSubmit(validateForm) {
    return function (event) {
        if (!validateForm()) {
            event.preventDefault();
        }
    };
}

function clearErrorMessage(input) {
    let errorSpan = document.getElementById(input.id + "Error");
    if (errorSpan) {
        errorSpan.textContent = "";
        errorSpan.style.color = "";
    }
}

function showErrorMessage(errorSpan, message) {
    if (message) {
        errorSpan.textContent = message;
        errorSpan.style.color = "red";
    } else {
        errorSpan.textContent = "";
        errorSpan.style.color = "";
    }
}

function validateInput(event) {
    let input = event.target;
    let errorSpan = document.getElementById(input.id + "Error");
    let value = input.value.trim();
    
    switch (input.id) {
        case "email":
            validateEmail(input, errorSpan);
            break;
        case "fullName":
            validateFullName(input, errorSpan); 
            break;
        case "phone":
            validatePattern(input, errorSpan, /^\d{3}-\d{3}-\d{4}$/, "Format: 123-456-7890");
            break;
        case "state":
            validateState(input, errorSpan);
            break;
        case "zip":
            validatePattern(input, errorSpan, /^\d{5}$/, "Enter a valid 5-digit ZIP code.");
            break;
        case "cardNumber":
            input.value = formatCardNumber(value);
            validatePattern(input, errorSpan, /^\d{4} \d{4} \d{4} \d{4}$/, "Enter a valid 16-digit card number.");
            break;
        case "expiryDate":
            input.value = formatExpiryDate(value);
            validateExpiryDate(input, errorSpan); 
            break;
        case "cvv":
            validatePattern(input, errorSpan, /^\d{3}$/, "Enter a valid 3-digit CVV.");
            break;
        default:
            showErrorMessage(errorSpan, value === "" ? "This field is required." : "");
    }
}

function validatePattern(input, errorSpan, regex, errorMsg) {
    if (!regex.test(input.value.trim())) {
        showErrorMessage(errorSpan, errorMsg);
    } else {
        showErrorMessage(errorSpan, "");
    }
}

function validateEmail(input, errorSpan) {
    let value = input.value.trim();
    let message = "";

    if (value === "") {
        message = "Email is required.";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        message = "Enter a valid email address (e.g., user@example.com).";
    } else {
        let domain = value.split("@")[1];
        let validDomains = ["gmail.com", "yahoo.com", "outlook.com", "icloud.com", "hotmail.com", "aol.com"];
        if (!validDomains.includes(domain)) {
            message = "Enter an email with a valid domain (e.g., Gmail, Yahoo, Outlook).";
        }
    }

    showErrorMessage(errorSpan, message);
}

function validateFullName(input, errorSpan) {
    let value = input.value.trim();
    let nameParts = value.split(/\s+/); 

    if (nameParts.length < 2) {
        showErrorMessage(errorSpan, "Please enter both first and last name.");
    } else {
        showErrorMessage(errorSpan, "");
    }
}

function validateState(input, errorSpan) {
    let value = input.value.trim();
    if (value === "") {
        showErrorMessage(errorSpan, "State is required.");
    } else {
        showErrorMessage(errorSpan, "");
    }
}

function formatCardNumber(value) {
    return value.replace(/\D/g, "").replace(/(.{4})/g, "$1 ").trim().substring(0, 19);
}

function formatExpiryDate(value) {
    return value.replace(/\D/g, "").replace(/^(\d{2})(\d{0,2})/, "$1/$2").substring(0, 5);
}

function validateExpiryDate(input, errorSpan) {
    let value = input.value.trim();
    let message = "";
    
    if (!/^(0[1-9]|1[0-2])\/(\d{2})$/.test(value)) {
        message = "Enter a valid expiration date (MM/YY).";
    } else {
        let currentDate = new Date();
        let currentYear = currentDate.getFullYear();
        let currentMonth = currentDate.getMonth() + 1; 
        let [expiryMonth, expiryYear] = value.split('/');

        expiryMonth = parseInt(expiryMonth);
        expiryYear = parseInt(expiryYear);

        if (expiryYear < (currentYear % 100)) {
            message = "Your credit card has expired.";
        } else if (expiryYear === (currentYear % 100) && expiryMonth < currentMonth) {
            message = "Your credit card has expired.";
        }
    }

    showErrorMessage(errorSpan, message);
}

function validateForm(fields) {
    let isValid = true;
    fields.forEach(id => {
        let input = document.getElementById(id);
        validateInput({ target: input });
        if (document.getElementById(id + "Error").textContent !== "") {
            isValid = false;
        }
    });
    return isValid;
}

function validateCheckoutForm() {
    return validateForm(["email", "fullName", "phone", "address", "city", "state", "zip", "cardNumber", "expiryDate", "cvv"]);
}

function validateAddressForm() {
    return validateForm(["email", "fullName", "phone", "address", "city", "state", "zip"]);
}