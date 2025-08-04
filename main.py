# main.py
from app import make_app
import tornado.ioloop

if __name__ == "__main__":
    app = make_app()
    port = 8888
    app.listen(port)
    print(f"[+] Tornado listening on http://localhost:{port}")
    tornado.ioloop.IOLoop.current().start()
