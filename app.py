import os, re
from flask import Flask, request, jsonify, send_from_directory
import requests

app = Flask(__name__, static_folder="static")

BREVO_API_KEY  = os.environ.get("BREVO_API_KEY", "")
DESTINO_EMAIL  = os.environ.get("DESTINO_EMAIL", "yanisrodriguez13@gmail.com")
REMITENTE_EMAIL = os.environ.get("REMITENTE_EMAIL", "web@janisrodriguez.cl")
REMITENTE_NOMBRE = os.environ.get("REMITENTE_NOMBRE", "Web Janis Rodríguez")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True) or {}
    nombre  = (data.get("nombre") or "").strip()
    email   = (data.get("email") or "").strip()
    mensaje = (data.get("mensaje") or "").strip()

    if not nombre or not email or not mensaje:
        return jsonify({"ok": False, "error": "Campos incompletos"}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"ok": False, "error": "Correo inválido"}), 400
    if not BREVO_API_KEY:
        return jsonify({"ok": False, "error": "Sin API key"}), 500

    payload = {
        "sender": {"name": REMITENTE_NOMBRE, "email": REMITENTE_EMAIL},
        "to": [{"email": DESTINO_EMAIL, "name": "Janis Rodríguez"}],
        "replyTo": {"email": email, "name": nombre},
        "subject": f"Nuevo contacto desde la web — {nombre}",
        "htmlContent": f"""
            <h3 style="color:#B5654E">Nuevo mensaje desde tu web</h3>
            <p><strong>Nombre:</strong> {nombre}</p>
            <p><strong>Correo:</strong> <a href="mailto:{email}">{email}</a></p>
            <p><strong>Mensaje:</strong><br>{mensaje}</p>
            <hr>
            <p style="color:#999;font-size:12px">Enviado desde janisrodriguez.cl</p>
        """
    }

    try:
        r = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers={"api-key": BREVO_API_KEY, "content-type": "application/json"},
            timeout=10
        )
        if r.status_code in (200, 201):
            return jsonify({"ok": True})
        return jsonify({"ok": False, "error": r.text}), 502
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
