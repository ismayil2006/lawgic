
  // Load required modules
const axios = require('axios');
require('dotenv').config(); // Load environment variables

const API_KEY = process.env.DID_API_KEY;
if (!API_KEY) {
  console.error("Error: D-ID API key not found. Please check your .env file.");
  process.exit(1);
}

// Use the streaming endpoint (or the appropriate endpoint per your docs)
const CREATE_TALK_URL = "https://api.d-id.com/talks";
// Assume the status-check endpoint uses the talk id in the URL like this:
const CHECK_TALK_URL = (talkId) => `https://api.d-id.com/talks/${talkId}`;

// Function to create a talk (avatar generation)
async function createTalk(text) {
  try {
    const response = await axios.post(CREATE_TALK_URL, {
      script: { type: "text", input: text },
      source_url: "https://www.ehshirts.com/wp-content/uploads/2022/02/womens-formal-shirts.jpg",
    //   config: {
    //     result_format: ".mp4",
    //     // Try reducing the resolution to lower the final file size.
    //     // Common values might be "480p", "360p", or even "240p" depending on what D‑ID supports.
    //     resolution: "480p",
    //     // Lowering the bitrate can help, too.
    //     bitrate: "600k"
    //   }

    }, {
      headers: {
        Authorization: `Basic ${API_KEY}`, // Using Basic auth per your documentation
        "Content-Type": "application/json"
      }
    });
    console.log("Talk Created. Full Response Data:", response.data);
    return response.data.id;
  } catch (error) {
    console.error("Error creating talk:", error.response ? error.response.data : error.message);
    throw error;
  }
}

// Function to poll for the final result using the talk id
async function pollTalkStatus(talkId, interval = 5000, maxAttempts = 12) {
  let attempts = 0;
  while (attempts < maxAttempts) {
    try {
      const response = await axios.get(CHECK_TALK_URL(talkId), {
        headers: {
          Authorization: `Basic ${API_KEY}`,
          "Content-Type": "application/json"
        }
      });
      console.log(`Polling attempt ${attempts + 1}:`, response.data);
      // Check if the talk has completed processing and if the final video URL exists
      if ((response.data.status === "completed" || response.data.status === "done") && response.data.result_url) {
        return response.data.result_url;
      }
    } catch (error) {
      console.error("Error polling talk status:", error.response ? error.response.data : error.message);
    }
    // Wait for the specified interval before trying again
    await new Promise(resolve => setTimeout(resolve, interval));
    attempts++;
  }
  throw new Error("Timed out waiting for talk to complete.");
}

// Main function to create a talk and then poll for the final video URL
async function generateTalkingAvatar(text) {
  try {
    const talkId = await createTalk(text);
    console.log("Talk ID:", talkId);
    const videoUrl = await pollTalkStatus(talkId);
    console.log("Avatar Video URL:", videoUrl);
  } catch (error) {
    console.error("Error generating avatar:", error.message);
  }
}

// Call the main function with a sample text
generateTalkingAvatar("Ismayil you are so hot and manly. Please be my man baby. ISHHHHH, ish, ish, ish");