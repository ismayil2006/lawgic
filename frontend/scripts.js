let messages = [];

async function sendMessage() {
    const userInput = document.getElementById("chat-input").value;
    const chatSection = document.getElementById("chat-section");
    const generatePdfBtn = document.getElementById("generate-pdf-btn");

    if (!userInput.trim()) {
        alert("Please enter a message!");
        return;
    }

    messages.push({ role: "user", content: userInput });

    const userMessage = document.createElement("div");
    userMessage.className = "chat-message";
    userMessage.textContent = `You: ${userInput}`;
    chatSection.appendChild(userMessage);

    document.getElementById("chat-input").value = "";

    try {
        const response = await fetch("http://127.0.0.1:8000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ messages: messages }),
        });

        const data = await response.json();

        if (data.response) {
            messages.push({ role: "assistant", content: data.response });

            const botMessage = document.createElement("div");
            botMessage.className = "chat-message";
            botMessage.textContent = `Bot: ${data.response}`;
            chatSection.appendChild(botMessage);
        }

        if (messages.length > 1) {
            generatePdfBtn.disabled = false;
        }
    } catch (error) {
        console.error("Error:", error);
    }
}
