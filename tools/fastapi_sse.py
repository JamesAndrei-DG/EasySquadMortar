from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json, uvicorn
from asyncio import sleep
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def waypoints_generator():
    while True:
        long = random.randint(-1000, 0)
        lat = random.randint(0, 1000)

        event = "add"
        data = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [long, lat]},
            "properties": {"id": 1, "lat": lat, "lon": long},
        }

        formatted_event = (f"event: {event}\n"
                           f"data: {json.dumps(data)}\n\n")

        yield (formatted_event)
        print(f"x: {lat}\ny: {long}")
        await sleep(5)


@app.get("/impact-point")
async def root():
    return StreamingResponse(waypoints_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
