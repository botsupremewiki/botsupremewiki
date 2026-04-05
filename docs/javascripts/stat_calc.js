/* ============================================================
   Calculateur de Stats — Bot Suprême Wiki
   ============================================================ */
(function () {

  const BASE_STATS = {
    "Guerrier":         { hp: 550,  p_atk: 52,  m_atk: 0,   p_pen: 8,  m_pen: 0,  p_def: 32, m_def: 6,  speed: 80,  crit_chance: 5.0,  crit_damage: 50.0 },
    "Assassin":         { hp: 500,  p_atk: 50,  m_atk: 0,   p_pen: 10, m_pen: 0,  p_def: 4,  m_def: 3,  speed: 105, crit_chance: 18.0, crit_damage: 75.0 },
    "Mage":             { hp: 420,  p_atk: 0,   m_atk: 42,  p_pen: 0,  m_pen: 8,  p_def: 3,  m_def: 10, speed: 92,  crit_chance: 12.0, crit_damage: 75.0 },
    "Tireur":           { hp: 440,  p_atk: 44,  m_atk: 0,   p_pen: 8,  m_pen: 0,  p_def: 4,  m_def: 4,  speed: 105, crit_chance: 16.0, crit_damage: 75.0 },
    "Support":          { hp: 650,  p_atk: 48,  m_atk: 48,  p_pen: 6,  m_pen: 6,  p_def: 25, m_def: 25, speed: 80,  crit_chance: 5.0,  crit_damage: 40.0 },
    "Vampire":          { hp: 580,  p_atk: 60,  m_atk: 0,   p_pen: 9,  m_pen: 0,  p_def: 12, m_def: 7,  speed: 90,  crit_chance: 15.0, crit_damage: 75.0 },
    "Gardien du Temps": { hp: 480,  p_atk: 35,  m_atk: 35,  p_pen: 6,  m_pen: 6,  p_def: 18, m_def: 18, speed: 95,  crit_chance: 8.0,  crit_damage: 55.0 },
    "Ombre Venin":      { hp: 460,  p_atk: 32,  m_atk: 32,  p_pen: 5,  m_pen: 5,  p_def: 5,  m_def: 5,  speed: 115, crit_chance: 17.0, crit_damage: 70.0 },
    "Pyromancien":      { hp: 500,  p_atk: 0,   m_atk: 58,  p_pen: 0,  m_pen: 9,  p_def: 2,  m_def: 10, speed: 85,  crit_chance: 13.0, crit_damage: 75.0 },
    "Paladin":          { hp: 560,  p_atk: 42,  m_atk: 0,   p_pen: 8,  m_pen: 0,  p_def: 35, m_def: 22, speed: 72,  crit_chance: 5.0,  crit_damage: 50.0 },
  };

  const LEVEL_GROWTH = {
    "Guerrier":         { hp: 45.44, p_atk: 2.400, m_atk: 0,     p_pen: 0,     m_pen: 0,     p_def: 0.822, m_def: 0.194, speed: 0.230, crit_chance: 0, crit_damage: 0 },
    "Assassin":         { hp: 36.54, p_atk: 2.643, m_atk: 0,     p_pen: 0.549, m_pen: 0,     p_def: 0,     m_def: 0,     speed: 0.365, crit_chance: 0, crit_damage: 0 },
    "Mage":             { hp: 39.64, p_atk: 0,     m_atk: 2.814, p_pen: 0,     m_pen: 0.553, p_def: 0,     m_def: 0,     speed: 0.405, crit_chance: 0, crit_damage: 0 },
    "Tireur":           { hp: 37.60, p_atk: 2.668, m_atk: 0,     p_pen: 0.555, m_pen: 0,     p_def: 0,     m_def: 0,     speed: 0.360, crit_chance: 0, crit_damage: 0 },
    "Support":          { hp: 72.42, p_atk: 1.283, m_atk: 1.283, p_pen: 0,     m_pen: 0,     p_def: 0.630, m_def: 0.630, speed: 0.195, crit_chance: 0, crit_damage: 0 },
    "Vampire":          { hp: 50.00, p_atk: 2.638, m_atk: 0,     p_pen: 0.528, m_pen: 0,     p_def: 0.268, m_def: 0.193, speed: 0.245, crit_chance: 0, crit_damage: 0 },
    "Gardien du Temps": { hp: 41.56, p_atk: 1.400, m_atk: 1.400, p_pen: 0.304, m_pen: 0.304, p_def: 0.362, m_def: 0.362, speed: 0.240, crit_chance: 0, crit_damage: 0 },
    "Ombre Venin":      { hp: 45.65, p_atk: 1.540, m_atk: 1.540, p_pen: 0.300, m_pen: 0.300, p_def: 0,     m_def: 0,     speed: 0.345, crit_chance: 0, crit_damage: 0 },
    "Pyromancien":      { hp: 43.64, p_atk: 0,     m_atk: 3.100, p_pen: 0,     m_pen: 0.610, p_def: 0,     m_def: 0,     speed: 0.395, crit_chance: 0, crit_damage: 0 },
    "Paladin":          { hp: 71.51, p_atk: 2.361, m_atk: 0,     p_pen: 0,     m_pen: 0,     p_def: 0.916, m_def: 0.428, speed: 0.193, crit_chance: 0, crit_damage: 0 },
  };

  const CLASS_EMOJI = {
    "Guerrier": "⚔️", "Assassin": "🗡️", "Mage": "🔮", "Tireur": "🏹", "Support": "🛡️",
    "Vampire": "🧛", "Gardien du Temps": "⏳", "Ombre Venin": "☠️", "Pyromancien": "🔥", "Paladin": "✝️",
  };

  const STAT_ROWS = [
    { key: "hp",          icon: "❤️",  label: "PV (max)",            fmt: "int",     hp: true },
    { key: "p_atk",       icon: "⚔️",  label: "ATK Physique",        fmt: "int"  },
    { key: "m_atk",       icon: "✨",  label: "ATK Magique",          fmt: "int"  },
    { key: "p_pen",       icon: "🗡️",  label: "Pén. Physique",       fmt: "int"  },
    { key: "m_pen",       icon: "💫",  label: "Pén. Magique",         fmt: "int"  },
    { key: "p_def",       icon: "🛡️",  label: "Déf. Physique",       fmt: "int"  },
    { key: "m_def",       icon: "🔮",  label: "Déf. Magique",         fmt: "int"  },
    { key: "speed",       icon: "💨",  label: "Vitesse",              fmt: "int"  },
    { key: "crit_chance", icon: "🎯",  label: "Chance de Critique",   fmt: "pct"  },
    { key: "crit_damage", icon: "💥",  label: "Dégâts de Critique",   fmt: "cdmg" },
  ];

  function clamp(val, min, max) {
    return Math.min(max, Math.max(min, val));
  }

  function computeStats(cls, level, prestige) {
    const base   = BASE_STATS[cls];
    const growth = LEVEL_GROWTH[cls];
    const mult   = 1 + prestige * 0.001;
    const out    = {};
    for (const key of Object.keys(base)) {
      out[key] = (base[key] + growth[key] * (level - 1)) * mult;
    }
    return out;
  }

  function fmt(key, val) {
    if (key === "crit_chance") return val.toFixed(1) + "%";
    if (key === "crit_damage") return (100 + val).toFixed(1) + "%";
    return Math.round(val).toLocaleString("fr-FR");
  }

  function render() {
    const clsSel  = document.getElementById("sc-class");
    const lvlNum  = document.getElementById("sc-level-num");
    const preSel  = document.getElementById("sc-prestige");
    if (!clsSel || !lvlNum || !preSel) return;

    const cls      = clsSel.value;
    const level    = clamp(parseInt(lvlNum.value) || 1, 1, 1000);
    const prestige = clamp(parseInt(preSel.value) || 0, 0, 9999);

    lvlNum.value = level;

    const stats    = computeStats(cls, level, prestige);
    const rawStats = prestige > 0 ? computeStats(cls, level, 0) : null;

    // prestige badge
    const badge = document.getElementById("sc-prestige-badge");
    if (badge) {
      if (prestige > 0) {
        const bonus = (prestige * 0.1).toFixed(1);
        badge.textContent = `✨ Prestige ${prestige} — ×${(1 + prestige * 0.001).toFixed(3)} sur toutes les stats (+${bonus}%)`;
        badge.style.display = "";
      } else {
        badge.style.display = "none";
      }
    }

    // header 3rd column
    const thBase = document.getElementById("sc-th-base");
    if (thBase) thBase.style.display = rawStats ? "" : "none";

    // class header
    const clsHeader = document.getElementById("sc-class-header");
    if (clsHeader) {
      clsHeader.textContent = `${CLASS_EMOJI[cls] || ""} ${cls}  —  Niveau ${level}`;
    }

    // tbody
    const tbody = document.getElementById("sc-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    for (const row of STAT_ROWS) {
      const b = BASE_STATS[cls];
      const g = LEVEL_GROWTH[cls];
      // skip stats absent for this class (0 base AND 0 growth)
      if (b[row.key] === 0 && g[row.key] === 0) continue;

      const tr  = document.createElement("tr");
      if (row.hp) tr.className = "sc-row-hp";

      // stat name cell
      const tdName = document.createElement("td");
      tdName.innerHTML = `<span class="sc-stat-icon">${row.icon}</span> ${row.label}`;
      tr.appendChild(tdName);

      // final value
      const tdVal = document.createElement("td");
      tdVal.innerHTML = `<strong>${fmt(row.key, stats[row.key])}</strong>`;
      tr.appendChild(tdVal);

      // raw (without prestige)
      if (rawStats) {
        const tdRaw = document.createElement("td");
        tdRaw.className = "sc-col-base";
        tdRaw.textContent = fmt(row.key, rawStats[row.key]);
        tr.appendChild(tdRaw);
      }

      tbody.appendChild(tr);
    }
  }

  function init() {
    const wrap = document.getElementById("stat-calculator");
    if (!wrap || wrap.dataset.init) return;
    wrap.dataset.init = "1";

    // populate class select
    const clsSel = document.getElementById("sc-class");
    if (clsSel) {
      clsSel.innerHTML = "";
      for (const [cls, emoji] of Object.entries(CLASS_EMOJI)) {
        const opt = document.createElement("option");
        opt.value       = cls;
        opt.textContent = `${emoji} ${cls}`;
        clsSel.appendChild(opt);
      }
    }

    // wire events
    const lvlNum = document.getElementById("sc-level-num");
    const preSel = document.getElementById("sc-prestige");

    clsSel?.addEventListener("change", render);
    preSel?.addEventListener("input",  render);
    lvlNum?.addEventListener("input",  render);

    render();
  }

  // Material instant-loading compat
  if (typeof document$ !== "undefined") {
    document$.subscribe(init);
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }

})();
