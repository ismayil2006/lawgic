let messages = [];

async function sendMessage() {
    const userInput = document.getElementById("chat-input").value;
    const chatSection = document.getElementById("chat-section");
    const generatePdfBtn = document.getElementById("generate-pdf-btn");

    if (!userInput.trim()) {
        alert("Please enter a message!");
        return;
    }

    // Append user message to chat
    messages.push({ role: "user", content: userInput });
    if (messages.length > 5) {
        messages = messages.slice(-5); // Keep only last 5 messages
    }

    const userMessage = document.createElement("div");
    userMessage.className = "chat-message";
    userMessage.textContent = `You: ${userInput}`;
    chatSection.appendChild(userMessage);

    document.getElementById("chat-input").value = "";

    // Create bot's response area immediately
    const botMessage = document.createElement("div");
    botMessage.className = "chat-message";
    botMessage.textContent = "Bot: ..."; // Placeholder until response arrives
    chatSection.appendChild(botMessage);
    
    try {
        const response = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ messages: messages }),
        });

        const data = await response.json();

        if (data.response) {
            messages.push({ role: "assistant", content: data.response });

            botMessage.textContent = `Bot: ${data.response}`;
        } else {
            botMessage.textContent = "Bot: (Error processing response)";
        }

        if (messages.length > 1) {
            generatePdfBtn.disabled = false;
        }
    } catch (error) {
        console.error("Error:", error);
        botMessage.textContent = "Bot: (Error connecting to server)";
    }
}

// Generate PDF Report
async function generateReport() {
    const content = messages.map((msg) => `${msg.role}: ${msg.content}`).join("\n");
    const response = await fetch("http://127.0.0.1:8000/generate-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: content }),
    });

    if (response.ok) {
        alert("PDF Report generated successfully!");
    } else {
        alert("Failed to generate PDF Report.");
    }
}
