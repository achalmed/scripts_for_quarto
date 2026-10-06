"""
process_runner.py — Ejecución asíncrona de comandos backend (QProcess).

Único punto de ejecución de los scripts. Emite señales con el comando,
cada línea de stdout/stderr, progreso estimado y el resultado final con
tiempo de ejecución. La UI (consola, barra de estado, logs) solo escucha.
"""

from __future__ import annotations

import re

from PySide6.QtCore import QObject, QProcess, QProcessEnvironment, QElapsedTimer, Signal

from app.models.operation import Operacion
from app.services.command import Command
from app.utils.ansi import limpiar

# Patrones para estimar progreso a partir de la salida de los scripts
_RE_TOTAL = re.compile(r"[Ee]ncontrad[oa]s?\s+(\d+)\s+archivo")
_RE_ITEM = re.compile(r"^\s*(?:🔧|✅|✓|📄|→|Procesando)")


class ProcessRunner(QObject):
    """Ejecuta un Command a la vez; los long-running (preview) se pueden detener."""

    iniciado = Signal(Command)                 # al arrancar
    linea_salida = Signal(str, bool)           # (texto, es_stderr)
    progreso = Signal(int, int, str)           # (actual, total, archivo) — total=0 → indeterminado
    terminado = Signal(Operacion)
    estado_ocupado = Signal(bool)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._proc: QProcess | None = None
        self._cmd: Command | None = None
        self._timer = QElapsedTimer()
        self._total = 0
        self._actual = 0

    # ------------------------------------------------------------------ API
    def ocupado(self) -> bool:
        return self._proc is not None and self._proc.state() != QProcess.NotRunning

    def ejecutar(self, cmd: Command) -> bool:
        """Lanza el comando. Devuelve False si ya hay uno en ejecución."""
        if self.ocupado():
            return False

        self._cmd = cmd
        self._total = 0
        self._actual = 0

        proc = QProcess(self)
        if cmd.cwd:
            proc.setWorkingDirectory(cmd.cwd)
        if cmd.entorno:
            env = QProcessEnvironment.systemEnvironment()
            for k, v in cmd.entorno.items():
                env.insert(k, v)
            proc.setProcessEnvironment(env)

        proc.readyReadStandardOutput.connect(self._leer_stdout)
        proc.readyReadStandardError.connect(self._leer_stderr)
        proc.finished.connect(self._al_terminar)
        proc.errorOccurred.connect(self._al_fallar)

        self._proc = proc
        self._timer.start()
        proc.start(cmd.programa, cmd.args)

        if cmd.stdin_data:
            proc.write(cmd.stdin_data.encode())
            proc.closeWriteChannel()

        self.iniciado.emit(cmd)
        self.estado_ocupado.emit(True)
        self.progreso.emit(0, 0, "")
        return True

    def detener(self) -> None:
        """Termina el proceso actual (SIGTERM; kill a los 3 s si no responde)."""
        if self._proc and self.ocupado():
            self._proc.terminate()
            if not self._proc.waitForFinished(3000):
                self._proc.kill()

    # ------------------------------------------------------------- internos
    def _emitir_lineas(self, datos: bytes, es_stderr: bool) -> None:
        for cruda in datos.decode(errors="replace").splitlines():
            linea = limpiar(cruda)
            if not linea.strip():
                continue
            self.linea_salida.emit(linea, es_stderr)
            self._actualizar_progreso(linea)

    def _actualizar_progreso(self, linea: str) -> None:
        m = _RE_TOTAL.search(linea)
        if m:
            self._total = int(m.group(1))
            return
        if _RE_ITEM.match(linea):
            self._actual += 1
            self.progreso.emit(self._actual, self._total, linea.strip()[:80])

    def _leer_stdout(self) -> None:
        if self._proc:
            self._emitir_lineas(bytes(self._proc.readAllStandardOutput()), False)

    def _leer_stderr(self) -> None:
        if self._proc:
            self._emitir_lineas(bytes(self._proc.readAllStandardError()), True)

    def _al_terminar(self, codigo: int, _estado) -> None:
        cmd = self._cmd
        self._proc = None
        self.estado_ocupado.emit(False)
        if cmd:
            self.terminado.emit(Operacion(
                descripcion=cmd.descripcion,
                linea_comando=cmd.linea(),
                codigo_salida=codigo,
                duracion_seg=self._timer.elapsed() / 1000.0,
            ))

    def _al_fallar(self, error) -> None:
        # FailedToStart no dispara finished: informar y liberar
        if self._proc and self._proc.state() == QProcess.NotRunning:
            cmd = self._cmd
            self._proc = None
            self.linea_salida.emit(f"❌ No se pudo iniciar el proceso ({error})", True)
            self.estado_ocupado.emit(False)
            if cmd:
                self.terminado.emit(Operacion(
                    descripcion=cmd.descripcion,
                    linea_comando=cmd.linea(),
                    codigo_salida=-1,
                    duracion_seg=self._timer.elapsed() / 1000.0,
                ))
