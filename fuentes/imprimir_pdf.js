// Imprime en PDF los documentos de fuentes/ y la presentación de la sesión.
// Uso, desde la raíz del repositorio:  node fuentes/imprimir_pdf.js
// Requiere Playwright con Chromium (npm install playwright && npx playwright install chromium).
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

const RAIZ = path.resolve(__dirname, "..");
const DOCUMENTOS = [
  ["fuentes/GCMS_S2_Enunciado_Actividad_2.html", "documentos/1_actividad/GCMS_S2_Enunciado_Actividad_2.pdf"],
  ["fuentes/GCMS_S2_Recorrido_Flask.html", "documentos/2_ejemplo/GCMS_S2_Recorrido_Flask.pdf"],
  ["fuentes/GCMS_S2_Instrumentos.html", "documentos/3_como_se_hace/GCMS_S2_Instrumentos.pdf"],
];
const DECK = "documentos/4_clase/GCMS_S2_Deck.pdf";

(async () => {
  const navegador = await chromium.launch({ args: ["--no-sandbox"] });

  for (const [fuente, destino] of DOCUMENTOS) {
    const pagina = await navegador.newPage();
    await pagina.goto("file://" + path.join(RAIZ, fuente), { waitUntil: "load" });
    fs.mkdirSync(path.dirname(path.join(RAIZ, destino)), { recursive: true });
    await pagina.pdf({ path: path.join(RAIZ, destino), format: "Letter", printBackground: true, preferCSSPageSize: true });
    await pagina.close();
    console.log("  " + destino);
  }

  if (!fs.existsSync(path.join(RAIZ, "presentacion.html"))) { await navegador.close(); return; }

  // La presentación se fotografía diapositiva por diapositiva a 1280×720 y se arma un PDF apaisado.
  const deck = await navegador.newPage({ viewport: { width: 1280, height: 754 } });
  await deck.goto("file://" + path.join(RAIZ, "presentacion.html"), { waitUntil: "load" });
  await deck.addStyleTag({ content: "#estado,#progreso{display:none!important} .slide [data-anim]{animation:none!important;opacity:1!important;transform:none!important}" });
  const total = await deck.evaluate(() => document.querySelectorAll(".slide").length);
  const imagenes = [];
  for (let n = 0; n < total; n++) {
    if (n) await deck.keyboard.press("ArrowRight");
    await deck.waitForTimeout(300);
    const lienzo = await deck.$("#lienzo");
    imagenes.push((await lienzo.screenshot({ animations: "disabled" })).toString("base64"));
  }
  const html = `<html><head><style>@page{size:1280px 720px;margin:0}body{margin:0}
    img{display:block;width:1280px;height:720px;break-after:page}</style></head><body>
    ${imagenes.map(b => `<img src="data:image/png;base64,${b}"/>`).join("")}</body></html>`;
  const hoja = await navegador.newPage();
  await hoja.setContent(html, { waitUntil: "load" });
  fs.mkdirSync(path.dirname(path.join(RAIZ, DECK)), { recursive: true });
  await hoja.pdf({ path: path.join(RAIZ, DECK), width: "1280px", height: "720px", printBackground: true });
  console.log("  " + DECK + " (" + total + " diapositivas)");

  await navegador.close();
})().catch(e => { console.error(e); process.exit(1); });
