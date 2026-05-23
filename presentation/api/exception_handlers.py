from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from domain.Exceptions.domain_exceptions import DomainException
from application.exceptions.application_exceptions import AuctionNotFoundError, ApplicationException, UnauthorizedActionError


def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(AuctionNotFoundError)
    async def handle_not_found(request: Request, exc: AuctionNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"error": str(exc)})

    @app.exception_handler(UnauthorizedActionError)
    async def handle_unauthorized(request: Request, exc: UnauthorizedActionError) -> JSONResponse:
        return JSONResponse(status_code=403, content={"error": str(exc)})
        
    @app.exception_handler(DomainException)
    async def handle_domain_error(request: Request, exc: DomainException) -> JSONResponse:
        return JSONResponse(status_code=400, content={"error": str(exc)})

    @app.exception_handler(ApplicationException)
    async def handle_application_error(request: Request, exc: ApplicationException) -> JSONResponse:
        return JSONResponse(status_code=500, content={"error": str(exc)})
