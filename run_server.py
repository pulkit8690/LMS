import eventlet
eventlet.monkey_patch()

import os
from app import create_app
from extensions import init_extensions  # ✅ Import `init_extensions` but NOT `socketio` yet

print("🚀 Creating Flask app...")
app = create_app()

# ✅ Now import `socketio`, AFTER calling `create_app()`
from extensions import socketio

print("🔍 Checking if socketio is initialized...")
if socketio is None:
    raise RuntimeError("❌ socketio was not initialized! Check `init_extensions(app)`.")

print("✅ socketio is initialized, starting server...")

if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        debug=True,
        allow_unsafe_werkzeug=True,
    )
