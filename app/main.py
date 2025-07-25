from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import asyncio
import core.app_configuration as config
from dotenv import load_dotenv
from core.di import IMOMService, ISharedDataService
from core.logging_config import setup_logging
import logging

load_dotenv()


def register_routers(app):  
    from controllers import all_routers    
    for router in all_routers:
        app.include_router(router)


async def background_worker():
        await IMOMService().download_quantized_model_from_huggingface(model_name=config.LLAMA)

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging() 
    app.state.shared_data = ISharedDataService()   
    task = asyncio.create_task(background_worker())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    for handler in logging.getLogger().handlers:
        handler.flush()
    logging.shutdown()
    
app = FastAPI( lifespan=lifespan,
              title= "Minutes of Meeting (MOM) Service",
              version="1.0.0",
              description="A service to generate and manage Minutes of Meeting (MOM) from audio document using Hugging face Llama model.")

templates = Jinja2Templates(directory="templates")

register_routers(app)

@app.get("/", response_class=HTMLResponse)
async def root(request:Request):
    return templates.TemplateResponse("home.html", 
                                      {"request": request, 
                                       "title": "Welcome to MOM LLM Project",
                                       "user": "Kamran Asim"
                                       })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

