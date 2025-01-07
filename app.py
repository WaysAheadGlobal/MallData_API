import json
import pyodbc
from fastapi import FastAPI, Query, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from datetime import datetime
import uvicorn

# ----------------- Database Connection Setup -----------------
DB_CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=103.239.89.99,21433;"
    "DATABASE=RetailMEApp_DB;"
    "UID=RetailMEAppUsr;"
    "PWD=App*Retail8usr"
)

# ----------------- Connect to MSSQL -----------------
def get_db_connection():
    return pyodbc.connect(DB_CONNECTION_STRING)

# ----------------- Load Mall Data -----------------
with open("mall.json", "r", encoding="utf-8") as file:
    mall_data = json.load(file)

# ----------------- FastAPI Setup -----------------
app = FastAPI()
security = HTTPBasic()

# ----------------- Authentication -----------------
def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user exists in the api_keys table
    cursor.execute(
        "SELECT email FROM api_keys WHERE email = ? AND api_key = ?",
        (credentials.username, credentials.password)
    )
    user = cursor.fetchone()
    
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return credentials.username

# ----------------- Log API Call -----------------
def log_api_call(email, endpoint, query, ip_address):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO api_logs (email, endpoint, query, ip_address) VALUES (?, ?, ?, ?)",
        (email, endpoint, query, ip_address)
    )
    
    conn.commit()
    conn.close()

# ----------------- API Endpoints -----------------
@app.get("/api/malls")
async def search_malls_fastapi(
    request: Request,
    username: str = Depends(authenticate_user), 
    q: str = Query(default="", description="Search query for malls")
):
    # Extract IP Address with Fallback
    client_ip = request.client.host if request.client else request.headers.get("X-Forwarded-For", "unknown")

    # Log API Call
    log_api_call(username, "/api/malls", q, client_ip)

    # Mall Query
    if not q:
        ibn_buttata_mall = next((mall for mall in mall_data if mall["name"].lower() == "ibn battuta mall"), None)
        if ibn_buttata_mall:
            return JSONResponse(content=ibn_buttata_mall)
        raise HTTPException(status_code=404, detail="IBN Buttata Mall not found.")
    
    results = [mall for mall in mall_data if q.lower() in mall["name"].lower()]
    if not results:
        raise HTTPException(status_code=404, detail="No malls found matching the query.")
    
    return results

# ----------------- Run the API -----------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
