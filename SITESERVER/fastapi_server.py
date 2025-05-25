# Copied from Pythonanywhere

from fastapi import FastAPI, UploadFile, File, Form, WebSocket, Request, HTTPException, Depends #type:ignore
from fastapi.websockets import WebSocketDisconnect, WebSocketState #type:ignore
from fastapi.responses import JSONResponse #type:ignore
from fastapi.staticfiles import StaticFiles #type:ignore
import os
import json
from datetime import datetime, timedelta, timezone
from fastapi.middleware.cors import CORSMiddleware #type:ignore
from zoneinfo import ZoneInfo
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials #type: ignore
import hashlib
import secrets

os.makedirs("livetiming_data", exist_ok=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount('/pages', StaticFiles(directory="pages"), name="pages")
app.mount("/livetiming_data", StaticFiles(directory="livetiming_data"), name="livetiming_data")
app.mount("/page_data", StaticFiles(directory="page_data"), name="page_data")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Config
CORRECT_PASSWORD = "the password"
BUFFER_SIZE = 100
FLUSH_INTERVAL = 0.25
ET = timezone(timedelta(hours=-4)) 

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
                    live = header.get("header",{}).get("live", False)
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
                        "timestamp": timestamp.isoformat(),
                        "live":live
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
    header_data = None  
    log_file_path = ""

    try:
        while True:
            data = await websocket.receive_text()
            now_et = datetime.now(ET)

            try:
                json_data = json.loads(data)
                message_count += 1

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

                if message_count == 2 and "new_url" in json_data:
                    created_route = json_data["new_url"].replace(" ", "_")
                    date_str = now_et.strftime("%d-%m-%Y_%H-%M")
                    log_file_path = f"livetiming_data/{created_route}_{date_str}.jsonl"
                    log_file = open(log_file_path, "w", buffering=1)
                    await websocket.send_json({
                        "status": "success",
                        "new_route": created_route,
                        "log_file": log_file_path
                    })
                    continue

                if message_count == 3 and log_file and not header_written:
                    header_data = {
                        "header_timestamp": now_et.strftime("%Y-%m-%d %H:%M:%S EDT"),
                        "header": json_data
                    }
                    header_data["header"]["live"] = True  

                    log_file.write(json.dumps(header_data) + "\n")
                    header_written = True
                    await websocket.send_json({
                        "status": "success",
                        "message": "Header written with live:true"
                    })
                    continue

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
                if "INFO_SERVER_PING" in json_data:
                    await websocket.send_json({"INFO_CLIENT_PONG":"bro got ponged fr fr"})
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

            if header_written and header_data:
                try:
                    header_data["header"]["live"] = False
                    with open(log_file_path, "r+") as f:
                        lines = f.readlines()
                        lines[0] = json.dumps(header_data) + "\n"
                        f.seek(0)
                        f.writelines(lines)
                except Exception as e:
                    print(f"Error updating header live status: {e}")

            log_file.close()
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()

@app.post("/create-post")
async def create_post(
    postName: str = Form(...),
    markdown: str = Form(...),
    tags: str = Form(...),
    files: list[UploadFile] = File(default=[])
):
    images_dir = os.path.join("static", postName)
    pages_dir = "pages"
    tags_dir = "page_data"

    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(tags_dir, exist_ok=True)

    saved_files = []

    def unique_filepath(directory, base_name, ext):
        """
        Generate a unique file path in directory, appending _1, _2, etc if needed.
        """
        candidate = os.path.join(directory, base_name + ext)
        counter = 1
        while os.path.exists(candidate):
            candidate = os.path.join(directory, f"{base_name}_{counter}{ext}")
            counter += 1
        return candidate

    for idx, file in enumerate(files):
        ext = os.path.splitext(file.filename)[1].lower()
        ext = ext if ext in [".png", ".jpg", ".jpeg", ".gif"] else ".png"
        base_name = str(idx)
        file_path = unique_filepath(images_dir, base_name, ext)
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        saved_files.append(file_path)

    md_base_name = postName
    md_ext = ".md"
    md_path = unique_filepath(pages_dir, md_base_name, md_ext)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    tags_base_name = postName
    tags_ext = ".txt"
    tags_path = unique_filepath(tags_dir, tags_base_name, tags_ext)
    with open(tags_path, "w", encoding="utf-8") as f:
        f.write(tags)
        f.write(f"\n{datetime.now(tz=ZoneInfo('America/New_York'))}\n")
    return md_base_name


# TODO: os.gettmtime !!! for recently updated posts.
@app.post("/pages_paginated")
async def get_paginated_pages(index: int = 0):
    pages_folder = "pages"
    tags_folder = "page_data"
    page_size = 10
    results = []

    try:
        files = [
            f for f in os.listdir(pages_folder)
            if f.endswith(".md")
        ]

        for filename in files:
            base_name = os.path.splitext(filename)[0]
            txt_path = os.path.join(tags_folder, f"{base_name}.txt")
            post_date = None

            if os.path.exists(txt_path):
                try:
                    with open(txt_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        if len(lines) >= 2:
                            post_date = lines[1].strip()
                            # Try to parse date
                            try:
                                post_date_dt = datetime.fromisoformat(post_date)
                            except ValueError:
                                post_date_dt = datetime.min
                        else:
                            post_date_dt = datetime.min
                except Exception as e:
                    print(f"Failed to read {txt_path}: {e}")
                    post_date_dt = datetime.min
            else:
                post_date_dt = datetime.min

            results.append({
                "filename": filename,
                "post_date": post_date_dt.isoformat()
            })

        results.sort(key=lambda x: x["post_date"], reverse=True)

        start = index * page_size
        end = start + page_size
        paginated = results[start:end]

        return JSONResponse(content={
            "index": index,
            "page_size": page_size,
            "total_files": len(results),
            "results": paginated
        })

    except Exception as e:
        return JSONResponse(content={
            "status": "error",
            "message": str(e)
        }, status_code=500)


# Login system

security = HTTPBearer()

USERS_FILE = "users.json"
TOKENS_FILE = "tokens.json"

os.makedirs("auth_data", exist_ok=True)
USERS_PATH = os.path.join("auth_data", USERS_FILE)
TOKENS_PATH = os.path.join("auth_data", TOKENS_FILE)

for path in [USERS_PATH, TOKENS_PATH]:
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def hash_password(password, salt=None):
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return hashed, salt

def verify_password(password, salt, stored_hash):
    new_hash, _ = hash_password(password, salt)
    return new_hash == stored_hash

def create_token():
    return secrets.token_urlsafe(32)

def get_user_from_token(token: str):
    tokens = load_json(TOKENS_PATH)
    return tokens.get(token)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    username = get_user_from_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return username

@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    users = load_json(USERS_PATH)
    if username in users:
        return {"status": "error", "message": "Username already exists"}

    hashed, salt = hash_password(password)
    users[username] = {"hash": hashed, "salt": salt}
    save_json(USERS_PATH, users)
    return {"status": "success", "message": "User registered"}

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    users = load_json(USERS_PATH)
    if username not in users:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = users[username]
    if not verify_password(password, user["salt"], user["hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token()
    tokens = load_json(TOKENS_PATH)
    tokens[token] = username
    save_json(TOKENS_PATH, tokens)

    return {"status": "success", "token": token}

@app.get("/me")
async def read_me(user: str = Depends(get_current_user)):
    return {"status": "success", "user": user}

@app.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    tokens = load_json(TOKENS_PATH)
    if token in tokens:
        del tokens[token]
        save_json(TOKENS_PATH, tokens)
        return {"status": "success", "message": "Logged out"}
    else:
        return {"status": "error", "message": "Token not found"}
