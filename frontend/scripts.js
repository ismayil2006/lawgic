let messages = [];

document.addEventListener("DOMContentLoaded", function () {

    document.getElementById("chat-input").addEventListener("keypress", function (e) {
        if (e.key === "Enter") sendMessage();
    });

    document.querySelector("button[onclick='sendMessage()']").addEventListener("click", sendMessage);
    document.querySelector("button[onclick='generateReport()']").addEventListener("click", generateReport);
});


document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("find-lawyer-btn").addEventListener("click", findLawyer);
});

async function findLawyer() {
    const location = document.getElementById("user-location").value.trim();
    const category = document.getElementById("lawyer-category").value;
    const range = document.getElementById("lawyer-range").value;

    if (!location) {
        alert("Please enter your city.");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/find-lawyer", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ location, category, range })
        });

        const data = await response.json();
        
        if (data.lawyers.length > 0) {
            let results = "🔹 **Recommended Lawyers:**\n";
            data.lawyers.forEach((lawyer, index) => {
                results += `**${index + 1}. ${lawyer.name}** - ${lawyer.specialty}\n📍 ${lawyer.location}\n📞 ${lawyer.contact}\n\n`;
            });

            displayMessage("Bot", results); // Show results in chat area
        } else {
            displayMessage("Bot", "❌ No lawyers found for your criteria.");
        }
    } catch (error) {
        console.error("🚨 Error fetching lawyers:", error);
        displayMessage("Bot", "❌ Failed to find lawyer recommendations.");
    }
}

// ✅ Helper function to display messages in the chat area
function displayMessage(sender, message) {
    const chatSection = document.getElementById("chat-section");
    const botMessage = document.createElement("div");
    botMessage.className = "chat-message";
    botMessage.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatSection.appendChild(botMessage);
}

// ✅ Function to switch between pages
function showPage(pageId) {
    // ✅ Prevent accidental reload by checking if we're already on the page
    const currentPage = document.querySelector(".container[style*='block']");
    if (currentPage && currentPage.id === pageId) {
        return;  // ✅ Do nothing if already on the selected page
    }

    document.querySelectorAll(".container").forEach(container => {
        container.style.display = "none";
    });

    document.getElementById(pageId).style.display = "block";
}

// ✅ Send Message & Enable Multiturn Chat (Retaining History)
async function sendMessage() {
    const userInput = document.getElementById("chat-input").value.trim();
    const chatSection = document.getElementById("chat-section");

    if (!userInput) {
        return; // ✅ Do nothing if input is empty
    }

    // ✅ Append user's message
    messages.push({ role: "user", content: userInput });

    const userMessage = document.createElement("div");
    userMessage.className = "chat-message";
    userMessage.textContent = `You: ${userInput}`;
    chatSection.appendChild(userMessage);
    
    document.getElementById("chat-input").value = ""; // Clear input field

    // ✅ Append bot thinking message
    const botMessage = document.createElement("div");
    botMessage.className = "chat-message";
    botMessage.textContent = "Bot: ...";
    chatSection.appendChild(botMessage);

    try {
        const response = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ messages: messages }),
        });

        const data = await response.json();

        if (data.response) {
            messages.push({ role: "assistant", content: data.response }); // ✅ Store response for multiturn conversation
            botMessage.textContent = `Bot: ${data.response}`;
        } else {
            botMessage.textContent = `Bot: (Error: ${data.error})`;
        }

        document.getElementById("generate-pdf-btn").disabled = false; // ✅ Enable PDF report button

    } catch (error) {
        botMessage.textContent = "Bot: (Error connecting to server)";
    }
}

// ✅ Generate PDF Report with Full Conversation
async function generateReport() {
    // ✅ Show warning before proceeding
    const confirmAction = confirm(
        "⚠ WARNING: If this button is pressed, the conversation will be terminated and you will be taken to the home page."
    );

    if (!confirmAction) return; // ✅ If user cancels, stop execution

    try {
        const response = await fetch("http://127.0.0.1:8000/generate-report", {
            method: "POST"
        });

        if (!response.ok) return;

        // ✅ Convert response into a downloadable PDF file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "disclaimer.pdf";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        // ✅ Redirect user to home page after generating PDF
        showPage("home");

    } catch (error) {
        console.error("🚨 PDF Generation Failed:", error.message);
    }

}    