"""Web server for the Web Dashboard.

This module provides:
- FastAPI application factory
- Background thread runner for web server
- CORS middleware configuration
"""

import os
import threading
import logging
from typing import Optional
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.core import AppCore
from src.web.routes import api_router, stream_router, websocket_router

logger = logging.getLogger(__name__)


def create_app(app_core: Optional[AppCore] = None) -> FastAPI:
    """Create FastAPI application.

    Args:
        app_core: Optional AppCore instance (uses singleton if not provided)

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Circle Measurement System - Web Dashboard",
        description="REST API for remote monitoring",
        version="2.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware - allow all origins for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router)
    app.include_router(stream_router)
    app.include_router(websocket_router)

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "version": "2.1.0"}

    # Serve static files from web-dashboard directory
    static_dir = Path(__file__).parent.parent.parent / "web-dashboard"
    if static_dir.exists():
        # Serve static files (CSS, JS)
        app.mount("/css", StaticFiles(directory=static_dir / "css"), name="css")
        app.mount("/js", StaticFiles(directory=static_dir / "js"), name="js")

        # Serve index.html at root
        @app.get("/")
        async def root():
            index_path = static_dir / "index.html"
            if index_path.exists():
                return FileResponse(index_path)
            return {"message": "Circle Measurement System - Web Dashboard API", "docs": "/docs"}
    else:
        # No static files - return API info
        @app.get("/")
        async def root():
            return {"message": "Circle Measurement System - Web Dashboard API", "docs": "/docs"}

    return app


class WebServer:
    """Background web server runner.

    This class manages the web server lifecycle, running it in a
    background thread so it doesn't block the main Tkinter event loop.

    Usage:
        server = WebServer(port=8080)
        server.start()
        # ... application runs ...
        server.stop()
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        """Initialize web server.

        Args:
            host: Host to bind to (default: 0.0.0.0 for all interfaces)
            port: Port to listen on (default: 8080)
        """
        self.host = host
        self.port = port
        self._thread: Optional[threading.Thread] = None
        self._server: Optional[uvicorn.Server] = None
        self._running = False
        self._app: Optional[FastAPI] = None

    def start(self) -> bool:
        """Start the web server in a background thread.

        Returns:
            True if started successfully, False otherwise
        """
        if self._running:
            logger.warning("Web server is already running")
            return False

        try:
            # Create the FastAPI app
            self._app = create_app()

            # Configure uvicorn
            config = uvicorn.Config(
                app=self._app,
                host=self.host,
                port=self.port,
                log_level="warning",
                access_log=False,
            )
            self._server = uvicorn.Server(config)

            # Start in background thread
            self._thread = threading.Thread(target=self._run_server, name="WebServer", daemon=True)
            self._thread.start()
            self._running = True

            logger.info(f"Web server started on http://{self.host}:{self.port}")
            return True

        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
            return False

    def _run_server(self) -> None:
        """Run the uvicorn server (called in background thread)."""
        try:
            if self._server is not None:
                self._server.run()
        except Exception as e:
            logger.error(f"Web server error: {e}")
        finally:
            self._running = False

    def stop(self) -> None:
        """Stop the web server."""
        if not self._running:
            return

        try:
            if self._server:
                self._server.should_exit = True

            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=5.0)

            self._running = False
            logger.info("Web server stopped")

        except Exception as e:
            logger.error(f"Error stopping web server: {e}")

    @property
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running

    @property
    def url(self) -> str:
        """Get the server URL."""
        return f"http://{self.host}:{self.port}"


# Global server instance
_web_server: Optional[WebServer] = None


def get_web_server() -> Optional[WebServer]:
    """Get the global web server instance."""
    return _web_server


def start_web_server(host: str = "0.0.0.0", port: int = 8080) -> WebServer:
    """Start the global web server.

    Args:
        host: Host to bind to
        port: Port to listen on

    Returns:
        WebServer instance
    """
    global _web_server

    if _web_server is not None and _web_server.is_running:
        return _web_server

    _web_server = WebServer(host=host, port=port)
    _web_server.start()
    return _web_server


def stop_web_server() -> None:
    """Stop the global web server."""
    global _web_server

    if _web_server is not None:
        _web_server.stop()
        _web_server = None
