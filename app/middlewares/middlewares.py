import logging

from fastapi.middleware.cors import CORSMiddleware

from app.config import config


def setup_middlewares(app):
    allow_origins = config.allowed_origins
    logging.info(f"Allowed CORS origins: {allow_origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "Accept", "Origin", 
                      "X-Requested-With", "Access-Control-Request-Method",
                      "Access-Control-Request-Headers"],
        expose_headers=["Access-Control-Allow-Origin", "Access-Control-Allow-Methods", 
                       "Access-Control-Allow-Headers"],
        max_age=600,
    )
