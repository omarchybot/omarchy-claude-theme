import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import QtQuick

// Capa animada entre el fondo de pantalla y las ventanas (WlrLayer.Bottom).
// No captura ratón ni teclado (mask vacía). Se enciende sola cuando el tema
// activo se llama "Claude..." y se apaga con cualquier otro.
//
// Toda la animación sale de un único reloj a FPS bajos (ver `fps`): la capa
// solo se redibuja cuando avanza el reloj, así el coste en CPU es contenido.
Item {
  id: root

  readonly property string home: Quickshell.env("HOME")
  readonly property string themeNameFile: home + "/.local/state/omarchy/current/theme.name"

  property string themeName: ""
  readonly property bool active: themeName.toLowerCase().indexOf("claude") === 0
  readonly property bool light: themeName.toLowerCase().indexOf("light") !== -1

  // Ajustes rápidos
  readonly property int fps: 20            // fotogramas por segundo de la capa
  readonly property real intensity: light ? 0.55 : 1.0   // 0-1, fuerza de los halos
  readonly property int clawds: 3          // cuántos Clawds pasean

  // Reloj en segundos
  property real t: 0
  readonly property real dt: 1 / fps
  Timer {
    interval: Math.round(1000 / root.fps)
    running: root.active
    repeat: true
    onTriggered: root.t += root.dt
  }

  function wave(period, phase) {  // 0..1 suave, periodo en segundos
    return 0.5 - 0.5 * Math.cos((t / period + phase) * 2 * Math.PI)
  }

  FileView {
    id: themeFile
    path: root.themeNameFile
    watchChanges: true
    onFileChanged: reload()
    onLoaded: root.themeName = String(text() || "").trim()
  }
  Timer { interval: 4000; running: true; repeat: true; onTriggered: themeFile.reload() }

  // Estado por IPC: `omarchy-shell claude-aura status`
  IpcHandler {
    target: "claude-aura"
    function status(): string {
      return "theme=" + root.themeName + " active=" + root.active + " light=" + root.light
        + " fps=" + root.fps + " t=" + root.t.toFixed(1) + "s"
    }
  }

  Variants {
    model: Quickshell.screens

    PanelWindow {
      id: panel
      required property var modelData

      screen: modelData
      visible: root.active
      color: "transparent"
      anchors { top: true; bottom: true; left: true; right: true }
      exclusionMode: ExclusionMode.Ignore
      mask: Region {}

      WlrLayershell.namespace: "claude-aura"
      WlrLayershell.layer: WlrLayer.Bottom
      WlrLayershell.keyboardFocus: WlrKeyboardFocus.None

      readonly property real w: width
      readonly property real h: height

      // ---- halos que derivan lentamente -------------------------------
      component Halo: Image {
        required property real size
        required property real baseOpacity
        required property real periodX
        required property real periodY
        required property real phase
        required property real x0
        required property real y0
        required property real x1
        required property real y1
        readonly property real fx: x0 + (x1 - x0) * root.wave(periodX, phase)
        readonly property real fy: y0 + (y1 - y0) * root.wave(periodY, phase + 0.3)
        source: (root.light || baseOpacity > 0.3) ? Qt.resolvedUrl("assets/glow-terra.png") : Qt.resolvedUrl("assets/glow-cream.png")
        width: size; height: size
        x: fx * panel.w - width / 2
        y: fy * panel.h - height / 2
        scale: 0.92 + 0.2 * root.wave(periodY * 0.6, phase)
        opacity: baseOpacity * root.intensity * (0.85 + 0.15 * root.wave(periodX * 0.5, phase))
        smooth: true
      }

      Halo { size: panel.h * 1.4; baseOpacity: 0.40; periodX: 38; periodY: 27; phase: 0.00; x0: 0.70; y0: 0.50; x1: 0.58; y1: 0.62 }
      Halo { size: panel.h * 0.9; baseOpacity: 0.22; periodX: 51; periodY: 43; phase: 0.37; x0: 0.15; y0: 0.20; x1: 0.30; y1: 0.10 }
      Halo { size: panel.h * 0.7; baseOpacity: 0.16; periodX: 33; periodY: 46; phase: 0.71; x0: 0.85; y0: 0.15; x1: 0.75; y1: 0.30 }

      // ---- asterisco grande que gira y respira ------------------------
      Image {
        source: root.light ? Qt.resolvedUrl("assets/star-terra.png") : Qt.resolvedUrl("assets/star-cream.png")
        width: panel.h * 0.95; height: width
        x: panel.w * 0.68 - width / 2
        y: panel.h * 0.50 - height / 2
        rotation: (root.t / 240) * 360
        scale: 0.97 + 0.07 * root.wave(12, 0)
        opacity: (root.light ? 0.10 : 0.07) * root.intensity
        smooth: true
      }

      // ---- Clawds paseando por el borde inferior ----------------------
      // Sprite base 400x280 (celda de 40 px). Anchos 50/80/100 dan celdas
      // enteras (5/8/10 px) y píxeles nítidos con smooth:false.
      Repeater {
        model: root.clawds
        delegate: Item {
          id: walker
          required property int index
          readonly property real seed: (index * 0.6180339887) % 1
          readonly property int cellW: [80, 50, 100][index % 3]
          readonly property string tint: (index % 3 === 1 && !root.light) ? "cream" : "terra"
          readonly property real speed: 22 + seed * 26      // px/s

          // estado
          property real px: 0.1 * panel.w + seed * 0.8 * panel.w
          property int dir: seed > 0.5 ? 1 : -1
          property string phase: "idle"
          property real phaseEnd: 2 + seed * 4
          property real blinkAt: 3 + seed * 3
          property int glance: 0                              // -1/0/1 mientras está parado
          property real lastT: 0

          function frame() {
            if (phase === "walk") return (Math.floor(root.t * 5) % 2 === 0) ? "walk1" : "walk2"
            if (root.t > blinkAt && root.t < blinkAt + 0.18) return "blink"
            if (glance === 1) return "right"
            if (glance === -1) return "left"
            return "idle"
          }

          Connections {
            target: root
            function onTChanged() {
              var now = root.t
              var d = Math.min(0.25, Math.max(0, now - walker.lastT))
              walker.lastT = now
              if (now > walker.blinkAt + 0.18) walker.blinkAt = now + 2.5 + Math.random() * 4
              if (now > walker.phaseEnd) {
                if (walker.phase === "walk") {
                  walker.phase = "idle"
                  walker.phaseEnd = now + 2 + Math.random() * 5
                  walker.glance = [-1, 0, 1][Math.floor(Math.random() * 3)]
                } else {
                  walker.phase = "walk"
                  walker.phaseEnd = now + 4 + Math.random() * 10
                  if (Math.random() < 0.35) walker.dir = -walker.dir
                  walker.glance = 0
                }
              }
              if (walker.phase === "walk") {
                walker.px += walker.dir * walker.speed * d
                var minX = 8, maxX = panel.w - walker.cellW - 8
                if (walker.px < minX) { walker.px = minX; walker.dir = 1 }
                if (walker.px > maxX) { walker.px = maxX; walker.dir = -1 }
              }
            }
          }

          width: cellW; height: cellW * 0.7
          x: Math.round(px)
          y: Math.round(panel.h - height - 8 - (phase === "walk" ? Math.abs(Math.sin(root.t * 10)) * 3 : 0))
          z: 10

          Image {
            anchors.fill: parent
            source: Qt.resolvedUrl("assets/clawd-" + walker.tint + "-" + walker.frame() + ".png")
            smooth: false
            cache: true
            transform: Scale { origin.x: walker.width / 2; xScale: walker.dir }
          }
        }
      }
    }
  }
}
