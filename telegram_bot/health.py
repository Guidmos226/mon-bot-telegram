"""
Serveur HTTP minimaliste pour les health checks de Replit Deployments.
Tourne dans un thread séparé sans bloquer le bot asyncio.
"""
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

logger = logging.getLogger(__name__)


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot actif\n")

    def log_message(self, format, *args):
        pass  # Supprime les logs HTTP verbeux


def start_health_server(port: int = 8080) -> None:
    """Lance le serveur de santé dans un thread daemon (non bloquant)."""
    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info("✅ Serveur de santé démarré sur le port %d", port)
