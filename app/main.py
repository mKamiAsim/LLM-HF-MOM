from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from core.logging_config import logger


def register_routers(app):  
    from controllers import all_routers    
    for router in all_routers:
        app.include_router(router)


async def background_worker():
    while True:
        logger.info("Background worker running...")
        await asyncio.sleep(10)  # Replace with your logic

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(background_worker())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    
app = FastAPI( lifespan=lifespan,
              title= "Minutes of Meeting (MOM) Service",
              version="1.0.0",
              description="A service to generate and manage Minutes of Meeting (MOM) from audio document using Hugging face Llama model.")

register_routers(app)

