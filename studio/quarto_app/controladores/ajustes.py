"""quarto_app/controladores/ajustes.py — «Configurar Quarto Studio…»: el puerto del preview, el destino de publicación
(vacío: `git push`, Netlify), el Excel de metadatos y la terminal, sobre las claves de QSettings de 1.x
(`quarto_app.settings`)."""
from __future__ import annotations

from gui_comun.qt import QObject, Property, Signal, Slot

from quarto_app.services import paths
from quarto_app.settings import settings


class Ajustes(QObject):
    cambiado = Signal()
    guardado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._s = settings()

    def _get(self, clave: str, defecto: str = "") -> str:
        return self._s.get(clave) or defecto

    def _set(self, clave: str, v) -> None:
        if str(v) != str(self._s.get(clave)):
            self._s.set(clave, v)
            self.cambiado.emit()

    puerto = Property(int, lambda self: self._s.get_int("blogs/preview_port") or 4200, lambda self, v: self._set("blogs/preview_port", int(v) if int(v) > 0 else 4200), notify=cambiado)
    destino = Property(str, lambda self: self._get("blogs/destino_publicacion"), lambda self, v: self._set("blogs/destino_publicacion", (v or "").strip()), notify=cambiado)
    excel = Property(str, lambda self: self._get("metadata/excel_file") or str(paths.excel_por_defecto()), lambda self, v: self._set("metadata/excel_file", (v or "").strip()), notify=cambiado)
    terminal = Property(str, lambda self: self._get("sistema/terminal", "konsole"), lambda self, v: self._set("sistema/terminal", (v or "").strip() or "konsole"), notify=cambiado)

    @Property(str, constant=True)
    def interprete(self) -> str:
        return paths.interprete()

    @Property(bool, constant=True)
    def hayVenv(self) -> bool:
        return (paths.venv_dir() / "bin" / "python").is_file()

    @Property(str, constant=True)
    def ordenVenv(self) -> str:
        return paths.orden_crear_venv()

    @Slot()
    def guardar(self) -> None:
        self.cambiado.emit()
        self.guardado.emit()
