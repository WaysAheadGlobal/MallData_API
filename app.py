import json
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.wsgi import WSGIMiddleware
import uvicorn
# Load mall data from mall.json
with open("mall.json", "r", encoding="utf-8") as file:
    mall_data = json.load(file)
# -------------------- FastAPI Setup --------------------

app = FastAPI()
@app.get("/api/malls")
async def search_malls_fastapi(q: str = Query(default="", description="Search query for malls")):
    if not q:
        # Return only "IBN Buttata Mall" data if no query is provided
        ibn_buttata_mall = next((mall for mall in mall_data if mall["name"].lower() == "ibn buttata mall"), None)
        if ibn_buttata_mall:
            return JSONResponse(content=ibn_buttata_mall)
        raise HTTPException(status_code=404, detail="IBN Buttata Mall not found.")
    
    # Filter malls by name
    results = [mall for mall in mall_data if q.lower() in mall["name"].lower()]
    if not results:
        raise HTTPException(status_code=404, detail="No malls found matching the query.")
    return results
# -------------------- Run Both Apps --------------------
if __name__ == "__main__":
    # Run FastAPI with Flask mounted
    uvicorn.run(app, host="127.0.0.1", port=8000)
