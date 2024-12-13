import random
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import json, uvicorn
from asyncio import sleep, Event

# Initialization
app = FastAPI()

# Middleware Configuration
app.add_middleware(
    CORSMiddleware,  # type hint bug https://github.com/fastapi/fastapi/discussions/10968
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pause Event Handler
pause_for_waypoint_generator = Event()
pause_for_waypoint_generator.set()
long = 0
lat = 0


def set_waypoint(x: int, y: int) -> None:
    global long, lat
    long = x
    lat = y


def resume() -> None:
    pause_for_waypoint_generator.set()


def pause() -> None:
    pause_for_waypoint_generator.clear()


def generate_event(lat: int, long: int) -> str:
    event = "add"
    data = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lat, long]},
        "properties": {"id": 1, "lat": lat, "lon": long},
    }
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def waypoints_generator() -> list:
    while True:
        set_waypoint(2544, -2808)
        await pause_for_waypoint_generator.wait()
        yield generate_event(lat, long)
        print(f"x: {long}\ny: {lat}")
        await sleep(2)


@app.get("/impact-point")
async def root() -> StreamingResponse:
    return StreamingResponse(waypoints_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
