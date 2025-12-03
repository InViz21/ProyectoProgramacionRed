S3 - Servidor de Recursos
-------------------------
1. Inicializar DB (una sola vez):
   python3 init_db.py

2. Crear entorno y dependencias:
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

3. Ejecutar:
   python app.py

4. (Opcional) Crear usuario de prueba:
   curl -X POST http://localhost:5002/users -H "Content-Type: application/json" \
     -d '{"username":"prueba","password":"1234","email":"tu.email@dominio.com"}'
