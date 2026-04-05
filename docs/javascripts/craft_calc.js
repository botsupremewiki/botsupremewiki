/* ============================================================
   Calculateur d'Artisanat — Bot Suprême Wiki
   ============================================================ */
(function () {

  const PROFESSIONS = [
    { name: "Heaumier",   emoji: "⛑️", slot: "Casque" },
    { name: "Armurier",   emoji: "🦺", slot: "Plastron" },
    { name: "Tailleur",   emoji: "👖", slot: "Pantalon" },
    { name: "Cordonnier", emoji: "👟", slot: "Chaussures" },
    { name: "Forgeron",   emoji: "⚔️", slot: "Arme" },
    { name: "Joaillier",  emoji: "📿", slot: "Amulette" },
    { name: "Orfèvre",    emoji: "💍", slot: "Anneau" },
  ];

  const CLASS_EMOJI = {
    "Guerrier":         "⚔️",
    "Assassin":         "🗡️",
    "Mage":             "🔮",
    "Tireur":           "🏹",
    "Support":          "🛡️",
    "Vampire":          "🧛",
    "Gardien du Temps": "⏳",
    "Ombre Venin":      "☠️",
    "Pyromancien":      "🔥",
    "Paladin":          "✝️",
  };

  const CLASS_MATS = {
    "Guerrier":         { mat1: "Mineur",     mat2: "Bûcheron"   },
    "Assassin":         { mat1: "Chasseur",   mat2: "Herboriste" },
    "Mage":             { mat1: "Herboriste", mat2: "Mineur"     },
    "Tireur":           { mat1: "Bûcheron",   mat2: "Chasseur"   },
    "Support":          { mat1: "Fermier",    mat2: "Mineur"     },
    "Vampire":          { mat1: "Chasseur",   mat2: "Bûcheron"   },
    "Gardien du Temps": { mat1: "Bûcheron",   mat2: "Herboriste" },
    "Ombre Venin":      { mat1: "Herboriste", mat2: "Fermier"    },
    "Pyromancien":      { mat1: "Fermier",    mat2: "Chasseur"   },
    "Paladin":          { mat1: "Mineur",     mat2: "Fermier"    },
  };

  const FAMILY_MATS = {
    "Mineur":     ["🪨 Minerai de Fer", "⛏️ Minerai d'Acier", "💎 Minerai de Mithril", "🔷 Adamantium Brut", "🔥 Pierre de Feu", "❄️ Pierre de Glace", "🟠 Orichalque", "⚡ Pierre de Foudre", "🔮 Cristal Brut", "💠 Diamant Brut"],
    "Bûcheron":   ["🌳 Bois de Chêne", "🌲 Bois de Sapin", "🪵 Bois d'Ébène", "🪵 Bois de Teck", "🪵 Bois de Cèdre", "✨ Bois Enchanté", "🔴 Bois de Sang", "🌙 Bois de Lune", "🔥 Bois de Feu", "🐉 Bois de Dragon"],
    "Herboriste": ["🌿 Herbe de Soin", "💧 Herbe de Mana", "🌱 Racine de Force", "🌸 Fleur de Lune", "🌼 Pollen Doré", "🍄 Champignon Vénéneux", "🔮 Cristal Végétal", "🌾 Mousse Ancienne", "🌵 Épine de Dragon", "🖤 Lotus de l'Ombre"],
    "Chasseur":   ["🐺 Cuir de Loup", "🦌 Cuir de Cerf", "🐍 Écailles de Serpent", "🦅 Plumes de Phénix", "🦷 Croc de Goule", "🦁 Griffe de Griffon", "🐉 Peau de Dragon", "💀 Os de Chimère", "☠️ Venin de Basilic", "❤️ Cœur de Bête"],
    "Fermier":    ["🌾 Blé", "🌾 Orge", "🌽 Farine de Maïs", "🌿 Herbes Aromatiques", "🫐 Baies Sauvages", "🦄 Lait de Licorne", "🍯 Miel Enchanté", "🧂 Sel de Mer", "🌶️ Épices Rares", "🍑 Fruit du Paradis"],
  };

  // Tiers T1-T10 — quantités et multiplicateurs depuis items.py/_TIER_QTY et models.py/get_craft_source_mult
  // mult = 1.0 + craft_level * 0.01 (au niveau minimum du tier)
  // À T10 niv 100 : ×2.00 (même recette T10, mult max)
  const TIERS = [
    { label: "T1",  level: 1,  matIdx: 0, qty1: 3,  qty2: 2,  mult: "×1.01" },
    { label: "T2",  level: 10, matIdx: 1, qty1: 4,  qty2: 3,  mult: "×1.10" },
    { label: "T3",  level: 20, matIdx: 2, qty1: 5,  qty2: 3,  mult: "×1.20" },
    { label: "T4",  level: 30, matIdx: 3, qty1: 6,  qty2: 4,  mult: "×1.30" },
    { label: "T5",  level: 40, matIdx: 4, qty1: 7,  qty2: 5,  mult: "×1.40" },
    { label: "T6",  level: 50, matIdx: 5, qty1: 8,  qty2: 5,  mult: "×1.50" },
    { label: "T7",  level: 60, matIdx: 6, qty1: 10, qty2: 6,  mult: "×1.60" },
    { label: "T8",  level: 70, matIdx: 7, qty1: 12, qty2: 7,  mult: "×1.70" },
    { label: "T9",  level: 80, matIdx: 8, qty1: 14, qty2: 9,  mult: "×1.80" },
    { label: "T10", level: 90, matIdx: 9, qty1: 16, qty2: 10, mult: "×1.90" },
  ];

  const RARITIES = [
    { name: "Commun",       emoji: "⬜", color: "#9E9E9E" },
    { name: "Peu Commun",   emoji: "🟩", color: "#4CAF50" },
    { name: "Rare",         emoji: "🟦", color: "#2196F3" },
    { name: "Épique",       emoji: "🟪", color: "#9C27B0" },
    { name: "Légendaire",   emoji: "🟧", color: "#FF9800" },
    { name: "Mythique",     emoji: "🟥", color: "#F44336" },
    { name: "Artefact",     emoji: "🔶", color: "#FF5722" },
    { name: "Divin",        emoji: "🌟", color: "#FFD700" },
    { name: "Transcendant", emoji: "💠", color: "#00BCD4" },
    { name: "Prismatique",  emoji: "🌈", color: "#E91E63" },
  ];

  // Keyframes: [zone, weights[10]] — zone = level × 10
  const RARITY_KEYFRAMES = [
    [   1, [100.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, 0.0]],
    [ 200, [ 20.0, 50.0, 20.0,  8.0,  2.0,  0.0,  0.0,  0.0,  0.0, 0.0]],
    [ 400, [  0.0, 10.0, 20.0, 20.0, 18.0, 15.0, 10.0,  5.0,  2.0, 0.0]],
    [ 600, [  0.0,  2.0, 10.0, 18.0, 20.0, 20.0, 18.0,  8.0,  3.0, 1.0]],
    [ 800, [  0.0,  0.0,  8.0, 14.0, 18.0, 20.0, 20.0, 15.0,  4.0, 1.0]],
    [1000, [  0.0,  0.0,  5.0, 10.0, 15.0, 20.0, 20.0, 15.0, 10.0, 5.0]],
  ];

  function getRarityWeights(level) {
    const zone = Math.min(Math.max(level, 1), 100) * 10;
    let weights = RARITY_KEYFRAMES[RARITY_KEYFRAMES.length - 1][1].slice();
    for (let i = 0; i < RARITY_KEYFRAMES.length - 1; i++) {
      const [z0, w0] = RARITY_KEYFRAMES[i];
      const [z1, w1] = RARITY_KEYFRAMES[i + 1];
      if (z0 <= zone && zone <= z1) {
        const t = (zone - z0) / (z1 - z0);
        weights = w0.map((a, j) => a + (w1[j] - a) * t);
        break;
      }
    }
    return weights;
  }

  let selectedProfession = 0;
  let selectedClass = "Guerrier";

  function renderProfessionBar() {
    const bar = document.getElementById("cc-profession-bar");
    if (!bar) return;
    bar.innerHTML = "";
    PROFESSIONS.forEach((p, i) => {
      const btn = document.createElement("button");
      btn.className = "cc-tab-btn" + (i === selectedProfession ? " active" : "");
      btn.textContent = `${p.emoji} ${p.name}`;
      btn.addEventListener("click", () => {
        selectedProfession = i;
        renderProfessionBar();
        renderProfessionInfo();
      });
      bar.appendChild(btn);
    });
  }

  function renderProfessionInfo() {
    const el = document.getElementById("cc-profession-info");
    if (!el) return;
    const p = PROFESSIONS[selectedProfession];
    el.innerHTML = `<span class="cc-slot-badge">${p.emoji} ${p.name}</span> fabrique le slot <strong>${p.slot}</strong> pour toutes les classes.`;
  }

  function renderClassBar() {
    const bar = document.getElementById("cc-class-bar");
    if (!bar) return;
    bar.innerHTML = "";
    for (const [cls, emoji] of Object.entries(CLASS_EMOJI)) {
      const btn = document.createElement("button");
      btn.className = "cc-tab-btn" + (cls === selectedClass ? " active" : "");
      btn.textContent = `${emoji} ${cls}`;
      btn.addEventListener("click", () => {
        selectedClass = cls;
        renderClassBar();
        renderRecipeTable();
      });
      bar.appendChild(btn);
    }
  }

  function renderRecipeTable() {
    const tbody = document.getElementById("cc-recipe-tbody");
    if (!tbody) return;
    const mats = CLASS_MATS[selectedClass];
    const fam1 = FAMILY_MATS[mats.mat1];
    const fam2 = FAMILY_MATS[mats.mat2];

    const matHeader = document.getElementById("cc-mat-header");
    if (matHeader) matHeader.textContent = `Matériaux (${mats.mat1} + ${mats.mat2})`;

    tbody.innerHTML = "";
    for (const tier of TIERS) {
      const m1 = fam1[tier.matIdx];
      const m2 = fam2[tier.matIdx];
      const isT10 = tier.label === "T10";
      const tr = document.createElement("tr");
      if (isT10) tr.className = "cc-row-t10";
      tr.innerHTML = `
        <td>${tier.label}</td>
        <td>${tier.level}${isT10 ? "–100" : ""}</td>
        <td>${m1} ×${tier.qty1}<br>${m2} ×${tier.qty2}</td>
        <td>${tier.mult}${isT10 ? "→×2.00" : ""}</td>
      `;
      tbody.appendChild(tr);
    }
  }

  function renderRarityTable() {
    const input = document.getElementById("cc-prof-level");
    if (!input) return;
    const level = Math.min(Math.max(parseInt(input.value) || 1, 1), 100);
    input.value = level;

    const weights = getRarityWeights(level);
    const total = weights.reduce((a, b) => a + b, 0);

    const tbody = document.getElementById("cc-rarity-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    weights.forEach((w, i) => {
      if (w < 0.05) return;
      const pct = total > 0 ? (w / total * 100).toFixed(1) : "0.0";
      const r = RARITIES[i];
      const barWidth = Math.round(parseFloat(pct));
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${r.emoji} ${r.name}</td>
        <td><strong>${pct}%</strong></td>
        <td><div class="cc-bar"><div class="cc-bar-fill" style="width:${barWidth}%;background:${r.color}"></div></div></td>
      `;
      tbody.appendChild(tr);
    });
  }

  function init() {
    const wrap = document.getElementById("craft-calculator");
    if (wrap) {
      if (wrap.dataset.init) return;
      wrap.dataset.init = "1";
      renderProfessionBar();
      renderProfessionInfo();
      renderClassBar();
      renderRecipeTable();
    }

    const lvlInput = document.getElementById("cc-prof-level");
    if (lvlInput) {
      lvlInput.addEventListener("input", renderRarityTable);
      renderRarityTable();
    }
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(init);
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }

})();
