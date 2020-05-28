#!/usr/bin/python3
import os
import time
from http.server import HTTPServer
from socketserver import StreamRequestHandler


class RequestHandler(StreamRequestHandler):
    def handle(self):
        now = int(time.time())
        request_str = b""
        print("\n----- Headers Start ----->\n")
        content_length = 0
        while True:
            result = self.rfile.readline(100000000000000000)
            result_str = result.decode("utf-8")
            print(result)
            request_str += result
            if result_str.startswith("Content-Length"):
                content_length = int(result_str.split(":")[-1])
            if result == b"\r\n":
                break

        print("<----- Headers End -----")
        print("\n----- Body Start ----->")
        body = self.rfile.read(content_length)
        print(body)
        request_str += body
        print("<----- Body End -----")

        os.makedirs("/app/logs/", exist_ok=True)
        fpath = f"/app/logs/{now}.txt"
        with open(fpath, "wb") as f:
            f.write(request_str + b"\r\n")

        self.wfile.write(b"HTTP/1.1 200 Cool beans\r\n")
        self.wfile.flush()


if __name__ == "__main__":
    port = 8001
    print("Listening on localhost:%s" % port)
    server = HTTPServer(("", port), RequestHandler)
    server.serve_forever()
