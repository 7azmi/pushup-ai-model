import uvicorn

import pushup
from fastapi import FastAPI, HTTPException, Form
from cryptography.fernet import Fernet

app = FastAPI()

# Generate a secret key for encryption
secret_key = Fernet.generate_key()
cipher_suite = Fernet(secret_key)

@app.get("/")
def central():
    return {"hehe": "boi"}


@app.get("/test")
def test():
    pu = pushup.calculate_pushups()
    return {"hehe": str(pu)}

class VideoLinkWithToken:
    def __init__(self, video_url: str):
        self.video_url = video_url
        self.encrypted_token = self.encrypt_token()

    def encrypt_token(self):
        token = "your_secret_token"  # Replace with your secret token
        encrypted_token = cipher_suite.encrypt(token.encode())
        return encrypted_token

@app.post('/count_pushups')
async def count_pushups_route(video_link_with_token: VideoLinkWithToken = Form(...)):
    try:
        decrypted_token = cipher_suite.decrypt(video_link_with_token.encrypted_token).decode()
        if decrypted_token == "your_secret_token":  # Replace with your secret token
            pushup_count = pushup.count_pushups(video_link_with_token.video_url)
            return {"pushup_count": pushup_count}
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid input")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    uvicorn.run(app, port=5000, host="0.0.0.0")
