import os
import httpx
import tempfile

async def download_voice_message(file_url: str) -> str:
    """Download voice message to a temporary file"""
    async with httpx.AsyncClient() as client:
        response = await client.get(file_url)
        if response.status_code != 200:
            raise Exception("Failed to download voice message")
        
        # Create temp file with .ogg extension since Telegram uses OGG format
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
            temp_file.write(response.content)
            return temp_file.name

async def transcribe_audio(file_path: str) -> str:
    """Transcribe audio file using OpenAI's Whisper API"""
    try:
        async with httpx.AsyncClient() as client:
            with open(file_path, 'rb') as audio:
                response = await client.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={
                        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
                    },
                    files={
                        "file": audio,
                    },
                    data={
                        "model": "whisper-1",
                    },
                    timeout=30.0
                )
            
            if response.status_code != 200:
                raise Exception(f"Transcription failed: {response.text}")
            
            return response.json()["text"]
    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path) 