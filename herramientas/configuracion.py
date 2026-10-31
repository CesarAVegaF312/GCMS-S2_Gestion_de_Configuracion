#!/usr/bin/env python3
"""Inventario de ítems de configuración y trazabilidad de un repositorio Git.

Material de la Unidad 2 de GCMS (Gestión de Configuración y Mantenimiento de Software).
Tiene dos subcomandos, que alimentan los formatos F-08 y F-12:

  inventario  clasifica los archivos versionados en categorías de ítems de configuración y revisa
              dos señales de integridad: archivos de bloqueo de dependencias y acciones de CI fijadas
              por hash. Escribe inventario_ci.csv.
  traza       recorre los cambios entre dos versiones, extrae las referencias a PR o issues de cada
              commit y, si se indica un registro de cambios, comprueba cuáles de sus referencias se
              pueden seguir dentro de Git. Escribe traza_cambios.csv y traza_registro.csv.

Solo usa la biblioteca estándar de Python 3.8 o posterior y el comando git.

Uso:
  python configuracion.py inventario RUTA_DEL_REPOSITORIO [--ref main]
  python configuracion.py traza RUTA_DEL_REPOSITORIO --desde 3.0.3 --hasta 3.1.0 [--registro CHANGES.rst]
"""

import argparse
import csv
import re
import subprocess
import sys
from collections import Counter
from difflib import SequenceMatcher
from fnmatch import fnmatch
from pathlib import Path

# Reglas por ruta, en orden: gana la primera que coincide. Son un punto de partida; el F-08 se revisa a mano.
CATEGORIAS = [
    ("integración continua", [".github/workflows/*", ".gitlab-ci.yml", "Jenkinsfile", "azure-pipelines.yml",
                              ".circleci/*", "bitbucket-pipelines.yml"]),
    ("gobierno del proyecto", [".github/ISSUE_TEMPLATE/*", ".github/pull_request_template.md", ".github/CODEOWNERS",
                               "CODEOWNERS", "CONTRIBUTING*", "SECURITY*", "LICENSE*", "CHANGES*", "CHANGELOG*",
                               "README*", ".github/dependabot.yml"]),
    ("construcción y dependencias", ["pyproject.toml", "setup.py", "setup.cfg", "requirements*.txt", "requirements/*",
                                     "*.lock", "package.json", "package-lock.json", "pnpm-lock.yaml", "pom.xml",
                                     "build.gradle*", "settings.gradle*", "Dockerfile*", "docker-compose*.y*ml",
                                     "compose*.y*ml", "Makefile", "tox.ini", "go.mod", "go.sum", "Cargo.toml",
                                     "*.csproj", "*.sln", "Gemfile*", "composer.json"]),
    ("entorno y herramientas", [".devcontainer/*", ".editorconfig", ".pre-commit-config.yaml", ".gitignore",
                                ".gitattributes", ".readthedocs.y*ml", ".vscode/*", ".env.example", ".flake8",
                                ".pylintrc", ".eslintrc*", ".prettierrc*", "*.code-workspace"]),
    ("pruebas", ["tests/*", "test/*", "*/tests/*", "*/test/*", "*_test.*", "test_*.py", "*.spec.*", "*.test.*"]),
    ("documentación", ["docs/*", "doc/*", "*.md", "*.rst", "*.txt"]),
    ("ejemplos", ["examples/*", "example/*", "samples/*"]),
    ("código fuente", ["*.py", "*.js", "*.ts", "*.tsx", "*.jsx", "*.java", "*.kt", "*.go", "*.rb", "*.cs", "*.php",
                       "*.c", "*.h", "*.cpp", "*.rs", "*.swift", "*.scala", "*.sql", "*.html", "*.css", "*.vue"]),
    ("configuración de la aplicación", ["*.yml", "*.yaml", "*.json", "*.toml", "*.ini", "*.cfg", "*.properties",
                                        "*.xml", "*.env"]),
]
BLOQUEOS = ["*.lock", "package-lock.json", "pnpm-lock.yaml", "go.sum", "Cargo.lock", "Gemfile.lock", "composer.lock"]
REFERENCIA = re.compile(r"(?<![\w/])#(\d+)\b")
REF_REGISTRO = re.compile(r"(?::(?:pr|issue):`([\d, ]+)`)|(?<![\w/&])#(\d+)\b")


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.exit(f"Falló: git {' '.join(args)}\n{r.stderr.strip()}")
    return r.stdout


CARPETAS = [("integración continua", (".github/workflows/", ".circleci/")), ("ejemplos", ("examples/", "example/", "samples/")),
            ("pruebas", ("tests/", "test/")), ("documentación", ("docs/", "doc/"))]
DE_RAIZ = {"gobierno del proyecto", "construcción y dependencias", "entorno y herramientas"}


def categoria(ruta):
    """Primero manda la carpeta; los archivos de proyecto (README, pyproject.toml...) solo cuentan en la raíz."""
    for cat, prefijos in CARPETAS:
        if ruta.startswith(prefijos) or any(f"/{p}" in ruta for p in prefijos if p in ("tests/", "test/")):
            return cat
    nombre = ruta.rsplit("/", 1)[-1]
    raiz = "/" not in ruta or ruta.startswith((".github/", ".devcontainer/", ".vscode/", "requirements/"))
    for cat, patrones in CATEGORIAS:
        if cat in DE_RAIZ and not raiz:
            continue
        if any(fnmatch(ruta, p) or fnmatch(nombre, p) for p in patrones):
            return cat
    return "otros"


def acciones(repo, ref, ruta):
    """Cuenta las acciones de un flujo de CI fijadas por hash de commit y las fijadas por etiqueta."""
    texto = git(repo, "show", f"{ref}:{ruta}")
    usos = re.findall(r"uses:\s*([^\s#]+)", texto)
    externas = [u for u in usos if "@" in u and not u.startswith("./")]
    por_hash = [u for u in externas if re.fullmatch(r"[0-9a-f]{40}", u.split("@", 1)[1])]
    return len(externas), len(por_hash)


def inventario(a):
    repo = Path(a.repo).resolve()
    archivos = git(repo, "ls-tree", "-r", "--name-only", a.ref).splitlines()
    filas = []
    for ruta in archivos:
        cat = categoria(ruta)
        fila = {"ruta": ruta, "categoria_sugerida": cat, "es_ci": "", "identificador": "", "responsable": "",
                "linea_base": "", "nota": ""}
        if cat == "integración continua" and ruta.endswith((".yml", ".yaml")):
            total, fijas = acciones(repo, a.ref, ruta)
            if total:
                fila["nota"] = f"{fijas} de {total} acciones externas fijadas por hash"
        filas.append(fila)

    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    with open(salida / "inventario_ci.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)

    conteo = Counter(f["categoria_sugerida"] for f in filas)
    print(f"{len(filas)} archivos versionados en {a.ref}\n")
    for cat, n in conteo.most_common():
        print(f"  {cat:<32} {n:>5}")
    bloqueos = [f["ruta"] for f in filas if any(fnmatch(f["ruta"].rsplit("/", 1)[-1], p) for p in BLOQUEOS)]
    print("\nArchivos de bloqueo de dependencias:", ", ".join(bloqueos) if bloqueos else "ninguno")
    for f in filas:
        if f["nota"]:
            print(f"Flujo de CI {f['ruta']}: {f['nota']}")
    print("\nLa categoría es una sugerencia por ruta. Decidir qué es ítem de configuración se hace en el F-08.")


def refs_de(entrada):
    refs = []
    for grupo, suelta in REF_REGISTRO.findall(entrada):
        refs += [x.strip() for x in grupo.split(",") if x.strip()] if grupo else [suelta]
    return refs


def entradas_registro(texto):
    """Separa un registro de cambios en entradas: cada viñeta de primer nivel con sus líneas de continuación."""
    entradas, actual = [], None
    for linea in texto.splitlines():
        if re.match(r"^[-*]\s+\S", linea):
            if actual:
                entradas.append(" ".join(actual.split()))
            actual = linea
        elif actual is not None and linea.startswith(" ") and linea.strip():
            actual += " " + linea.strip()
        elif actual is not None and not linea.strip():
            continue
        else:
            if actual:
                entradas.append(" ".join(actual.split()))
            actual = None
    if actual:
        entradas.append(" ".join(actual.split()))
    return entradas


def nuevas_en_registro(repo, desde, hasta, ruta):
    """Entradas que existen en «hasta» y no en «desde». Una entrada casi igual a una anterior es una edición."""
    antes = entradas_registro(git(repo, "show", f"{desde}:{ruta}"))
    despues = entradas_registro(git(repo, "show", f"{hasta}:{ruta}"))
    exactas = set(antes)
    nuevas = []
    for e in despues:
        if e in exactas:
            continue
        # Casi igual y con las mismas referencias: es una corrección de una entrada antigua.
        if any(refs_de(e) == refs_de(o) and SequenceMatcher(None, e, o).quick_ratio() > 0.9
               and SequenceMatcher(None, e, o).ratio() > 0.9 for o in antes):
            continue
        nuevas.append(e)
    return nuevas


def traza(a):
    repo = Path(a.repo).resolve()
    rango = f"{a.desde}..{a.hasta}"
    sep = "\x1f"
    filas = []
    for linea in git(repo, "log", f"--format=%H{sep}%cs{sep}%P{sep}%s", rango).splitlines():
        h, fecha, padres, asunto = linea.split(sep, 3)
        refs = REFERENCIA.findall(asunto)
        filas.append({"commit": h[:10], "fecha": fecha, "tipo": "integración" if len(padres.split()) > 1 else "cambio",
                      "asunto": asunto, "referencias": " ".join(sorted(set(refs)))})

    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    with open(salida / "traza_cambios.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["commit", "fecha", "tipo", "asunto", "referencias"])
        w.writeheader()
        w.writerows(filas)

    for tipo in ("cambio", "integración"):
        grupo = [f for f in filas if f["tipo"] == tipo]
        con = sum(1 for f in grupo if f["referencias"])
        print(f"  commits de {tipo}: {len(grupo):>4} · con referencia a PR o issue: {con}")

    if a.registro:
        # Solo cuentan las entradas que el registro de cambios ganó en el rango, no las que se corrigieron.
        entradas = nuevas_en_registro(repo, a.desde, a.hasta, a.registro)
        en_git = {r for f in filas for r in f["referencias"].split()}
        traza_reg = []
        for e in entradas:
            refs = refs_de(e)
            encontradas = [r for r in refs if r in en_git]
            traza_reg.append({"entrada": " ".join(e.split())[:160], "referencias": " ".join(refs),
                              "encontradas_en_git": " ".join(encontradas),
                              "estado": "sin referencia" if not refs else ("trazable en Git" if encontradas
                                                                           else "solo fuera de Git")})
        with open(salida / "traza_registro.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["entrada", "referencias", "encontradas_en_git", "estado"])
            w.writeheader()
            w.writerows(traza_reg)
        estados = Counter(t["estado"] for t in traza_reg)
        print(f"\n  entradas nuevas en {a.registro}: {len(traza_reg)}")
        for estado, n in estados.most_common():
            print(f"    {estado:<20} {n}")
        print("\n  «solo fuera de Git» significa que el vínculo existe en la plataforma (GitHub, GitLab, Jira),"
              "\n  no en el historial: se pierde si se cambia de plataforma.")


def main():
    p = argparse.ArgumentParser(description="Inventario de ítems de configuración y trazabilidad de un repositorio Git.")
    sub = p.add_subparsers(dest="comando", required=True)
    i = sub.add_parser("inventario", help="clasifica los archivos versionados en categorías de ítems de configuración")
    i.add_argument("repo")
    i.add_argument("--ref", default="HEAD", help="rama, etiqueta o commit que se inventaría (por defecto HEAD)")
    i.add_argument("--salida", default=".")
    t = sub.add_parser("traza", help="trazabilidad de los cambios entre dos versiones")
    t.add_argument("repo")
    t.add_argument("--desde", required=True, help="versión de partida (etiqueta o commit)")
    t.add_argument("--hasta", required=True, help="versión de llegada (etiqueta o commit)")
    t.add_argument("--registro", default="", help="ruta del registro de cambios, por ejemplo CHANGES.rst")
    t.add_argument("--salida", default=".")
    a = p.parse_args()
    inventario(a) if a.comando == "inventario" else traza(a)


if __name__ == "__main__":
    main()
