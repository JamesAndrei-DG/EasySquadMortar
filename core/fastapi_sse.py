from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
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
pause_for_waypoint_generator.clear()
long = 0
long_temp = 0
lat = 0
lat_temp = 0
frequency = 4
seconds_per_frequency = 1 / frequency
running = True
buffer = 3
counter = 0


def set_waypoint(coordinates: tuple[int, int]) -> None:
    global long, lat, counter
    long, lat = coordinates
    counter = 0


def resume() -> None:
    pause_for_waypoint_generator.set()


def pause() -> None:
    pause_for_waypoint_generator.clear()


def generate_event() -> str:
    global lat_temp, long_temp
    lat_temp = lat
    long_temp = long

    event = "add"
    data = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lat, long]},
        "properties": {"id": 1, "lat": lat, "lon": long},
    }
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def waypoints_generator() -> list:
    global counter
    while running:

        await pause_for_waypoint_generator.wait()
        await sleep(seconds_per_frequency)
        if lat == lat_temp and long == long_temp and counter > buffer:
            continue
        yield generate_event()
        print(f"x: {long} y: {lat}")
        counter += 1


@app.get("/impact-point")
async def root() -> StreamingResponse:
    return StreamingResponse(waypoints_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
