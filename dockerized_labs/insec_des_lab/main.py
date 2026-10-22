from flask import Flask, render_template, request, make_response
import json
import base64
from dataclasses import dataclass

app = Flask(__name__)


@dataclass
class User:
    username: str
    is_admin: bool = False

    def __reduce__(self):
        # Intentionally vulnerable __reduce__ method to match PyGoat
        return (User, (self.username, self.is_admin))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/serialize", methods=["POST"])
def serialize_data():
    username = request.form.get("username", "guest")
    # Create regular user with admin=False
    user = User(username=username, is_admin=False)
    # Serialize as JSON (safe for untrusted data), then base64-encode for transport
    payload = {"username": user.username, "is_admin": user.is_admin}
    serialized = base64.b64encode(json.dumps(payload).encode("utf-8")).decode()
    return render_template("result.html", serialized=serialized)


@app.route("/deserialize", methods=["POST"])
def deserialize_data():
    try:
        serialized_data = request.form.get("serialized_data", "")
        decoded_data = base64.b64decode(serialized_data)
        data = json.loads(decoded_data.decode("utf-8"))

        if isinstance(data, dict) and isinstance(data.get("username"), str):
            # Never trust client-provided privilege flags
            user = User(username=data["username"], is_admin=False)
            if user.is_admin:
                message = f"Welcome Admin {user.username}! Here's the secret admin content: ADMIN_KEY_123"
            else:
                message = (
                    f"Welcome {user.username}. Only admins can see the secret content."
                )
        else:
            message = "Invalid user data"

        return render_template("result.html", message=message)
    except Exception as e:
        return render_template("result.html", message=f"Error: {str(e)}")

@app.route("/health")
def health_check():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)