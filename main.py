from fastapi import FastAPI, HTTPException, Query
import openai


app = FastAPI()


# Set your OpenAI API key
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY


@app.get("/")
def home():
    """
    Home endpoint to verify if the API is running.
    """
    return {"message": "Welcome to the AI Legal Chatbot!"}


@app.post("/chat")
def chat_with_bot(user_input: str = Query(..., description="User's legal inquiry")):
    """
    Chatbot endpoint that takes user input and responds with GPT-4.
    """
    try:
        print("Received user input:", user_input)  # Log input for debugging
       
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI legal assistant specializing in tenant-landlord disputes."},
                {"role": "user", "content": user_input}
            ]
        )
       
        print("OpenAI Response:", response)  # Log response for debugging
        return {"response": response.choices[0].message.content}
   
    except openai.OpenAIError as e:
        # Log OpenAI-specific errors
        print(f"OpenAI Error: {e}")
        raise HTTPException(status_code=500, detail=f"OpenAI Error: {str(e)}")
   
    except Exception as e:
        # Log any other unexpected errors
        print(f"Unexpected Error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)