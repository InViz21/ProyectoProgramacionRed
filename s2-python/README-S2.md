S2 - Servicio OTP
-----------------
1. Crear entorno virtual:
   python3 -m venv venv
   source venv/bin/activate
2. Instalar:
   pip install -r requirements.txt
3. Variables opcionales:
   - SMTP_USER, SMTP_PASS (si quieres que S2 envíe el correo)
   - OTP_TTL (segundos)
4. Ejecutar:
   python app.py
