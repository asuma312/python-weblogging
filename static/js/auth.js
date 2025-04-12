//tira o event default do form
async function handleRegisterForm(event) {
    event.preventDefault();
    const form = event.target;
    let success_div = document.querySelector("#sucess-message");
    let email = form.querySelector("#email").value;
    let password = form.querySelector("#password").value;
    let confirmPassword = form.querySelector("#confirm-password").value;
    if (password !== confirmPassword) {
        console.log("Passwords do not match");
        CreateErrorModal("Passwords do not match", "Mismatch error");
        return;
    }
    let body = {
    email: email,
    password: password,
    };
    response = await fetch("/api/v1/auth/create_account", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
    });
    if (response.status !== 201) {
        const error = await response.json();
        console.log(error);
        CreateErrorModal(error.error, "Registration error");
        return
    };
    const data = await response.json();
    success_div.innerHTML = `<p>${data.message}</p>`;
    success_div.style.display = "block";
    setTimeout(() => {
        window.location.href = "/login";
    }, 2000);
}

async function handleLoginForm(event) {
    event.preventDefault();
    const form = event.target;
    let success_div = document.querySelector("#sucess-message");
    let email = form.querySelector("#email").value;
    let password = form.querySelector("#password").value;
    let rememberMe = form.querySelector("#remember-me").checked;

    let body = {
        username: email,
        password: password
    };

    response = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
    });

    if (response.status !== 200) {
        const error = await response.json();
        console.log(error);
        CreateErrorModal(error.error, "Login error");
        return;
    }

    const data = await response.json();

    success_div.innerHTML = "<p>Login successful!</p>";
    success_div.style.display = "block";

    setTimeout(() => {
        window.location.href = "/dashboard";
    }, 2000);
}