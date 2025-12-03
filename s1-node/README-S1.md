S1 - Servidor Node.js
--------------------
1. Variables de entorno necesarias:
   - SMTP_USER: tu correo (ej. tu.email@gmail.com)
   - SMTP_PASS: app password de Gmail (16 chars)
   - JWT_SECRET: secreto para firmar tokens (cámbialo)
   - S2_URL, S3_URL (opcionales)
2. Generar certificados (ver guía principal).
3. Instalar dependencias:
   npm install
4. Ejecutar:
   node index.js
