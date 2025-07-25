import logging

from fastapi.middleware.cors import CORSMiddleware


def setup_middlewares(app):
    # Simple CORS configuration
    allow_origins = [
        "http://localhost:3000",  # React development server
        "http://localhost:8080",  # Vue development server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "*"  # Allow all origins in development (remove in production)
    ]
    
    logging.info(f"Setting up CORS with origins: {allow_origins}")

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
