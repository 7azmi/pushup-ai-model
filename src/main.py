import uvicorn
from fastapi import FastAPI, Request, HTTPException, Form

import pushup

app = FastAPI()


@app.get("/")
def central():
    return {"hehe": "boi"}


@app.get("/test")
def test():
    pu = pushup.calculate_pushups()
    return {"hehe": str(pu)}


@app.post('/count_pushups')
async def count_pushups_route(video_url: str = Form(...)):
    if video_url:
        pushup_count = pushup.count_pushups(video_url)
        return {"pushup_count": pushup_count}
    else:
        raise HTTPException(status_code=400, detail="No video URL provided")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    uvicorn.run(app, port=5000, host="0.0.0.0")
