from flask import Flask, request, jsonify
import json
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.wsgi import WSGIMiddleware
import uvicorn

app = Flask(__name__)

# Load mall data from mall.json
try:
    with open('mall.json', 'r') as file:
        mall_data = json.load(file)
except FileNotFoundError:
    mall_data = []

# -------------------- Flask API --------------------

# API to search malls
@app.route('/api/malls', methods=['GET'])
def search_malls():
    query = request.args.get('q', '').lower()
    
    if not query:
        # Return only "IBN Buttata Mall" data if no query is provided
        result = next((mall for mall in mall_data if mall['name'].lower() == "ibn buttata mall"), None)
        return jsonify(result) if result else jsonify({"message": "IBN Buttata Mall not found."}), 404
    
    # Filter malls by name
    results = [mall for mall in mall_data if query in mall['name'].lower()]

    if not results:
        return jsonify({"message": "No malls found matching the query."}), 404

    return jsonify(results)

# -------------------- FastAPI Setup --------------------

fastapi_app = FastAPI()

@fastapi_app.get("/api/malls")
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

# Mount Flask app inside FastAPI
fastapi_app.mount("/flask", WSGIMiddleware(app))

# -------------------- Run Both Apps --------------------
if __name__ == "__main__":
    # Run FastAPI with Flask mounted
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000)
