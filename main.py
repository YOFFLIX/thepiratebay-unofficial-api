from fastapi import FastAPI
import thepiratebayapi

app = FastAPI()

@app.get("/search/{query}/{category}")
def search(query: str, category: int):
    tpb_instance = thepiratebayapi.ThePirateBayApi()
    return tpb_instance.search(query, category)