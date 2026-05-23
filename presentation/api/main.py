from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from presentation.routes.auctions_routes import router as auctions_router
from presentation.routes.add_bid_route import router as add_bid_router
from presentation.api.exception_handlers import setup_exception_handlers

app = FastAPI(
    title="Auction API (DDD)",
    description="API do Bounded Context de Leilões construída com Arquitetura Limpa",
    version="1.0.0"
)

app.include_router(auctions_router)
app.include_router(add_bid_router)

setup_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


