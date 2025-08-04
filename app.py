# app.py

import os
# ————————————————————————————————————————————————————————————————
# Allow multiple OpenMP runtimes so the process doesn’t abort
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# ————————————————————————————————————————————————————————————————

import json
import tornado.ioloop
import tornado.web
from chatbot.hybrid import hybrid_chatbot

# 1) Serve a Tailwind-styled HTML page on GET /
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>📖 Handbook Chat</title>
  <!-- Tailwind CSS via CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 flex items-center justify-center min-h-screen p-4">
  <div class="bg-white w-full max-w-md rounded-lg shadow-lg p-6 space-y-4">
    <h1 class="text-2xl font-semibold text-center">📖 Handbook Chat</h1>
    <textarea id="query"
      class="w-full h-32 border border-gray-300 rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
      placeholder="Type your question here…"></textarea>
    <button id="send"
      class="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 rounded-md transition">
      Ask the Handbook
    </button>
    <div id="answer"
      class="mt-4 min-h-[80px] p-4 bg-gray-50 rounded-md text-gray-800 whitespace-pre-wrap">
      <!-- answer appears here -->
    </div>
  </div>

  <script>
    const sendBtn = document.getElementById("send");
    const queryEl = document.getElementById("query");
    const answerEl = document.getElementById("answer");

    sendBtn.onclick = async () => {
      const q = queryEl.value.trim();
      if (!q) return alert("Please ask something!");
      answerEl.textContent = "🤖 Thinking…";
      try {
        const resp = await fetch("/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: q }),
        });
        const data = await resp.json();
        answerEl.textContent = data.answer ?? data.error;
      } catch (err) {
        answerEl.textContent = "❌ " + err.message;
      }
    };
  </script>
</body>
</html>
        """)

# 2) JSON API on POST /chat
class ChatHandler(tornado.web.RequestHandler):
    async def post(self):
        try:
            payload = json.loads(self.request.body.decode())
            query = payload.get("query", "").strip()
            if not query:
                self.set_status(400)
                return self.write({"error": "must include a non-empty 'query'"})

            # run the blocking model call off the main I/O loop
            answer = await tornado.ioloop.IOLoop.current().run_in_executor(
                None, hybrid_chatbot, query
            )
            self.write({"answer": answer})

        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"error": "invalid JSON"})
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})

# 3) Swallow favicon requests
class FaviconHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_status(204)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),             # friendly UI
        (r"/chat", ChatHandler),         # JSON POST API
        (r"/favicon.ico", FaviconHandler),
    ], debug=True)

# allow both `python app.py` and `python main.py` to run the server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8888))
    app = make_app()
    app.listen(port)
    print(f"[+] Tornado listening on http://localhost:{port}")
    tornado.ioloop.IOLoop.current().start()
