"""سرور توسعهٔ ارسی — بدون کش، تا تغییرات همان لحظه دیده شوند."""
import functools
import http.server

class NoCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

if __name__ == "__main__":
    http.server.ThreadingHTTPServer(
        ("0.0.0.0", 8090),
        functools.partial(NoCache, directory="/home/user/orsi"),
    ).serve_forever()
