# GCMS S2 — Gestión de Configuración

Material de la **Sesión 2** del curso *Gestión de Configuración y Mantenimiento de Software* (GCMS),
Unidad 2: **Gestión de configuración del software**. Maestría en Ingeniería de Software,
Universidad de La Sabana.

Cada grupo diseña la estrategia de gestión de configuración del mismo sistema que diagnosticó en la
Unidad 1. Esa estrategia debe responder a los riesgos de cambios no controlados que encontró allí, y se
implementa en la Unidad 3. Los temas son:

- identificación de **ítems de configuración**;
- **líneas base**;
- **control de cambios**;
- **trazabilidad**.

La actividad de la unidad:

- **Actividad 2. Diseño de estrategia de gestión de configuración** · grupal, de 2 a 3 · **20 %** · 16 horas.
  - **Entregable:** un documento técnico de **8 a 10 páginas** o un **README.md** en el repositorio del
    sistema, que incluya:
    - identificación de ítems de configuración;
    - definición de líneas base;
    - estrategia de control de cambios;
    - definición de trazabilidad;
    - modelo de gestión de configuración con roles y responsabilidades.
  - Se califica con la rúbrica del aula.
  - **Los formatos F-08 a F-14 no se suben:** son el borrador del documento.

---

## Empiecen aquí

**Todo el material se abre desde aquí, sin descargar nada:**
<https://cesaravegaf312.github.io/GCMS-S2_Gestion_de_Configuracion/>

1. **Lean el [enunciado](documentos/1_actividad/GCMS_S2_Enunciado_Actividad_2.pdf):** el encargo, las
   secciones del documento, los criterios de evaluación y el paso a paso.
2. **Lean el [recorrido resuelto con Flask](documentos/2_ejemplo/GCMS_S2_Recorrido_Flask.pdf):** la
   estrategia de gestión de configuración de un proyecto real, leída en su propio repositorio, con una
   matriz de trazabilidad hecha con tres cambios reales.
3. **Corran la herramienta** sobre el repositorio de su sistema (ver abajo).
4. **Llenen los [Instrumentos F-08 a F-14](documentos/3_como_se_hace/GCMS_S2_Instrumentos.pdf)** en
   orden, con el F-06 de la Unidad 1 a mano.

Para trabajar sin conexión, descarguen el repositorio (botón verde **`Code` → `Download ZIP`**),
descomprímanlo y hagan doble clic en `index.html`.

---

## La herramienta de gestión de configuración

`herramientas/configuracion.py` tiene dos subcomandos.

| Subcomando | Qué hace | Archivos | Formato |
|---|---|---|---|
| `inventario` | Clasifica los archivos versionados en categorías de ítems de configuración. Además informa si hay archivos de bloqueo de dependencias y cuántas acciones de CI están fijadas por hash. | `inventario_ci.csv` | F-08 |
| `traza` | Recorre los cambios entre dos versiones y extrae las referencias a PR o issues. Si se le da el registro de cambios, dice cuáles de sus entradas se pueden seguir dentro de Git. | `traza_cambios.csv`, `traza_registro.csv` | F-12 |

Requiere **Python 3.8 o posterior** y **git**. No usa bibliotecas externas.

```bash
python herramientas/configuracion.py inventario <sistema> --ref main --salida salida
python herramientas/configuracion.py traza <sistema> --desde v1.0.0 --hasta v1.1.0 --registro CHANGELOG.md --salida salida
```

La categoría que asigna `inventario` es una sugerencia por ruta: la decisión de qué es ítem de
configuración se toma en el F-08. `traza` reconoce referencias del tipo `#123` en los mensajes de commit y
del tipo `#123`, `` :pr:`123` `` o `` :issue:`123` `` en el registro de cambios. Una entrada que aparece como
«solo fuera de Git» tiene su vínculo en la plataforma (GitHub, GitLab, Jira), no en el historial.

---

## Estructura del repositorio

```text
GCMS-S2_Gestion_de_Configuracion/
├── index.html          ← portada: abre desde aquí todo lo demás
├── presentacion.html   ← las 21 diapositivas de la sesión
├── README.md
├── LICENSE
├── documentos/         ← enunciado, recorrido resuelto, instrumentos y diapositivas (PDF)
├── interactivos/       ← ítems de configuración y trazabilidad de una versión
├── herramientas/       ← configuracion.py
├── ejemplo_flask/      ← los CSV del recorrido resuelto
└── fuentes/            ← fuentes HTML de los PDF y el script para regenerarlos
```

### La clase

| Archivo | Descripción |
|---|---|
| [`presentacion.html`](presentacion.html) | La sesión en el navegador: 21 diapositivas con índice (**I**), glosario de códigos (**G**), cronómetro del taller (**T**), notas del docente (**N**), modo presentador (**P**) y modo de lectura para el teléfono (**L**). |
| [`documentos/4_clase/GCMS_S2_Deck.pdf`](documentos/4_clase/GCMS_S2_Deck.pdf) | Las mismas diapositivas en PDF. |

La sesión va en tres bloques:

1. **Primero, qué significa:** las actividades de la gestión de configuración, ítems de configuración,
   identificación, líneas base, control de cambios, trazabilidad y roles.
2. **Después, cinco ejemplos guiados** con el repositorio de Flask.
3. **Al final, el taller en salas:** cada grupo sale con el inventario de su sistema y su primera línea base.

### Documentos — carpeta `documentos/`

| Archivo | Descripción |
|---|---|
| [`1_actividad/GCMS_S2_Enunciado_Actividad_2.pdf`](documentos/1_actividad/GCMS_S2_Enunciado_Actividad_2.pdf) | El encargo, el entregable, las secciones del documento, los criterios de evaluación y los errores frecuentes. |
| [`2_ejemplo/GCMS_S2_Recorrido_Flask.pdf`](documentos/2_ejemplo/GCMS_S2_Recorrido_Flask.pdf) | Los formatos F-08 a F-13 leídos en el repositorio de Flask. |
| [`3_como_se_hace/GCMS_S2_Instrumentos.pdf`](documentos/3_como_se_hace/GCMS_S2_Instrumentos.pdf) | Los siete formatos en blanco, con instrucciones de llenado. |
| [`4_clase/GCMS_S2_Deck.pdf`](documentos/4_clase/GCMS_S2_Deck.pdf) | Las diapositivas de la sesión. |

### Recursos interactivos — carpeta `interactivos/`

| Archivo | Descripción |
|---|---|
| [`items_configuracion_interactivo.html`](interactivos/items_configuracion_interactivo.html) | Catorce artefactos para decidir si son ítem de configuración y dónde deben vivir, con la justificación de cada caso. No califica. |
| [`trazabilidad_interactivo.html`](interactivos/trazabilidad_interactivo.html) | Las diez entradas del registro de cambios de Flask 3.1.0, seguidas del motivo a la prueba. Muestra qué eslabón se encuentra con Git, cuál exige búsqueda y cuál solo existe en GitHub. |

---

## Material de la unidad

**Obligatorio**

- Berczuk, S., & Appleton, B. (2002). *Software configuration management patterns: Effective teamwork, practical integration*. Addison-Wesley. Capítulos 1 a 3.
- IEEE. (2012). *IEEE Standard for configuration management in systems and software engineering* (IEEE Std 828-2012). Secciones 1 a 4.
- Kim, G., Humble, J., Debois, P., & Willis, J. (2016). *The DevOps handbook*. IT Revolution Press. Capítulo sobre control de versiones.

**Complementario**

- Atlassian. *Git tutorials*. https://www.atlassian.com/git/tutorials
- Git. *Documentation*. https://git-scm.com/docs

---

## Cómo abrir los archivos

Los `.html` son **autocontenidos**: no requieren instalación, servidor ni conexión a internet. Se abren
desde la [portada publicada](https://cesaravegaf312.github.io/GCMS-S2_Gestion_de_Configuracion/) o
descargando el repositorio y haciendo doble clic en `index.html`. Al hacer clic sobre un `.html` dentro de
GitHub se ve el código fuente, no la página.

---

## Para el docente: regenerar los PDF

```bash
node fuentes/imprimir_pdf.js   # los cuatro PDF; requiere Playwright con Chromium
```

---

## Referencias de la sesión

- Berczuk, S., & Appleton, B. (2002). *Software configuration management patterns: Effective teamwork, practical integration*. Addison-Wesley.
- Chacon, S., & Straub, B. (2014). *Pro Git* (2.ª ed.). Apress. https://git-scm.com/book
- Humble, J., & Farley, D. (2010). *Continuous delivery: Reliable software releases through build, test, and deployment automation*. Addison-Wesley.
- IEEE. (2012). *IEEE Standard for configuration management in systems and software engineering* (IEEE Std 828-2012). IEEE.
- Kim, G., Humble, J., Debois, P., & Willis, J. (2016). *The DevOps handbook*. IT Revolution Press.

---

## Licencia

Este material se publica bajo la licencia
**[Creative Commons Atribución-NoComercial-CompartirIgual 4.0 Internacional (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es)**.
Ver [`LICENSE`](LICENSE).

*Los datos de los ejemplos provienen del repositorio público de [Flask](https://github.com/pallets/flask),
proyecto de Pallets con licencia BSD-3-Clause. Este repositorio analiza su historial; no redistribuye su
código.*
