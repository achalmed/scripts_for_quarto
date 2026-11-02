"""quarto_app/controladores/operaciones.py — la operación actual de cada vista (del catálogo `servicios.operaciones`): lo
que pide (texto, carpeta o archivo; se recuerda por operación), Simular (F5: la simulación de la CLI o el plan de la
ventana) y Aplicar (Ctrl+Intro, tras confirmar en QML con la orden exacta, lo que toca y, al publicar, el sitio y su
dominio) por `gui_comun.tareas.proceso` (una a la vez; la salida íntegra en el panel inferior; el progreso por entrada
en un render; Esc cancela, también el preview); el plan (la última simulación) y el registro (la última aplicación)
por operación en la caché del studio; al terminar, el sitio se relee y su registro y sus problemas quedan en la caché
por sitio. La ventana no renderiza ni publica por su cuenta: toda corrida es la CLI de un backend."""
from __future__ import annotations

import time
from pathlib import Path

from gui_comun.qt import QObject, QSettings, QStandardPaths, Property, Signal, Slot

from quarto_app.services import operaciones as ops
from quarto_app.services import paths, render as svc_render
from quarto_app.services.command import Command

DE_SITIO = {"render", "publicar", "commit", "limpiar", "preview", "verificar", "inspeccionar", "git_status", "listar_entradas", "render_entrada"}
DE_RENDER = {"render", "render_entrada"}
DE_TODOS = {"render_todos", "limpiar_todos", "respaldar", "estructura", "crear_sitio"}


def cache_del_studio() -> Path:
    return Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.CacheLocation) or (Path.home() / ".cache" / "quarto-studio"))


class Operaciones(QObject):
    cambiado = Signal()
    listaCambiada = Signal()
    corridaCambiada = Signal()
    terminada = Signal(str, bool, int)      # id, aplicar, código
    aviso = Signal(str, str)

    def __init__(self, espacio, sitios, flujo, ajustes, consola, tareas, cache: Path | None = None, parent=None):
        super().__init__(parent)
        self.espacio, self.sitios, self.flujo, self.ajustes, self.consola, self.tareas = espacio, sitios, flujo, ajustes, consola, tareas
        self._s = QSettings()
        self._cache = (cache or cache_del_studio()) / "corridas"
        self._por_vista: dict[str, str] = {}
        for v in ops.NOMBRES_VISTAS:
            guardada = str(self._s.value(f"operacion/{v}", "") or "")
            lista = ops.de_vista(v)
            self._por_vista[v] = guardada if ops.operacion(guardada) and ops.operacion(guardada).vista == v else (lista[0].id if lista else "")
        self._usar_excel = str(self._s.value("metadata/usar_excel", "false")).lower() in ("true", "1")
        self._filtro_ruta = str(self._s.value("metadata/filtro_ruta", "") or "")
        self._worker = None
        self._id_en_curso = ""
        self._sitio_en_curso = ""
        self._aplicando = False
        self._lineas: list[str] = []
        self._inicio = 0.0
        self._argv: list[str] = []
        espacio.vistaCambiada.connect(self._vista_cambio)
        sitios.actualCambiado.connect(self.cambiado)
        sitios.entradaCambiada.connect(self.cambiado)
        tareas.cambiada.connect(self.cambiado)
        tareas.linea.connect(self._linea)

    def _vista_cambio(self) -> None:
        self.listaCambiada.emit()
        self.cambiado.emit()
        self.corridaCambiada.emit()

    # ------------------------------------------------------------ la operación actual
    def _op(self) -> ops.Operacion | None:
        return ops.operacion(self._por_vista.get(self.espacio.vista, ""))

    @Property("QVariantList", notify=listaCambiada)
    def lista(self) -> list:
        return [{"id": o.id, "titulo": o.titulo, "descripcion": o.descripcion} for o in ops.de_vista(self.espacio.vista)]

    @Property(int, notify=listaCambiada)
    def indiceActual(self) -> int:
        actual = self._por_vista.get(self.espacio.vista, "")
        return next((i for i, o in enumerate(ops.de_vista(self.espacio.vista)) if o.id == actual), -1)

    @Slot(int)
    def fijarPorIndice(self, i: int) -> None:
        lista = ops.de_vista(self.espacio.vista)
        if 0 <= i < len(lista):
            self.fijar(lista[i].id)

    @Slot(str)
    def fijar(self, id_: str) -> None:
        o = ops.operacion(id_)
        if o is None:
            return
        if self._por_vista.get(o.vista) != id_:
            self._por_vista[o.vista] = id_
            self._s.setValue(f"operacion/{o.vista}", id_)
        if self.espacio.vista != o.vista:
            self.espacio.fijarVista(o.vista)
        else:
            self._vista_cambio()

    @Property(bool, notify=cambiado)
    def hayOperacion(self) -> bool:
        return self._op() is not None

    @Property(str, notify=cambiado)
    def actual(self) -> str:
        o = self._op()
        return o.id if o else ""

    @Property(str, notify=cambiado)
    def titulo(self) -> str:
        o = self._op()
        return o.titulo if o else ""

    @Property(str, notify=cambiado)
    def descripcion(self) -> str:
        o = self._op()
        return o.descripcion if o else ""

    @Property(str, notify=cambiado)
    def verbo(self) -> str:
        o = self._op()
        return o.verbo if o else "Simular"

    @Property(bool, notify=cambiado)
    def escribe(self) -> bool:
        o = self._op()
        return bool(o and o.escribe)

    @Property(bool, notify=cambiado)
    def publica(self) -> bool:
        o = self._op()
        return bool(o and o.publica)

    @Property(bool, notify=cambiado)
    def larga(self) -> bool:
        o = self._op()
        return bool(o and o.larga)

    @Property(bool, notify=cambiado)
    def sobreSitio(self) -> bool:
        o = self._op()
        return bool(o and o.sobre_sitio)

    @Property(bool, notify=cambiado)
    def admiteExcel(self) -> bool:
        o = self._op()
        return bool(o and o.admite_excel)

    @Property(str, notify=cambiado)
    def queToca(self) -> str:
        o = self._op()
        if o is None:
            return ""
        if o.larga:
            return "arranca un servidor local; no escribe nada"
        if not o.escribe:
            return "solo lee (o escribe el Excel y la configuración del repo, no los sitios)"
        partes = []
        if o.publica:
            partes.append("publica: Netlify despliega con el push y no se deshace")
        if o.borra:
            partes.append("borra " + o.borra)
        if o.id in ("render", "render_todos", "render_entrada"):
            partes.append("escribe _site/ (y _freeze/) del sitio")
        if o.vista == "entradas" and o.id not in ("plantilla", "plantilla_incremental", "crear_config"):
            partes.append("reescribe el frontmatter de los .qmd" if not self._usar_excel else "escribe en el Excel")
        if o.vista == "indice":
            partes.append("escribe enlaces en web/_indice/")
        if o.vista == "contenido":
            partes.append("escribe los _contenido_*.qmd del sitio")
        return "; ".join(partes) or "escribe en el sitio"

    # ------------------------------------------------------------------ la entrada
    @Property(str, notify=cambiado)
    def entradaTipo(self) -> str:
        o = self._op()
        return o.entrada if o else ""

    @Property(str, notify=cambiado)
    def entradaEtiqueta(self) -> str:
        o = self._op()
        return o.etiqueta if o else ""

    def _valor_de(self, o: ops.Operacion) -> str:
        guardado = str(self._s.value(f"entrada/{o.id}", "") or "")
        if guardado:
            return guardado
        if o.defecto == "sitio":
            return self.sitios.ruta
        if o.defecto == "entrada":
            return self.sitios.entrada
        return o.defecto

    @Property(str, notify=cambiado)
    def valor(self) -> str:
        o = self._op()
        return self._valor_de(o) if o and o.entrada else ""

    @Slot(str)
    def fijarValor(self, v: str) -> None:
        o = self._op()
        if o and o.entrada and v != self._valor_de(o):
            self._s.setValue(f"entrada/{o.id}", v)
            self.cambiado.emit()

    @Property(bool, notify=cambiado)
    def usarExcel(self) -> bool:
        return self._usar_excel

    @Slot(bool)
    def fijarUsarExcel(self, v: bool) -> None:
        if bool(v) != self._usar_excel:
            self._usar_excel = bool(v)
            self._s.setValue("metadata/usar_excel", "true" if v else "false")
            self.cambiado.emit()

    @Property(str, notify=cambiado)
    def filtroRuta(self) -> str:
        return self._filtro_ruta

    @Slot(str)
    def fijarFiltroRuta(self, v: str) -> None:
        if v != self._filtro_ruta:
            self._filtro_ruta = v
            self._s.setValue("metadata/filtro_ruta", v)
            self.cambiado.emit()

    def contexto(self) -> ops.Contexto:
        o = self._op()
        return ops.Contexto(sitio=self.sitios.nombre, ruta=self.sitios.ruta, estado={} if not self.sitios.hayActual else {
                                "estado": self.sitios.estadoClave, "texto_estado": self.sitios.estadoTexto, "motivo": self.sitios.motivo},
                            sitios=self.sitios.estados(), entrada=self.sitios.entrada, valor=self._valor_de(o) if o and o.entrada else "",
                            excel=self.ajustes.excel, filtro_ruta=self._filtro_ruta, usar_excel=self._usar_excel)

    @Property(str, notify=cambiado)
    def ordenSimular(self) -> str:
        o = self._op()
        if o is None:
            return ""
        if o.simular is None:
            return "(el plan lo calcula la ventana sin correr nada)" if o.plan else ""
        try:
            return ops.texto_orden(o.simular(self.contexto()))
        except Exception as e:      # noqa: BLE001
            return f"(no se puede armar la orden: {e})"

    @Property(str, notify=cambiado)
    def ordenAplicar(self) -> str:
        o = self._op()
        if o is None or not o.escribe:
            return ""
        try:
            return ops.texto_orden(o.aplicar(self.contexto()))
        except Exception as e:      # noqa: BLE001
            return f"(no se puede armar la orden: {e})"

    # ----------------------------------------------------------- disponibilidad
    @Property(bool, notify=cambiado)
    def enCurso(self) -> bool:
        return self._worker is not None and self._worker.isRunning()

    @Property(str, notify=cambiado)
    def motivoNoSimular(self) -> str:
        o = self._op()
        if o is None:
            return "Esta vista no tiene operaciones."
        if self.tareas.activa:
            return "Hay una operación en curso (Esc la cancela)."
        if o.sobre_sitio and not self.sitios.hayActual:
            return "Elige primero un sitio en la tabla."
        if o.sobre_entrada and not self.sitios.hayEntrada:
            return "Elige primero una entrada (pestaña Entradas o vista Entradas)."
        if o.entrada and o.id not in ("commit", "contenido_generar", "crear_sitio") and not self._valor_de(o).strip():
            return f"Falta {o.etiqueta} (pestaña Operación)."
        if o.id == "crear_sitio" and not self._valor_de(o).strip():
            return "Escribe el nombre del sitio nuevo (pestaña Operación)."
        if o.vista == "entradas" and o.id in ("diferencias", "aplicar_excel") and not Path(self.ajustes.excel or "").is_file():
            return "No existe el Excel de metadatos: «Plantilla del Excel» lo genera."
        return ""

    @Property(bool, notify=cambiado)
    def puedeSimular(self) -> bool:
        return self.motivoNoSimular == ""

    @Property(str, notify=cambiado)
    def motivoNoAplicar(self) -> str:
        o = self._op()
        if o is None or not o.escribe:
            return "Esta operación no tiene modo «aplicar»: con F5 se ejecuta."
        motivo = self.motivoNoSimular
        if motivo:
            return motivo
        if o.publica and self.sitios.estadoClave == "problemas":
            return "El sitio tiene problemas (" + self.sitios.motivo + "): la puerta R6 no dejaría publicar."
        return ""

    @Property(bool, notify=cambiado)
    def puedeAplicar(self) -> bool:
        return self.motivoNoAplicar == ""

    @Property(str, notify=cambiado)
    def textoConfirmacion(self) -> str:
        o = self._op()
        if o is None:
            return ""
        lineas = [f"Orden: {self.ordenAplicar}", "", f"Esta operación {self.queToca}."]
        if o.publica and self.sitios.hayActual:
            lineas.append(f"Sitio: {self.sitios.nombre}" + (f" → {self.sitios.dominio}" if self.sitios.dominio else "") + ". Pasa primero por la puerta R6 del hub.")
        if o.id in DE_TODOS:
            lineas.append(f"Sobre los {self.sitios.total} sitios.")
        return "\n".join(lineas)

    # ------------------------------------------------------------------ correr
    @Slot(result=bool)
    def simular(self) -> bool:
        """F5: la simulación de la CLI, el plan de la ventana, la ejecución de lo que solo lee o el arranque del preview."""
        o = self._op()
        if o is None or not self.puedeSimular:
            self.aviso.emit(self.motivoNoSimular, "aviso")
            return False
        if o.simular is None:
            if o.plan is None:
                return False
            texto = o.plan(self.contexto())
            self._escribir(o.id, False, f"# {time.strftime('%Y-%m-%d %H:%M:%S')} · plan · {o.titulo}\n\n{texto}\n")
            for linea in texto.splitlines():
                self.consola.escribir(linea, "info")
            self.aviso.emit(f"Plan de «{o.titulo}» en la pestaña Plan: revísalo y aplica con Ctrl+Intro.", "informacion")
            self.corridaCambiada.emit()
            return True
        return self._lanzar(o, o.simular(self.contexto()), aplicar=False)

    @Slot(result=bool)
    def aplicar(self) -> bool:
        """Ctrl+Intro, tras la confirmación en QML."""
        o = self._op()
        if o is None or not self.puedeAplicar:
            self.aviso.emit(self.motivoNoAplicar, "aviso")
            return False
        return self._lanzar(o, o.aplicar(self.contexto()), aplicar=True)

    def _lanzar(self, o: ops.Operacion, cmd: Command, aplicar: bool) -> bool:
        argv = [cmd.programa, *cmd.args]
        if argv[0] in ("python3", "python"):
            argv[0] = paths.interprete()
        programa = Path(argv[1]) if len(argv) > 1 else None
        if programa is not None and programa.suffix in (".sh", ".py") and not programa.is_file():
            self.aviso.emit(f"No existe {programa}.", "error")
            return False
        self._argv, self._id_en_curso, self._aplicando, self._lineas, self._inicio = argv, o.id, aplicar, [], time.monotonic()
        self._sitio_en_curso = self.sitios.nombre if o.id in DE_SITIO else ""
        verbo = "Arrancando" if o.larga else ("Aplicando" if aplicar else ("Simulando" if o.escribe else "Ejecutando"))
        nombre = f"{verbo}: {o.titulo}" + (f" · {self._sitio_en_curso}" if self._sitio_en_curso else "")
        self._worker = self.tareas.proceso(nombre, argv, cwd=cmd.cwd, entrada=cmd.stdin_data, entorno=cmd.entorno or None,
                                           progreso_de=svc_render.progreso_de if o.id in DE_RENDER or o.id == "render_todos" else None,
                                           al_terminar=lambda codigo, i=o.id, a=aplicar, s=self._sitio_en_curso: self._fin(codigo, i, a, s))
        self.cambiado.emit()
        self.corridaCambiada.emit()
        return True

    def _linea(self, texto: str, nivel: str) -> None:
        if self._worker is not None:
            self._lineas.append(texto)

    def _fin(self, codigo: int, id_: str, aplicar: bool, sitio: str) -> None:
        self._worker = None
        segundos = time.monotonic() - self._inicio
        o = ops.operacion(id_)
        titulo = o.titulo if o else id_
        cuerpo = "\n".join(self._lineas[1:] if self._lineas and self._lineas[0].startswith("$ ") else self._lineas) + "\n"
        cabecera = (f"# {time.strftime('%Y-%m-%d %H:%M:%S')} · {'aplicado' if aplicar else 'simulación'} · {titulo}" + (f" · {sitio}" if sitio else "") + "\n"
                    f"# {' '.join(self._argv)}\n# código de salida {codigo} · {segundos:.1f} s\n\n")
        self._escribir(id_, aplicar, cabecera + cuerpo)
        if sitio and (aplicar or id_ in ("verificar", "inspeccionar", "git_status", "publicar", "commit")):
            self.sitios.guardarCorrida(sitio, cabecera + cuerpo, es_render=aplicar and id_ in DE_RENDER)
        if o and o.larga:
            self.aviso.emit(f"{titulo} detenido ({segundos:.0f} s).", "informacion")
        elif codigo == 0:
            que = "aplicada" if aplicar else ("simulada" if o and o.escribe else "ejecutada")
            self.aviso.emit(f"{titulo}{' · ' + sitio if sitio else ''} {que} en {segundos:.1f} s" + (": revisa el plan antes de aplicar (Ctrl+Intro)." if not aplicar and o and o.escribe else "."),
                            "positivo" if aplicar else "informacion")
        else:
            self.aviso.emit(f"{titulo}{' · ' + sitio if sitio else ''} terminó con código {codigo} ({segundos:.1f} s): revisa la salida (F4).", "error")
        if aplicar or id_ in ("render_todos", "limpiar_todos", "respaldar", "crear_sitio"):
            if sitio and id_ in DE_SITIO:
                self.sitios.refrescar(sitio)
            elif id_ in DE_TODOS or id_ == "render_entrada":
                self.sitios.recargar()
            if o and o.vista != "sitios":
                self.flujo.recargar(o.vista)
        elif sitio and id_ in ("publicar", "commit"):
            self.sitios.refrescar(sitio)
        self.cambiado.emit()
        self.corridaCambiada.emit()
        self.terminada.emit(id_, aplicar, codigo)

    @Slot()
    def cancelar(self) -> None:
        if self.enCurso:
            self.tareas.cancelar()

    # ------------------------------------------------------------- plan y registro
    def _archivo(self, id_: str, aplicar: bool) -> Path:
        return self._cache / f"{id_}.{'registro' if aplicar else 'plan'}.txt"

    def _escribir(self, id_: str, aplicar: bool, texto: str) -> None:
        try:
            self._cache.mkdir(parents=True, exist_ok=True)
            self._archivo(id_, aplicar).write_text(texto, encoding="utf-8")
        except OSError as e:
            self.consola.registrar("warn", f"No se pudo guardar el {'registro' if aplicar else 'plan'}: {e}")

    def _leer(self, aplicar: bool) -> str:
        o = self._op()
        if o is None:
            return ""
        try:
            return self._archivo(o.id, aplicar).read_text(encoding="utf-8")
        except OSError:
            return ""

    @Property(str, notify=corridaCambiada)
    def plan(self) -> str:
        return self._leer(False)

    @Property(str, notify=corridaCambiada)
    def registro(self) -> str:
        return self._leer(True)

    def entradas_paleta(self, _texto: str) -> list[dict]:
        grupos = dict((n, t) for n, t, _i in ops.VISTAS)
        return [{"nombre": f"op.ir.{o.id}", "texto": f"Operación: {o.titulo}", "grupo": grupos.get(o.vista, ""), "icono": "system-run",
                 "ejecutar": lambda i=o.id: self.fijar(i)} for o in ops.OPERACIONES]
