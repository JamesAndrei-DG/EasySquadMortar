import random
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import json, uvicorn
from asyncio import sleep, Event

# Initialization
app = FastAPI()

# Added middleware to prevent the frontend from causing error
app.add_middleware(
    CORSMiddleware,  # type hint bug https://github.com/fastapi/fastapi/discussions/10968
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PauseEventhandler
pause_for_waypoint_generator = Event()
pause_for_waypoint_generator.set()
long = 0
lat = 0


def set_waypoint(x: int, y: int) -> None:
    global long, lat
    long = long
    lat = lat


def resume() -> None:
    pause_for_waypoint_generator.set()
    pass


def pause() -> None:
    pause_for_waypoint_generator.clear()
    pass


async def waypoints_generator() -> list:
    while True:
        set_waypoint(1, 2)
        await pause_for_waypoint_generator.wait()

        event = "add"
        data = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lat, long]},
            "properties": {"id": 1, "lat": lat, "lon": long},
        }

        formatted_event = (f"event: {event}\n"
                           f"data: {json.dumps(data)}\n\n")

        yield (formatted_event)
        print(f"x: {long}\ny: {lat}")
        await sleep(5)


@app.get("/impact-point")
async def root() -> StreamingResponse:
    return StreamingResponse(waypoints_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
