const form = document.getElementById("authForm");
const tabs = document.querySelectorAll(".tab");
const title = document.getElementById("authTitle");
const subtitle = document.getElementById("authSubtitle");
const confirmField = document.querySelector(".confirm-field");
const errorBox = document.getElementById("formError");
const submitBtn = document.getElementById("submitBtn");
const password = document.getElementById("password");

let mode = "login";

const copy = {
    login: { title: "Welcome back", subtitle: "Sign in to continue to your assistant.", button: "Sign in" },
    register: { title: "Create your account", subtitle: "It takes ten seconds. No email needed.", button: "Create account" }
};

tabs.forEach(tab => {
    tab.addEventListener("click", () => setMode(tab.dataset.mode));
});

function setMode(next) {
    mode = next;
    tabs.forEach(t => t.classList.toggle("active", t.dataset.mode === mode));
    document.querySelector(".tabs").dataset.mode = mode;
    title.textContent = copy[mode].title;
    subtitle.textContent = copy[mode].subtitle;
    submitBtn.querySelector(".btn-label").textContent = copy[mode].button;
    confirmField.hidden = mode !== "register";
    password.autocomplete = mode === "register" ? "new-password" : "current-password";
    errorBox.textContent = "";
}

document.getElementById("togglePassword").addEventListener("click", e => {
    const show = password.type === "password";
    password.type = show ? "text" : "password";
    e.currentTarget.textContent = show ? "Hide" : "Show";
});

form.addEventListener("submit", async e => {
    e.preventDefault();
    errorBox.textContent = "";

    const username = form.username.value.trim();
    const pass = form.password.value;

    if (!username || !pass) {
        return showError("Please fill in your username and password.");
    }
    if (mode === "register" && pass.length < 8) {
        return showError("Password must be at least 8 characters.");
    }
    if (mode === "register" && pass !== form.confirm.value) {
        return showError("Passwords do not match.");
    }

    submitBtn.classList.add("loading");
    submitBtn.disabled = true;

    try {
        const res = await fetch(mode === "login" ? "/api/login" : "/api/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password: pass })
        });

        if (res.ok) {
            window.location.href = "/";
            return;
        }

        const data = await res.json().catch(() => ({}));
        showError(typeof data.detail === "string" ? data.detail : "Something went wrong. Try again.");
    } catch {
        showError("Cannot reach the server.");
    } finally {
        submitBtn.classList.remove("loading");
        submitBtn.disabled = false;
    }
});

function showError(message) {
    errorBox.textContent = message;
    form.classList.remove("shake");
    void form.offsetWidth;
    form.classList.add("shake");
}
