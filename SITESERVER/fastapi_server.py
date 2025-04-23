"""Copied from Python Anywhere"""
from fastapi import FastAPI, WebSocket #type:ignore
from fastapi.websockets import WebSocketDisconnect, WebSocketState #type:ignore
from fastapi.responses import JSONResponse #type:ignore
from fastapi.staticfiles import StaticFile #type:ignore
import os
import json
from datetime import datetime, timedelta, timezone

# Set up directories
os.makedirs("livetiming_data", exist_ok=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static") #type:ignore
app.mount("/livetiming_data", StaticFiles(directory="livetiming_data"), name="livetiming_data") #type:ignore

# Config
CORRECT_PASSWORD = "the password"
BUFFER_SIZE = 100
FLUSH_INTERVAL = 0.25
ET = timezone(timedelta(hours=-4))  # Eastern Daylight Time (EDT)

@app.get("/")
async def read_index():
    return "hi"

@app.get("/all_races")
async def get_all_results():
    folder_path = "livetiming_data"
    results = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".jsonl"):
            filepath = os.path.join(folder_path, filename)
            try:
                with open(filepath, "r") as f:
                    first_line = f.readline()
                    header = json.loads(first_line)

                    name = header.get("header", {}).get("name") or filename.replace(".jsonl", "")
                    place = header.get("header", {}).get("place", "Unknown")
                    timestamp_str = header.get("header_timestamp")

                    try:
                        if timestamp_str:
                            timestamp_clean = timestamp_str.rsplit(" ", 1)[0]
                            timestamp = datetime.strptime(timestamp_clean, "%Y-%m-%d %H:%M:%S")
                        else:
                            timestamp = datetime.min
                    except Exception as e:
                        print(f"Failed to parse timestamp in {filename}: {e}")
                        timestamp = datetime.min

                    results.append({
                        "filename": filename,
                        "name": name,
                        "place": place,
                        "timestamp": timestamp.isoformat()
                    })

            except Exception as e:
                print(f"Error processing {filename}: {e}")

    results.sort(key=lambda x: x["timestamp"], reverse=True)
    return JSONResponse(content=results)

@app.websocket("/livetiming-ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    authenticated = False
    created_route = ""
    log_file = None
    write_buffer = []
    last_flush_time = datetime.now()
    message_count = 0
    header_written = False

    try:
        while True:
            data = await websocket.receive_text()
            now_et = datetime.now(ET)

            try:
                json_data = json.loads(data)
                message_count += 1

                # 1. Authentication
                if not authenticated:
                    if json_data.get("password") == CORRECT_PASSWORD:
                        authenticated = True
                        await websocket.send_json({
                            "status": "success",
                            "message": "Authentication successful"
                        })
                        continue
                    else:
                        await websocket.send_json({
                            "status": "error",
                            "message": "Invalid password"
                        })
                        await websocket.close()
                        return

                # 2. Create route and file
                if message_count == 2 and "new_url" in json_data:
                    created_route = json_data["new_url"].replace(" ", "_")
                    date_str = now_et.strftime("%d-%m-%Y_%H-%M")
                    filename = f"livetiming_data/{created_route}_{date_str}.jsonl"
                    log_file = open(filename, "w", buffering=1)
                    await websocket.send_json({
                        "status": "success",
                        "new_route": created_route,
                        "log_file": filename
                    })
                    continue

                # 3. Header
                if message_count == 3 and log_file and not header_written:
                    header_entry = json.dumps({
                        "header_timestamp": now_et.strftime("%Y-%m-%d %H:%M:%S EDT"),
                        "header": json_data
                    })
                    log_file.write(header_entry + "\n")
                    header_written = True
                    await websocket.send_json({
                        "status": "success",
                        "message": "Header written"
                    })
                    continue

                # 4. Livedata
                if "livedata" in json_data and log_file:
                    log_entry = json.dumps({
                        "timestamp": now_et.strftime("%H:%M:%S.%f EDT")[:-3],
                        "data": json_data["livedata"]
                    })
                    write_buffer.append(log_entry)

                    await websocket.send_json({
                        "status": "success",
                        "message": "Data received"
                    })

                    time_elapsed = (datetime.now() - last_flush_time).total_seconds()
                    if len(write_buffer) >= BUFFER_SIZE or time_elapsed >= FLUSH_INTERVAL:
                        log_file.write("\n".join(write_buffer) + "\n")
                        write_buffer.clear()
                        last_flush_time = datetime.now()

            except json.JSONDecodeError:
                await websocket.send_json({
                    "status": "error",
                    "message": "Invalid JSON format"
                })
                break
            except Exception as e:
                await websocket.send_json({
                    "status": "error",
                    "message": f"Internal error: {str(e)}"
                })

    except WebSocketDisconnect:
        print(f"Client disconnected from route '{created_route}'")
    finally:
        if log_file:
            if write_buffer:
                log_file.write("\n".join(write_buffer) + "\n")
            log_file.close()
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()
