import base64
import os

import uvicorn
from cryptography.fernet import Fernet
from fastapi import FastAPI, Request, HTTPException, Form

import pushup

app = FastAPI()
KEY = os.environ.get('AI_API_KEY', 'OR9Hdu3NKcaT4PPHJni3NAepp61DL_SGeOmB2Eg7PT0=')
test = os.environ.get('TST', 'it is not working')
print(test)




@app.get("/")
def central():
    return {"hehe": "boi"}


@app.get("/test")
def test():
    pu = pushup.calculate_pushups()
    return {"hehe": str(pu)}


def decrypt_message(encrypted_message):
    #key = KEY.encode()
    f = Fernet(KEY)
    decrypted_message = f.decrypt(encrypted_message).decode()
    return decrypted_message

def encrypt_message(message):
    #key = KEY.encode()
    f = Fernet(KEY)
    encrypted_message = f.encrypt(message.encode())
    return encrypted_message

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
    lol = 'hehe boi'

    #print(decrypt_message(encrypt_message(lol)))

    uvicorn.run(app, port=5000, host="0.0.0.0")
