/* ============================================================
   Calculateur de Stats — Bot Suprême Wiki
   ============================================================ */
(function () {

  const BASE_STATS = {
    "Guerrier":         { hp: 6000, p_atk: 200, m_atk: 0,   p_pen: 90, m_pen: 0,  p_def: 100, m_def: 100, speed: 100, crit_chance: 20.0, crit_damage: 50.0 },
    "Assassin":         { hp: 5000, p_atk: 200, m_atk: 0,   p_pen: 90, m_pen: 0,  p_def: 100, m_def: 100, speed: 100, crit_chance: 20.0, crit_damage: 75.0 },
    "Mage":             { hp: 5000, p_atk: 0,   m_atk: 220, p_pen: 0,  m_pen: 90, p_def: 100, m_def: 100, speed: 100, crit_chance: 20.0, crit_damage: 50.0 },
    "Tireur":           { hp: 5000, p_atk: 200, m_atk: 0,   p_pen: 99, m_pen: 0,  p_def: 100, m_def: 100, speed: 100, crit_chance: 20.0, crit_damage: 50.0 },
    "Support":          { hp: 5000, p_atk: 150, m_atk: 150, p_pen: 90, m_pen: 90, p_def: 100, m_def: 110, speed: 100, crit_chance: 20.0, crit_damage: 50.0 },
    "Vampire":          { hp: 5000, p_atk: 220, m_atk: 0,   p_pen: 90, m_pen: 0,  p_def: 100, m_def: 100, speed: 100, crit_chance: 20.0, crit_damage: 50.0 },
    "Gardien du Temps": { hp: 5000, p_atk: 150, m_atk: 150, p_pen: 90, m_pen: 90, p_def: 100, m_def: 100, speed: 120, crit_chance: 20.0, crit_damage: 50.0 },
    "Ombre Venin":      { hp: 5000, p_atk: 150, m_atk: 150, p_pen: 90, m_pen: 90, p_def: 100, m_def: 100, speed: 100, crit_chance: 30.0, crit_damage: 50.0 },
    "Pyromancien":      { hp: 5000, p_atk: 0,   m_atk: 200, p_pen: 0,  m_pen: 99, p_def: 100, m_def: 100, speed: 100, crit_chance: 20.0, crit_damage: 50.0 },
    "Paladin":          { hp: 5000, p_atk: 200, m_atk: 0,   p_pen: 90, m_pen: 0,  p_def: 110, m_def: 100, speed: 100, crit_chance: 20.0, crit_damage: 50.0 },
  };

  const LEVEL_GROWTH = {
    "Guerrier":         { hp: 60.0, p_atk: 2.0, m_atk: 0.0, p_pen: 0.9,  m_pen: 0.0, p_def: 1.0, m_def: 1.0, speed: 1.0, crit_chance: 0, crit_damage: 0 },
    "Assassin":         { hp: 50.0, p_atk: 2.0, m_atk: 0.0, p_pen: 0.9,  m_pen: 0.0, p_def: 1.0, m_def: 1.0, speed: 1.0, crit_chance: 0, crit_damage: 0 },
    "Mage":             { hp: 50.0, p_atk: 0.0, m_atk: 2.2, p_pen: 0.0,  m_pen: 0.9, p_def: 1.0, m_def: 1.0, speed: 1.0, crit_chance: 0, crit_damage: 0 },
    "Tireur":           { hp: 50.0, p_atk: 2.0, m_atk: 0.0, p_pen: 0.99, m_pen: 0.0, p_def: 1.0, m_def: 1.0, speed: 1.0, crit_chance: 0, crit_damage: 0 },
    "Support":          { hp: 50.0, p_atk: 1.5, m_atk: 1.5, p_pen: 0.9,  m_pen: 0.9, p_def: 1.0, m_def: 1.1, speed: 1.0, crit_chance: 0, crit_damage: 0 },
    "Vampire":          { hp: 50.0, p_atk: 2.2, m_atk: 0.0, p_pen: 0.9,  m_pen: 0.0, p_def: 1.0, m_def: 1.0, speed: 1.0, crit_chance: 0, crit_damage: 0 },
    "Gardien du Temps": { hp: 50.0, p_atk: 1.5, m_atk: 1.5, p_pen: 0.9,  m_pen: 0.9, p_def: 1.0, m_def: 1.0, speed: 1.2, crit_chance: 0, crit_damage: 0 },
    "Ombre Venin":      { hp: 50.0, p_atk: 1.5, m_atk: 1.5, p_pen: 0.9,  m_pen: 0.9, p_def: 1.0, m_def: 1.0, speed: 1.0, crit_chance: 0, crit_damage: 0 },
    "Pyromancien":      { hp: 50.0, p_atk: 0.0, m_atk: 2.0, p_pen: 0.0,  m_pen: 0.99,p_def: 1.0, m_def: 1.0, speed: 1.0, crit_chance: 0, crit_damage: 0 },
    "Paladin":          { hp: 50.0, p_atk: 2.0, m_atk: 0.0, p_pen: 0.9,  m_pen: 0.0, p_def: 1.1, m_def: 1.0, speed: 1.0, crit_chance: 0, crit_damage: 0 },
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
