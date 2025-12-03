/**
 * S1 - Servidor REST con TLS + Login + Validación OTP
 * Se comunica con S2 para generar OTP y validar OTP.
 * Requiere Telegram en S2.
 */

const express = require("express");
const https = require("https");
const fs = require("fs");
const axios = require("axios");
const bodyParser = require("body-parser");
const jwt = require("jsonwebtoken");
const crypto = require("crypto");

const app = express();
app.use(bodyParser.json());

// ===== CONFIG ===== //

const JWT_SECRET = process.env.JWT_SECRET || "secreto123";

// S2 endpoints
const S2_URL = "http://localhost:5001";

// S3 endpoints
const S3_URL = "http://localhost:5002";

// Certificados TLS
const options = {
  key: fs.readFileSync("certs/server.key"),
  cert: fs.readFileSync("certs/server.crt"),
};

// =====================================================================
// ===========================  LOGIN  =================================
// =====================================================================

app.post("/login", async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password)
    return res.status(400).json({ error: "Faltan campos para login" });

  console.log(`[S1] Login recibido para usuario: ${username}`);

  try {
    const response = await axios.get(`${S3_URL}/users/${username}`);
    const user = response.data;

    if (!user) {
      console.log("[S1] Usuario no encontrado en S3");
      return res.status(404).json({ error: "Usuario no existe" });
    }

    const userHash = user.password_hash;
    const calculatedHash = crypto.createHash("sha256").update(password).digest("hex");

    if (calculatedHash !== userHash) {
      console.log("[S1] Contraseña incorrecta");
      return res.status(401).json({ error: "Credenciales inválidas" });
    }

    console.log("[S1] Credenciales correctas. Solicitando OTP a S2...");

    await axios.post(`${S2_URL}/generate_otp`, { username });

    console.log("[S1] OTP solicitado correctamente");

    return res.json({
      message: "OTP enviado (Telegram). Usa /validate-otp para validar.",
    });

  } catch (err) {
    console.log("[S1] Error durante login:", err.message);
    return res.status(500).json({ error: "Error en servidor" });
  }
});

// =====================================================================
// =======================  VALIDAR OTP  ===============================
// =====================================================================

app.post("/validate-otp", async (req, res) => {
  const { username, otp } = req.body;

  if (!username || !otp)
    return res.status(400).json({ error: "Faltan campos: username y otp" });

  console.log(`[S1] Validando OTP para ${username}: ${otp}`);

  try {
    const valid = await axios.post(`${S2_URL}/validate_otp`, {
      username,
      code: otp,
    });

    if (valid.data.valid === true) {
      console.log("[S1] OTP correcto. Generando token...");

      const token = jwt.sign({ username }, JWT_SECRET, { expiresIn: "1h" });

      return res.json({ token });
    }

    console.log("[S1] OTP incorrecto o expirado");
    return res.json(valid.data);

  } catch (err) {
    console.log("[S1] Error validando OTP:", err.message);
    return res.status(500).json({ error: "Error en servidor" });
  }
});

// =====================================================================
// ===============  MIDDLEWARE JWT (GENÉRICO)  ==========================
// =====================================================================

function verificarToken(req, res, next) {
  const header = req.headers["authorization"];
  if (!header) return res.status(401).json({ error: "Token requerido" });

  const token = header.split(" ")[1];

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded.username;
    next();
  } catch (err) {
    return res.status(401).json({ error: "Token inválido" });
  }
}

// =====================================================================
// ===================  EJEMPLO /profile ===============================
// =====================================================================

app.get("/profile", verificarToken, (req, res) => {
  res.json({
    user: req.user,
    message: "Acceso autorizado",
  });
});

// =====================================================================
// ====================  CRUD ITEMS (PROXY A S3) ========================
// =====================================================================

app.get("/items", verificarToken, async (req, res) => {
  try {
    const r = await axios.get(`${S3_URL}/items`);
    res.json(r.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/items/:id", verificarToken, async (req, res) => {
  try {
    const r = await axios.get(`${S3_URL}/items/${req.params.id}`);
    res.json(r.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/items", verificarToken, async (req, res) => {
  try {
    const r = await axios.post(`${S3_URL}/items`, req.body);
    res.status(201).json(r.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.put("/items/:id", verificarToken, async (req, res) => {
  try {
    const r = await axios.put(`${S3_URL}/items/${req.params.id}`, req.body);
    res.json(r.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.delete("/items/:id", verificarToken, async (req, res) => {
  try {
    const r = await axios.delete(`${S3_URL}/items/${req.params.id}`);
    res.json(r.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// =====================================================================
// ======================  INICIAR SERVIDOR =============================
// =====================================================================

https.createServer(options, app).listen(4430, () => {
  console.log("[S1] Servidor HTTPS escuchando en puerto 4430");
});
