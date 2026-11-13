"""سرور توسعهٔ ارسی — بدون کش، تا تغییرات همان لحظه دیده شوند.
کاربرد: python3 server.py [port]"""
import functools
import http.server
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8090

class NoCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()
    def log_message(self, *a):  # سکوت برای لاگ تمیز
        pass

if __name__ == "__main__":
    http.server.ThreadingHTTPServer(
        ("0.0.0.0", PORT),
        functools.partial(NoCache, directory="/home/user/orsi"),
    ).serve_forever()
