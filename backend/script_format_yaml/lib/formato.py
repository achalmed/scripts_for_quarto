"""lib/formato.py — reparación del bloque YAML de un .qmd (idempotente).

Formato correcto:
---
yaml
---
<una línea en blanco>
## Contenido
"""
import re
from pathlib import Path

import config


def reparar(filepath: Path, dry_run: bool = False):
    """True = corregido (o se corregiría), False = ya estaba bien, None = error o sin bloque YAML."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"❌ Error leyendo {filepath}: {e}")
        return None
    # «draft: false---» → salto de línea antes del cierre
    normalizado = re.sub(r"([^\n])---\s*\n", r"\1\n---\n", content)
    m = re.match(r"^---\s*\n(.*?)\n---\s*(.*)$", normalizado, re.DOTALL)
    if not m:
        print(f"⚠️  No se encontró bloque YAML válido en: {filepath}")
        return None
    yaml_content, after = m.group(1), m.group(2).lstrip("\n\r\t ")
    correcto = f"---\n{yaml_content}\n---\n" + ("\n" * config.LINEAS_EN_BLANCO_TRAS_YAML + after if after else "")
    if content == correcto:
        print(f"✓ OK (formato correcto): {filepath}")
        return False
    print(f"🔧 Corrigiendo formato YAML en: {filepath}")
    if after:
        print(f"   Contenido después de ---: '{after[:config.PREVIEW].replace(chr(10), chr(92) + 'n')}...'")
    if dry_run:
        print("   🔍 [DRY RUN] Se corregiría este archivo")
    else:
        filepath.write_text(correcto, encoding="utf-8")
        print("   ✅ Archivo corregido")
    return True


def archivos(directory: Path, recursive: bool):
    return sorted(directory.glob(("**/" if recursive else "") + config.EXTENSION))
