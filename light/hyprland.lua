-- Tema Claude: bordes terracota/crema que giran, esquinas redondeadas, sombras
-- cálidas, blur en menús y animaciones con rebote.

local terra, cream, ember = "rgba(c96442ee)", "rgba(3d3929ee)", "rgba(d97757ee)"

local active_border_color = { colors = { terra, ember, cream, ember, terra }, angle = 45 }
local inactive_border_color = "rgba(d8d3c6aa)"

hl.config({
  general = {
    gaps_in = 5,
    gaps_out = 12,
    border_size = 2,
    col = {
      active_border = active_border_color,
      inactive_border = inactive_border_color,
    },
  },

  group = {
    col = {
      border_active = active_border_color,
      border_inactive = inactive_border_color,
    },
  },

  decoration = {
    rounding = 10,
    rounding_power = 3,
    active_opacity = 1.0,
    inactive_opacity = 0.96,
    dim_inactive = true,
    dim_strength = 0.08,
    shadow = {
      enabled = true,
      range = 22,
      render_power = 3,
      color = "rgba(c9644255)",
      color_inactive = "rgba(3d392933)",
    },
    blur = {
      enabled = true,
      size = 6,
      passes = 3,
      noise = 0.02,
      contrast = 1.0,
      brightness = 1.05,
      vibrancy = 0.2,
      popups = true,
      special = true,
    },
  },

  animations = {
    enabled = true,
  },
})

-- Curvas con un poco de rebote (Material "expressive")
hl.curve("claudeSpring", { type = "bezier", points = { { 0.34, 1.35 }, { 0.64, 1.0 } } })
hl.curve("claudeOut", { type = "bezier", points = { { 0.05, 0.9 }, { 0.1, 1.0 } } })
hl.curve("claudeIn", { type = "bezier", points = { { 0.4, 0.0 }, { 0.8, 0.2 } } })
hl.curve("claudeLinear", { type = "bezier", points = { { 0, 0 }, { 1, 1 } } })

hl.animation({ leaf = "windows", enabled = true, speed = 5, bezier = "claudeSpring" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 5, bezier = "claudeSpring", style = "popin 75%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 4, bezier = "claudeIn", style = "popin 85%" })
hl.animation({ leaf = "windowsMove", enabled = true, speed = 5, bezier = "claudeSpring", style = "slide" })
hl.animation({ leaf = "fadeIn", enabled = true, speed = 4, bezier = "claudeOut" })
hl.animation({ leaf = "fadeOut", enabled = true, speed = 3, bezier = "claudeIn" })
hl.animation({ leaf = "fade", enabled = true, speed = 4, bezier = "claudeOut" })
hl.animation({ leaf = "fadeDim", enabled = true, speed = 6, bezier = "claudeOut" })
hl.animation({ leaf = "border", enabled = true, speed = 8, bezier = "claudeOut" })
-- El degradado del borde da vueltas sin parar: la "animación" visible en todo momento.
hl.animation({ leaf = "borderangle", enabled = true, speed = 60, bezier = "claudeLinear", style = "loop" })
hl.animation({ leaf = "layers", enabled = true, speed = 5, bezier = "claudeSpring" })
hl.animation({ leaf = "layersIn", enabled = true, speed = 5, bezier = "claudeSpring", style = "popin 85%" })
hl.animation({ leaf = "layersOut", enabled = true, speed = 4, bezier = "claudeIn", style = "popin 92%" })
hl.animation({ leaf = "fadeLayersIn", enabled = true, speed = 3, bezier = "claudeOut" })
hl.animation({ leaf = "fadeLayersOut", enabled = true, speed = 3, bezier = "claudeIn" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 5, bezier = "claudeSpring", style = "slidefade 12%" })
hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 5, bezier = "claudeSpring", style = "slidefadevert 15%" })

-- Terminales un pelín translúcidos para que se vea el brillo del fondo detrás.
o.window({ tag = "terminal" }, { opacity = "0.97 0.94" })
