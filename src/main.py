import os

import uvicorn
from cryptography.fernet import Fernet
from fastapi import FastAPI, Request, HTTPException, Form

import pushup

app = FastAPI()
KEY = os.environ.get('AI_API_KEY')


@app.get("/")
def central():
    return {"hehe": "boi"}


@app.get("/test")
def test():
    pu = pushup.calculate_pushups()
    return {"hehe": str(pu)}


def decrypt_message(encrypted_message):
    f = Fernet(KEY)
    decrypted_message = f.decrypt(encrypted_message).decode()
    return decrypted_message


@app.post('/count_pushups')
async def count_pushups_route(encrypted_video_url: str = Form(...)):
    try:
        video_url = decrypt_message(encrypted_video_url)
        pushup_count = pushup.count_pushups(video_url)
        return {"pushup_count": pushup_count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    uvicorn.run(app, port=5000, host="0.0.0.0")
