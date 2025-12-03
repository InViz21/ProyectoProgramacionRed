"""
S2 - Servicio OTP vía Telegram
Genera códigos OTP y los envía por Telegram usando Bot API.
"""

from flask import Flask, request, jsonify
import random, time, threading, os
import requests

app = Flask(__name__)

# ====== CONFIGURACIÓN ====== #

OTP_TTL = int(os.environ.get("OTP_TTL", "6000000"))

#TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
#TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TELEGRAM_BOT_TOKEN = "8120588514:AAGPSPfiOZ3z92VOGt6xqkVWDz9kL3zzbGU"
TELEGRAM_CHAT_ID = "1692603820"

TELEGRAM_ENABLED = TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID

# OTP almacenados en RAM
otps = {}
lock = threading.Lock()


def generate_code():
    """Genera un OTP de 6 dígitos"""
    return "{:06d}".format(random.randint(0, 999999))


def send_telegram(message):
    """Envía un mensaje por Telegram usando Bot API"""
    if not TELEGRAM_ENABLED:
        print("[S2] Telegram NO configurado")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    try:
        r = requests.post(url, json=payload, verify=False)
        if r.status_code == 200:
            print("[S2] Telegram enviado ✔")
            return True
        else:
            print("[S2] Error Telegram:", r.text)
            return False

    except Exception as e:
        print("[S2] Excepción Telegram:", e)
        return False


@app.route("/generate_otp", methods=["POST"])
def generate_otp():
    data = request.json or {}
    username = data.get("username")

    if not username:
        return jsonify({"error": "username requerido"}), 400

    code = generate_code()
    expiry = time.time() + OTP_TTL

    with lock:
        otps[username] = (code, expiry)

    print(f"[S2] OTP generado para {username}: {code}")

    message = f"🔐 Tu código OTP es: *{code}*\nVálido por {OTP_TTL} segundos."
    sent = send_telegram(message)

    return jsonify({
        "message": "OTP generado",
        "telegram_sent": sent
    })


@app.route("/validate_otp", methods=["POST"])
def validate_otp():
    data = request.json or {}
    username = data.get("username")
    code = data.get("code")

    if not username or not code:
        return jsonify({"error": "faltan campos"}), 400

    with lock:
        entry = otps.get(username)

        if not entry:
            return jsonify({"valid": False, "reason": "no existe OTP"}), 200

        real_code, expiry = entry

        if time.time() > expiry:
            del otps[username]
            return jsonify({"valid": False, "reason": "expirado"}), 200

        if code == real_code:
            del otps[username]
            return jsonify({"valid": True}), 200

        return jsonify({"valid": False, "reason": "incorrecto"}), 200


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(port=5001)

