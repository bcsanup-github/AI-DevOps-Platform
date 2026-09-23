const form = document.getElementById("chatForm");
const promptBox = document.getElementById("prompt");
const chatBox = document.getElementById("chatBox");
const emptyState = document.getElementById("emptyState");
const sendButton = document.getElementById("sendButton");

// Escape user/AI text so it can never inject HTML (the old version had an XSS bug)
function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

// Tiny, safe markdown: ```code blocks```, `inline code`, **bold**
function render(text) {
    const parts = escapeHtml(text).split(/```/);
    return parts.map((part, i) => {
        if (i % 2 === 1) {
            const code = part.replace(/^[\w+-]*\n/, "");
            return `<pre><code>${code}</code></pre>`;
        }
        return part
            .replace(/`([^`\n]+)`/g, "<code>$1</code>")
            .replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>")
            .replace(/\n/g, "<br>");
    }).join("");
}

function addMessage(role, text) {
    emptyState.hidden = true;
    const el = document.createElement("div");
    el.className = `msg ${role}`;
    el.innerHTML = `
        <div class="msg-avatar">${role === "user" ? "You" : "AI"}</div>
        <div class="msg-body">${render(text)}</div>`;
    chatBox.appendChild(el);
    chatBox.scrollTop = chatBox.scrollHeight;
    return el;
}

function addTyping() {
    const el = addMessage("ai", "");
    el.querySelector(".msg-body").innerHTML = `<span class="typing"><i></i><i></i><i></i></span>`;
    return el;
}

async function send(prompt) {
    addMessage("user", prompt);
    const typing = addTyping();
    sendButton.disabled = true;

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt })
        });

        if (res.status === 401) {
            window.location.href = "/login";
            return;
        }

        const data = await res.json();
        typing.querySelector(".msg-body").innerHTML = render(data.response ?? "No response.");
    } catch {
        typing.querySelector(".msg-body").innerHTML = render("Could not reach the server. Is the backend running?");
        typing.classList.add("error");
    } finally {
        sendButton.disabled = false;
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}

form.addEventListener("submit", e => {
    e.preventDefault();
    const prompt = promptBox.value.trim();
    if (!prompt || sendButton.disabled) return;
    promptBox.value = "";
    autoGrow();
    send(prompt);
});

promptBox.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        form.requestSubmit();
    }
});

function autoGrow() {
    promptBox.style.height = "auto";
    promptBox.style.height = Math.min(promptBox.scrollHeight, 200) + "px";
}
promptBox.addEventListener("input", autoGrow);

document.querySelectorAll(".suggestion").forEach(btn => {
    btn.addEventListener("click", () => {
        promptBox.value = btn.textContent;
        document.getElementById("sidebar").classList.remove("open");
        form.requestSubmit();
    });
});

document.getElementById("clearBtn").addEventListener("click", async () => {
    await fetch("/api/history", { method: "DELETE" });
    chatBox.querySelectorAll(".msg").forEach(m => m.remove());
    emptyState.hidden = false;
    promptBox.focus();
});

document.getElementById("menuBtn").addEventListener("click", () => {
    document.getElementById("sidebar").classList.toggle("open");
});

// Load this user's previous conversation
(async () => {
    try {
        const res = await fetch("/api/history");
        if (!res.ok) return;
        const items = await res.json();
        items.forEach(c => {
            addMessage("user", c.question);
            addMessage("ai", c.answer);
        });
    } catch { /* ignore */ }
    promptBox.focus();
})();
