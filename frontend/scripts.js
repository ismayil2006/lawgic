// ✅ 1. Chatbot Functionality
async function sendMessage() {
  const userInput = document.getElementById("user-input").value;
  const responseElement = document.getElementById("response");

  // Connects to FastAPI chatbot endpoint
  const response = await fetch("http://127.0.0.1:8000/chat", {  
      method: "POST",
      headers: {
          "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: userInput })
  });

  const data = await response.json();
  responseElement.innerText = data.response || "Error: " + data.error;
}

// ✅ 2. File Upload
async function uploadFile() {
  const fileInput = document.getElementById("file-upload").files[0];
  const uploadStatus = document.getElementById("upload-status");

  if (!fileInput) {
      uploadStatus.innerText = "Please select a file.";
      return;
  }

  const formData = new FormData();
  formData.append("file", fileInput);

  // Connects to FastAPI upload endpoint
  const response = await fetch("http://127.0.0.1:8000/upload", {  
      method: "POST",
      body: formData
  });

  const data = await response.json();
  uploadStatus.innerText = data.filename
      ? `File uploaded: ${data.filename} (${data.word_count} words)`
      : `Error: ${data.error}`;
}

// ✅ 3. Generate PDF Report
async function generateReport() {
  const content = document.getElementById("report-content").value;
  const reportStatus = document.getElementById("report-status");
  const downloadLink = document.getElementById("download-link");

  // Connects to FastAPI report generation endpoint
  const response = await fetch("http://127.0.0.1:8000/generate-report", {  
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: content })
  });

  if (response.ok) {
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      downloadLink.href = url;
      downloadLink.download = "report.pdf";
      downloadLink.innerText = "Download Report";
      downloadLink.style.display = "block";
  } else {
      reportStatus.innerText = "Error generating report.";
  }
}
