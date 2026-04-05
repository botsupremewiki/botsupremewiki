/* ============================================================
   Calculateur d'Équipements & Panoplies — Bot Suprême Wiki
   ============================================================ */
(function () {

  /* ── Données de classe ─────────────────────────────────────── */
  const BASE_STATS = {
    "Guerrier":         { hp:550,  p_atk:52,  m_atk:0,   p_pen:8,  m_pen:0,  p_def:32, m_def:6,  speed:80,  crit_chance:5.0,  crit_damage:50.0 },
    "Assassin":         { hp:500,  p_atk:50,  m_atk:0,   p_pen:10, m_pen:0,  p_def:4,  m_def:3,  speed:105, crit_chance:18.0, crit_damage:75.0 },
    "Mage":             { hp:420,  p_atk:0,   m_atk:42,  p_pen:0,  m_pen:8,  p_def:3,  m_def:10, speed:92,  crit_chance:12.0, crit_damage:75.0 },
    "Tireur":           { hp:440,  p_atk:44,  m_atk:0,   p_pen:8,  m_pen:0,  p_def:4,  m_def:4,  speed:105, crit_chance:16.0, crit_damage:75.0 },
    "Support":          { hp:650,  p_atk:48,  m_atk:48,  p_pen:6,  m_pen:6,  p_def:25, m_def:25, speed:80,  crit_chance:5.0,  crit_damage:40.0 },
    "Vampire":          { hp:580,  p_atk:60,  m_atk:0,   p_pen:9,  m_pen:0,  p_def:12, m_def:7,  speed:90,  crit_chance:15.0, crit_damage:75.0 },
    "Gardien du Temps": { hp:480,  p_atk:35,  m_atk:35,  p_pen:6,  m_pen:6,  p_def:18, m_def:18, speed:95,  crit_chance:8.0,  crit_damage:55.0 },
    "Ombre Venin":      { hp:460,  p_atk:32,  m_atk:32,  p_pen:5,  m_pen:5,  p_def:5,  m_def:5,  speed:115, crit_chance:17.0, crit_damage:70.0 },
    "Pyromancien":      { hp:500,  p_atk:0,   m_atk:58,  p_pen:0,  m_pen:9,  p_def:2,  m_def:10, speed:85,  crit_chance:13.0, crit_damage:75.0 },
    "Paladin":          { hp:560,  p_atk:42,  m_atk:0,   p_pen:8,  m_pen:0,  p_def:35, m_def:22, speed:72,  crit_chance:5.0,  crit_damage:50.0 },
  };
  const LEVEL_GROWTH = {
    "Guerrier":         { hp:45.44, p_atk:2.400, m_atk:0,     p_pen:0,     m_pen:0,     p_def:0.822, m_def:0.194, speed:0.230, crit_chance:0, crit_damage:0 },
    "Assassin":         { hp:36.54, p_atk:2.643, m_atk:0,     p_pen:0.549, m_pen:0,     p_def:0,     m_def:0,     speed:0.365, crit_chance:0, crit_damage:0 },
    "Mage":             { hp:39.64, p_atk:0,     m_atk:2.814, p_pen:0,     m_pen:0.553, p_def:0,     m_def:0,     speed:0.405, crit_chance:0, crit_damage:0 },
    "Tireur":           { hp:37.60, p_atk:2.668, m_atk:0,     p_pen:0.555, m_pen:0,     p_def:0,     m_def:0,     speed:0.360, crit_chance:0, crit_damage:0 },
    "Support":          { hp:72.42, p_atk:1.283, m_atk:1.283, p_pen:0,     m_pen:0,     p_def:0.630, m_def:0.630, speed:0.195, crit_chance:0, crit_damage:0 },
    "Vampire":          { hp:50.00, p_atk:2.638, m_atk:0,     p_pen:0.528, m_pen:0,     p_def:0.268, m_def:0.193, speed:0.245, crit_chance:0, crit_damage:0 },
    "Gardien du Temps": { hp:41.56, p_atk:1.400, m_atk:1.400, p_pen:0.304, m_pen:0.304, p_def:0.362, m_def:0.362, speed:0.240, crit_chance:0, crit_damage:0 },
    "Ombre Venin":      { hp:45.65, p_atk:1.540, m_atk:1.540, p_pen:0.300, m_pen:0.300, p_def:0,     m_def:0,     speed:0.345, crit_chance:0, crit_damage:0 },
    "Pyromancien":      { hp:43.64, p_atk:0,     m_atk:3.100, p_pen:0,     m_pen:0.610, p_def:0,     m_def:0,     speed:0.395, crit_chance:0, crit_damage:0 },
    "Paladin":          { hp:71.51, p_atk:2.361, m_atk:0,     p_pen:0,     m_pen:0,     p_def:0.916, m_def:0.428, speed:0.193, crit_chance:0, crit_damage:0 },
  };
  const CLASS_EMOJI = { "Guerrier":"⚔️","Assassin":"🗡️","Mage":"🔮","Tireur":"🏹","Support":"🛡️","Vampire":"🧛","Gardien du Temps":"⏳","Ombre Venin":"☠️","Pyromancien":"🔥","Paladin":"✝️" };
  const CLASS_TYPE  = { "Guerrier":"physique","Assassin":"physique","Tireur":"physique","Vampire":"physique","Paladin":"physique","Mage":"magique","Pyromancien":"magique","Support":"hybride","Gardien du Temps":"hybride","Ombre Venin":"hybride" };

  /* ── Préfixes de noms d'items par slot/classe ──────────────── */
  const SLOT_PREFIX = {
    "Guerrier":         {casque:"Heaume",    plastron:"Cuirasse",   pantalon:"Braies",    chaussures:"Sollerets", arme:"Épée",    amulette:"Médaillon", anneau:"Chevalière"},
    "Assassin":         {casque:"Capuche",   plastron:"Mantelet",   pantalon:"Grègues",   chaussures:"Chaussons", arme:"Dague",   amulette:"Pendentif", anneau:"Signet"},
    "Mage":             {casque:"Chapeau",   plastron:"Robe",       pantalon:"Jupe",      chaussures:"Sandales",  arme:"Bâton",   amulette:"Talisman",  anneau:"Bague"},
    "Tireur":           {casque:"Cagoule",   plastron:"Veste",      pantalon:"Jambières", chaussures:"Bottes",    arme:"Arc",     amulette:"Collier",   anneau:"Jonc"},
    "Support":          {casque:"Bassinet",  plastron:"Brigandine", pantalon:"Cuissardes",chaussures:"Grèves",    arme:"Bouclier",amulette:"Amulette",  anneau:"Sceau"},
    "Vampire":          {casque:"Masque",    plastron:"Cape",       pantalon:"Collant",   chaussures:"Bottines",  arme:"Crocs",   amulette:"Breloque",  anneau:"Cachet"},
    "Gardien du Temps": {casque:"Couronne",  plastron:"Manteau",    pantalon:"Bas",       chaussures:"Escarpes",  arme:"Sablier", amulette:"Relique",   anneau:"Alliance"},
    "Ombre Venin":      {casque:"Voile",     plastron:"Suaire",     pantalon:"Guêtres",   chaussures:"Mocassins", arme:"Aiguille",amulette:"Fiole",     anneau:"Annelet"},
    "Pyromancien":      {casque:"Coiffe",    plastron:"Tunique",    pantalon:"Pantalon",  chaussures:"Sabots",    arme:"Torche",  amulette:"Phylactère",anneau:"Gemme"},
    "Paladin":          {casque:"Armet",     plastron:"Haubert",    pantalon:"Tassettes", chaussures:"Éperons",   arme:"Marteau", amulette:"Croix",     anneau:"Insigne"},
  };

  /* ── Formules stats item ───────────────────────────────────── */
  const RARITY_MULT = { commun:1.0,"peu commun":1.2,rare:1.4,"épique":1.6,"légendaire":1.8,mythique:2.0,artefact:2.2,divin:2.4,transcendant:2.6,prismatique:3.0 };
  const SOURCE_MULT = { monde:1.0,donjon_classique:1.2,donjon_elite:1.4,donjon_abyssal:1.6,raid:1.8 };
  const RARITY_N_STATS = { commun:1,"peu commun":1,rare:2,"épique":2,"légendaire":3,mythique:3,artefact:4,divin:4,transcendant:5,prismatique:5 };

  const ARMOR_SLOT = {
    casque:     [["m_def",0.38],["hp",0.28],["speed",0.20],["p_def",0.14]],
    plastron:   [["hp",0.38],  ["p_def",0.28],["m_def",0.20],["speed",0.14]],
    pantalon:   [["p_def",0.38],["speed",0.28],["hp",0.20],  ["m_def",0.14]],
    chaussures: [["speed",0.38],["m_def",0.28],["p_def",0.20],["hp",0.14]],
  };
  const OFF_SLOT = {
    arme:     ["atk","pen","crit_chance","crit_damage","speed"],
    amulette: ["crit_chance","crit_damage","atk","speed","pen"],
    anneau:   ["pen","atk","speed","crit_chance","crit_damage"],
  };
  const OFF_WEIGHTS = [0.35,0.25,0.18,0.13,0.09];

  function statAt(cls, stat, level) {
    const b = (BASE_STATS[cls]  || {})[stat] || 0;
    const g = (LEVEL_GROWTH[cls]|| {})[stat] || 0;
    return b + g * (level - 1);
  }

  function computeItemStats(slot, cls, level, source, craftTier, rarity, enhancement) {
    level = Math.max(1, Math.min(level, 1000));
    const srcMult  = source === "craft" ? (1.0 + Math.max(1, craftTier) * 0.1) : (SOURCE_MULT[source] || 1.0);
    const rarMult  = RARITY_MULT[rarity] || 1.0;
    const totalMul = rarMult + srcMult - 1 + enhancement * 0.1;
    const nStats   = RARITY_N_STATS[rarity] || 1;
    const stats    = {};

    if (ARMOR_SLOT[slot]) {
      ARMOR_SLOT[slot].slice(0, nStats).forEach(([stat, w]) => {
        const base = statAt(cls, stat, level);
        const val  = base * w * totalMul;
        stats[stat] = (stats[stat] || 0) + (["crit_chance","crit_damage"].includes(stat) ? Math.round(val*100)/100 : Math.round(val));
      });
    } else if (OFF_SLOT[slot]) {
      const ctype = CLASS_TYPE[cls] || "physique";
      OFF_SLOT[slot].slice(0, nStats).forEach((key, i) => {
        const w = OFF_WEIGHTS[i];
        if (key === "atk") {
          if (ctype === "physique") { stats.p_atk = (stats.p_atk||0) + Math.round(statAt(cls,"p_atk",level) * w * totalMul); }
          else if (ctype === "magique") { stats.m_atk = (stats.m_atk||0) + Math.round(statAt(cls,"m_atk",level) * w * totalMul); }
          else { stats.p_atk = (stats.p_atk||0) + Math.round(statAt(cls,"p_atk",level) * (w/2) * totalMul); stats.m_atk = (stats.m_atk||0) + Math.round(statAt(cls,"m_atk",level) * (w/2) * totalMul); }
        } else if (key === "pen") {
          if (ctype === "physique") { stats.p_pen = (stats.p_pen||0) + Math.round(statAt(cls,"p_pen",level) * w * totalMul); }
          else if (ctype === "magique") { stats.m_pen = (stats.m_pen||0) + Math.round(statAt(cls,"m_pen",level) * w * totalMul); }
          else { stats.p_pen = (stats.p_pen||0) + Math.round(statAt(cls,"p_pen",level) * (w/2) * totalMul); stats.m_pen = (stats.m_pen||0) + Math.round(statAt(cls,"m_pen",level) * (w/2) * totalMul); }
        } else if (["crit_chance","crit_damage"].includes(key)) {
          const raw = statAt(cls, key, level) * w * totalMul;
          stats[key] = Math.round((stats[key]||0) + raw * 100) / 100;
        } else {
          stats[key] = (stats[key]||0) + Math.round(statAt(cls, key, level) * w * totalMul);
        }
      });
    }
    return stats;
  }

  /* ── Panoplies ─────────────────────────────────────────────── */
  // set_key → {class, source, name, theme, 2pcs, 3pcs, 4pcs, 5pcs, 6pcs, 7pcs}
  // class_source → set_key mapping
  const SET_BONUSES = {
    "guerrier_monde":            {cls:"Guerrier",source:"monde",            name:"Acier de Fer",            theme:"de Fer",            "2pcs":["speed"],      "3pcs":"+5% HP totaux.",                                                                              "4pcs":["p_def"],     "5pcs":["p_atk"],      "6pcs":["hp"],         "7pcs":"+10% HP totaux."},
    "guerrier_donjon_classique": {cls:"Guerrier",source:"donjon_classique", name:"Rempart de Fer",          theme:"du Rempart",        "2pcs":["speed"],      "3pcs":"-5% dégâts reçus.",                                                                           "4pcs":["m_def"],     "5pcs":["hp"],         "6pcs":["p_def"],      "7pcs":"-10% dégâts reçus."},
    "guerrier_craft":            {cls:"Guerrier",source:"craft",            name:"Métal Forgé",             theme:"Forgé",             "2pcs":["crit_damage"],"3pcs":"+5% dégâts totaux.",                                                                           "4pcs":["hp"],        "5pcs":["p_pen"],      "6pcs":["p_atk"],      "7pcs":"+10% dégâts totaux."},
    "guerrier_donjon_elite":     {cls:"Guerrier",source:"donjon_elite",     name:"Titan Écarlate",          theme:"du Titan",          "2pcs":["crit_chance"],"3pcs":"Bonus de ×0.25 de ressources.",                                                               "4pcs":["p_pen"],     "5pcs":["hp"],         "6pcs":["p_atk"],      "7pcs":"Bonus de ×0.5 de ressources."},
    "guerrier_donjon_abyssal":   {cls:"Guerrier",source:"donjon_abyssal",   name:"Seigneur de l'Abîme",    theme:"de l'Abîme",        "2pcs":["crit_damage"],"3pcs":"Bonus de ×0.5 de passif de classe.",                                                          "4pcs":["crit_chance"],"5pcs":["p_atk"],     "6pcs":["p_pen"],      "7pcs":"Bonus de ×1.0 de passif de classe."},
    "guerrier_raid":             {cls:"Guerrier",source:"raid",             name:"Colosse de Guerre",       theme:"de Guerre",         "2pcs":["p_pen"],      "3pcs":"Une fois par combat, si tu meurs, tu ne meurs pas et restes à 1 HP pendant 1 tour.",           "4pcs":["p_def"],     "5pcs":["p_atk"],      "6pcs":["hp"],         "7pcs":"Une fois par combat, si tu meurs, tu ne meurs pas et restes à 1 HP pendant 2 tours."},
    "assassin_monde":            {cls:"Assassin",source:"monde",            name:"Ombre Légère",            theme:"des Ombres",        "2pcs":["crit_chance"],"3pcs":"+25% de dégâts au premier coup.",                                                             "4pcs":["speed"],     "5pcs":["p_atk"],      "6pcs":["hp"],         "7pcs":"+50% de dégâts au premier coup."},
    "assassin_donjon_classique": {cls:"Assassin",source:"donjon_classique", name:"Lame du Crépuscule",     theme:"du Crépuscule",     "2pcs":["p_pen"],      "3pcs":"+5% dégâts totaux.",                                                                           "4pcs":["p_atk"],     "5pcs":["crit_chance"],"6pcs":["crit_damage"],"7pcs":"+10% dégâts totaux."},
    "assassin_craft":            {cls:"Assassin",source:"craft",            name:"Acier Trempé",            theme:"Trempé",            "2pcs":["crit_damage"],"3pcs":"+5% chance d'esquive.",                                                                        "4pcs":["crit_chance"],"5pcs":["p_atk"],     "6pcs":["speed"],      "7pcs":"+10% chance d'esquive."},
    "assassin_donjon_elite":     {cls:"Assassin",source:"donjon_elite",     name:"Fantôme Acéré",           theme:"du Fantôme",        "2pcs":["crit_damage"],"3pcs":"Bonus de ×0.25 de ressources.",                                                               "4pcs":["p_atk"],     "5pcs":["crit_chance"],"6pcs":["speed"],      "7pcs":"Bonus de ×0.5 de ressources."},
    "assassin_donjon_abyssal":   {cls:"Assassin",source:"donjon_abyssal",   name:"Voile de Sang",           theme:"de Sang",           "2pcs":["speed"],      "3pcs":"Bonus de ×0.5 de passif de classe.",                                                          "4pcs":["crit_damage"],"5pcs":["p_pen"],     "6pcs":["p_atk"],      "7pcs":"Bonus de ×1.0 de passif de classe."},
    "assassin_raid":             {cls:"Assassin",source:"raid",             name:"Exécuteur des Ombres",    theme:"de l'Exécuteur",    "2pcs":["crit_chance"],"3pcs":"+10% dégâts sur les ennemis à moins de 30% HP.",                                              "4pcs":["p_pen"],     "5pcs":["crit_damage"],"6pcs":["p_atk"],      "7pcs":"+20% dégâts sur les ennemis à moins de 30% HP."},
    "mage_monde":                {cls:"Mage",    source:"monde",            name:"Novice Arcane",           theme:"Arcane",            "2pcs":["speed"],      "3pcs":"+10% de la RES Magique ennemie ignorée.",                                                     "4pcs":["hp"],        "5pcs":["m_pen"],      "6pcs":["m_atk"],      "7pcs":"+20% de la RES Magique ennemie ignorée."},
    "mage_donjon_classique":     {cls:"Mage",    source:"donjon_classique", name:"Manteau Astral",          theme:"Astral",            "2pcs":["m_pen"],      "3pcs":"+5% dégâts totaux.",                                                                           "4pcs":["m_atk"],     "5pcs":["m_def"],      "6pcs":["hp"],         "7pcs":"+10% dégâts totaux."},
    "mage_craft":                {cls:"Mage",    source:"craft",            name:"Tissu Enchanté",          theme:"Enchanté",          "2pcs":["m_pen"],      "3pcs":"+10% de vitesse totale.",                                                                      "4pcs":["crit_chance"],"5pcs":["crit_damage"],"6pcs":["m_atk"],      "7pcs":"+20% de vitesse totale."},
    "mage_donjon_elite":         {cls:"Mage",    source:"donjon_elite",     name:"Voile du Prophète",       theme:"du Prophète",       "2pcs":["speed"],      "3pcs":"Bonus de ×0.25 de ressources.",                                                               "4pcs":["crit_damage"],"5pcs":["m_atk"],     "6pcs":["m_pen"],      "7pcs":"Bonus de ×0.5 de ressources."},
    "mage_donjon_abyssal":       {cls:"Mage",    source:"donjon_abyssal",   name:"Suaire Primordial",       theme:"Primordial",        "2pcs":["crit_chance"],"3pcs":"Bonus de ×0.5 de passif de classe.",                                                          "4pcs":["m_pen"],     "5pcs":["m_atk"],      "6pcs":["crit_damage"],"7pcs":"Bonus de ×1.0 de passif de classe."},
    "mage_raid":                 {cls:"Mage",    source:"raid",             name:"Nexus Primordial",        theme:"du Nexus",          "2pcs":["hp"],         "3pcs":"1 fois par combat, à 30% de tes HP, tu obtiens un bouclier de 2.5× ton ATK Magique.",        "4pcs":["crit_damage"],"5pcs":["m_pen"],     "6pcs":["m_atk"],      "7pcs":"1 fois par combat, à 30% de tes HP, tu obtiens un bouclier de 5× ton ATK Magique."},
    "tireur_monde":              {cls:"Tireur",  source:"monde",            name:"Carquois de Chasse",      theme:"de Chasse",         "2pcs":["speed"],      "3pcs":"+5% de vitesse.",                                                                              "4pcs":["crit_chance"],"5pcs":["p_atk"],     "6pcs":["hp"],         "7pcs":"+10% de vitesse."},
    "tireur_donjon_classique":   {cls:"Tireur",  source:"donjon_classique", name:"Arc du Faucon",           theme:"du Faucon",         "2pcs":["p_pen"],      "3pcs":"+5% dégâts totaux.",                                                                           "4pcs":["speed"],     "5pcs":["crit_chance"],"6pcs":["p_atk"],      "7pcs":"+10% dégâts totaux."},
    "tireur_craft":              {cls:"Tireur",  source:"craft",            name:"Bois Taillé",             theme:"Taillé",            "2pcs":["p_pen"],      "3pcs":"+5% de la RES Physique et Magique ennemie ignorée.",                                           "4pcs":["crit_chance"],"5pcs":["p_atk"],     "6pcs":["crit_damage"],"7pcs":"+10% de la RES Physique et Magique ennemie ignorée."},
    "tireur_donjon_elite":       {cls:"Tireur",  source:"donjon_elite",     name:"Tempête d'Acier",         theme:"de la Tempête",     "2pcs":["crit_chance"],"3pcs":"Bonus de ×0.25 de ressources.",                                                               "4pcs":["p_atk"],     "5pcs":["crit_damage"],"6pcs":["speed"],      "7pcs":"Bonus de ×0.5 de ressources."},
    "tireur_donjon_abyssal":     {cls:"Tireur",  source:"donjon_abyssal",   name:"Œil de l'Horizon",        theme:"de l'Horizon",      "2pcs":["crit_chance"],"3pcs":"Bonus de ×0.5 de passif de classe.",                                                          "4pcs":["p_atk"],     "5pcs":["p_pen"],      "6pcs":["crit_damage"],"7pcs":"Bonus de ×1.0 de passif de classe."},
    "tireur_raid":               {cls:"Tireur",  source:"raid",             name:"Ouragan d'Acier",         theme:"de l'Ouragan",      "2pcs":["p_pen"],      "3pcs":"+10% chance de double tir.",                                                                   "4pcs":["crit_damage"],"5pcs":["speed"],     "6pcs":["p_atk"],      "7pcs":"+20% chance de double tir."},
    "support_monde":             {cls:"Support", source:"monde",            name:"Médaillon du Novice",     theme:"du Novice",         "2pcs":["speed"],      "3pcs":"Renvoie 5% des dégâts reçus en dégâts purs.",                                                 "4pcs":["m_def"],     "5pcs":["p_def"],      "6pcs":["hp"],         "7pcs":"Renvoie 10% des dégâts reçus en dégâts purs."},
    "support_donjon_classique":  {cls:"Support", source:"donjon_classique", name:"Armure du Défenseur",     theme:"du Défenseur",      "2pcs":["m_atk"],      "3pcs":"-5% dégâts reçus.",                                                                           "4pcs":["p_atk"],     "5pcs":["m_def"],      "6pcs":["p_def"],      "7pcs":"-10% dégâts reçus."},
    "support_craft":             {cls:"Support", source:"craft",            name:"Métal Béni",              theme:"Béni",              "2pcs":["p_atk"],      "3pcs":"+5% dégâts physiques et magiques.",                                                           "4pcs":["m_atk"],     "5pcs":["hp"],         "6pcs":["m_def"],      "7pcs":"+10% dégâts physiques et magiques."},
    "support_donjon_elite":      {cls:"Support", source:"donjon_elite",     name:"Bénédiction Sacrée",      theme:"Sacré",             "2pcs":["m_atk"],      "3pcs":"Bonus de ×0.25 de ressources.",                                                               "4pcs":["m_def"],     "5pcs":["p_def"],      "6pcs":["hp"],         "7pcs":"Bonus de ×0.5 de ressources."},
    "support_donjon_abyssal":    {cls:"Support", source:"donjon_abyssal",   name:"Bouclier du Gardien",     theme:"du Gardien",        "2pcs":["p_atk"],      "3pcs":"Bonus de ×0.5 de passif de classe.",                                                          "4pcs":["m_def"],     "5pcs":["hp"],         "6pcs":["p_def"],      "7pcs":"Bonus de ×1.0 de passif de classe."},
    "support_raid":              {cls:"Support", source:"raid",             name:"Lumière Éternelle",       theme:"de la Lumière",     "2pcs":["p_atk"],      "3pcs":"Régénère 2.5% de tes HP max par tour.",                                                       "4pcs":["p_def"],     "5pcs":["m_def"],      "6pcs":["hp"],         "7pcs":"Régénère 5% de tes HP max par tour."},
    "vampire_monde":             {cls:"Vampire", source:"monde",            name:"Crocs de la Nuit",        theme:"de la Nuit",        "2pcs":["p_pen"],      "3pcs":"+5% dégâts totaux.",                                                                           "4pcs":["speed"],     "5pcs":["hp"],         "6pcs":["p_atk"],      "7pcs":"+10% dégâts totaux."},
    "vampire_donjon_classique":  {cls:"Vampire", source:"donjon_classique", name:"Manteau Maudit",          theme:"Maudit",            "2pcs":["crit_damage"],"3pcs":"+5% vol de vie.",                                                                              "4pcs":["crit_chance"],"5pcs":["hp"],        "6pcs":["p_atk"],      "7pcs":"+10% vol de vie."},
    "vampire_craft":             {cls:"Vampire", source:"craft",            name:"Acier Ensanglanté",       theme:"Ensanglanté",       "2pcs":["crit_chance"],"3pcs":"+10% vitesse totale.",                                                                          "4pcs":["hp"],        "5pcs":["p_atk"],      "6pcs":["speed"],      "7pcs":"+20% vitesse totale."},
    "vampire_donjon_elite":      {cls:"Vampire", source:"donjon_elite",     name:"Suaire des Ténèbres",     theme:"des Ténèbres",      "2pcs":["speed"],      "3pcs":"Bonus de ×0.25 de ressources.",                                                               "4pcs":["crit_damage"],"5pcs":["p_atk"],     "6pcs":["hp"],         "7pcs":"Bonus de ×0.5 de ressources."},
    "vampire_donjon_abyssal":    {cls:"Vampire", source:"donjon_abyssal",   name:"Seigneur des Ténèbres",   theme:"du Seigneur",       "2pcs":["crit_chance"],"3pcs":"Bonus de ×0.5 de passif de classe.",                                                          "4pcs":["crit_damage"],"5pcs":["p_pen"],     "6pcs":["p_atk"],      "7pcs":"Bonus de ×1.0 de passif de classe."},
    "vampire_raid":              {cls:"Vampire", source:"raid",             name:"Prince Immortel",         theme:"Immortel",          "2pcs":["speed"],      "3pcs":"Limite les dégâts reçus à 30% de tes HP max par coup.",                                       "4pcs":["p_pen"],     "5pcs":["p_atk"],      "6pcs":["hp"],         "7pcs":"Limite les dégâts reçus à 15% de tes HP max par coup."},
    "gardien_monde":             {cls:"Gardien du Temps",source:"monde",            name:"Sablier Brisé",   theme:"Brisé",             "2pcs":["hp"],         "3pcs":"+5% dégâts physiques et magiques.",                                                           "4pcs":["p_atk"],     "5pcs":["m_atk"],      "6pcs":["speed"],      "7pcs":"+10% dégâts physiques et magiques."},
    "gardien_donjon_classique":  {cls:"Gardien du Temps",source:"donjon_classique", name:"Horloge Fractale",theme:"Fractal",           "2pcs":["crit_damage"],"3pcs":"+15% de chance de réduire une stat ennemie supplémentaire.",                                 "4pcs":["speed"],     "5pcs":["m_atk"],      "6pcs":["p_atk"],      "7pcs":"+30% de chance de réduire une stat ennemie supplémentaire."},
    "gardien_craft":             {cls:"Gardien du Temps",source:"craft",            name:"Tissu Temporel",  theme:"Temporel",          "2pcs":["speed"],      "3pcs":"Réduit la vitesse de l'ennemi de 10%.",                                                       "4pcs":["m_atk"],     "5pcs":["p_atk"],      "6pcs":["hp"],         "7pcs":"Réduit la vitesse de l'ennemi de 20%."},
    "gardien_donjon_elite":      {cls:"Gardien du Temps",source:"donjon_elite",     name:"Chrono Maudit",   theme:"Chronique",         "2pcs":["speed"],      "3pcs":"Bonus de ×0.25 de ressources.",                                                               "4pcs":["crit_damage"],"5pcs":["p_atk"],     "6pcs":["m_atk"],      "7pcs":"Bonus de ×0.5 de ressources."},
    "gardien_donjon_abyssal":    {cls:"Gardien du Temps",source:"donjon_abyssal",   name:"Paradoxe Temporel",theme:"du Paradoxe",      "2pcs":["m_pen"],      "3pcs":"Bonus de ×0.5 de passif de classe.",                                                          "4pcs":["crit_damage"],"5pcs":["m_atk"],     "6pcs":["p_atk"],      "7pcs":"Bonus de ×1.0 de passif de classe."},
    "gardien_raid":              {cls:"Gardien du Temps",source:"raid",             name:"Maître du Destin",theme:"du Destin",         "2pcs":["m_pen"],      "3pcs":"5% de chance que ton tour recommence après ton attaque/sort (max d'affilée : 2).",            "4pcs":["p_pen"],     "5pcs":["p_atk"],      "6pcs":["m_atk"],      "7pcs":"10% de chance que ton tour recommence après ton attaque/sort (max d'affilée : 2)."},
    "ombre_monde":               {cls:"Ombre Venin",source:"monde",            name:"Distillat Vénéneux",  theme:"Vénéneux",          "2pcs":["speed"],      "3pcs":"Cible empoisonnée te fait -5% de dégâts.",                                                   "4pcs":["m_atk"],     "5pcs":["p_atk"],      "6pcs":["hp"],         "7pcs":"Cible empoisonnée te fait -10% de dégâts."},
    "ombre_donjon_classique":    {cls:"Ombre Venin",source:"donjon_classique", name:"Aiguille Toxique",    theme:"Toxique",           "2pcs":["p_pen"],      "3pcs":"+5% dégâts sur les cibles empoisonnées.",                                                    "4pcs":["m_atk"],     "5pcs":["p_atk"],      "6pcs":["speed"],      "7pcs":"+10% dégâts sur les cibles empoisonnées."},
    "ombre_craft":               {cls:"Ombre Venin",source:"craft",            name:"Venin Distillé",      theme:"Distillé",          "2pcs":["crit_damage"],"3pcs":"-3% de vitesse de l'ennemi par stack de poison.",                                             "4pcs":["p_pen"],     "5pcs":["m_atk"],      "6pcs":["p_atk"],      "7pcs":"-6% de vitesse de l'ennemi par stack de poison."},
    "ombre_donjon_elite":        {cls:"Ombre Venin",source:"donjon_elite",     name:"Brume Toxique",       theme:"de Brume",          "2pcs":["m_atk"],      "3pcs":"Bonus de ×0.25 de ressources.",                                                               "4pcs":["crit_chance"],"5pcs":["p_pen"],     "6pcs":["p_atk"],      "7pcs":"Bonus de ×0.5 de ressources."},
    "ombre_donjon_abyssal":      {cls:"Ombre Venin",source:"donjon_abyssal",   name:"Essence Corrompue",   theme:"Corrompu",          "2pcs":["m_atk"],      "3pcs":"Bonus de ×0.5 de passif de classe.",                                                          "4pcs":["p_atk"],     "5pcs":["p_pen"],      "6pcs":["m_pen"],      "7pcs":"Bonus de ×1.0 de passif de classe."},
    "ombre_raid":                {cls:"Ombre Venin",source:"raid",             name:"Nécrosis Primordiale", theme:"de la Nécrosis",    "2pcs":["m_pen"],      "3pcs":"Si la cible a moins de 1.5% de ses HP max par stack de poison, elle est exécutée.",          "4pcs":["p_pen"],     "5pcs":["m_atk"],      "6pcs":["p_atk"],      "7pcs":"Si la cible a moins de 3% de ses HP max par stack de poison, elle est exécutée."},
    "pyro_monde":                {cls:"Pyromancien",source:"monde",            name:"Tison Ardent",         theme:"Ardent",            "2pcs":["speed"],      "3pcs":"+5% dégâts totaux.",                                                                          "4pcs":["hp"],        "5pcs":["m_pen"],      "6pcs":["m_atk"],      "7pcs":"+10% dégâts totaux."},
    "pyro_donjon_classique":     {cls:"Pyromancien",source:"donjon_classique", name:"Flamme Enflammée",     theme:"Enflammé",          "2pcs":["crit_chance"],"3pcs":"10% de ne pas dépenser de mana quand on utilise un sort.",                                    "4pcs":["m_atk"],     "5pcs":["speed"],      "6pcs":["m_pen"],      "7pcs":"20% de ne pas dépenser de mana quand on utilise un sort."},
    "pyro_craft":                {cls:"Pyromancien",source:"craft",            name:"Pierre Incandescente", theme:"Incandescent",      "2pcs":["m_pen"],      "3pcs":"Tes coups critiques ajoutent 1 stack de brûlure.",                                            "4pcs":["crit_chance"],"5pcs":["m_atk"],     "6pcs":["crit_damage"],"7pcs":"Tes coups critiques ajoutent 2 stacks de brûlure."},
    "pyro_donjon_elite":         {cls:"Pyromancien",source:"donjon_elite",     name:"Brasier Infernal",     theme:"Infernal",          "2pcs":["m_atk"],      "3pcs":"Bonus de ×0.25 de ressources.",                                                               "4pcs":["crit_chance"],"5pcs":["crit_damage"],"6pcs":["speed"],      "7pcs":"Bonus de ×0.5 de ressources."},
    "pyro_donjon_abyssal":       {cls:"Pyromancien",source:"donjon_abyssal",   name:"Âme Volcanique",       theme:"Volcanique",        "2pcs":["m_atk"],      "3pcs":"Bonus de ×0.5 de passif de classe.",                                                          "4pcs":["m_pen"],     "5pcs":["crit_damage"],"6pcs":["hp"],         "7pcs":"Bonus de ×1.0 de passif de classe."},
    "pyro_raid":                 {cls:"Pyromancien",source:"raid",             name:"Phénix Éternel",        theme:"du Phénix",         "2pcs":["crit_damage"],"3pcs":"50% de chance que Flammèche soit lancé gratuitement quand Brasier est utilisé.",             "4pcs":["speed"],     "5pcs":["hp"],         "6pcs":["m_atk"],      "7pcs":"Flammèche est lancé gratuitement quand Brasier est utilisé."},
    "paladin_monde":             {cls:"Paladin", source:"monde",            name:"Armure Consacrée",         theme:"Consacré",          "2pcs":["speed"],      "3pcs":"-5% dégâts reçus.",                                                                           "4pcs":["m_def"],     "5pcs":["p_def"],      "6pcs":["hp"],         "7pcs":"-10% dégâts reçus."},
    "paladin_donjon_classique":  {cls:"Paladin", source:"donjon_classique", name:"Vœu du Croisé",            theme:"du Croisé",         "2pcs":["speed"],      "3pcs":"Renvoie 5% des dégâts reçus en dégâts purs.",                                                "4pcs":["hp"],        "5pcs":["m_def"],      "6pcs":["p_def"],      "7pcs":"Renvoie 10% des dégâts reçus en dégâts purs."},
    "paladin_craft":             {cls:"Paladin", source:"craft",            name:"Métal Sanctifié",          theme:"Sanctifié",         "2pcs":["hp"],         "3pcs":"+10% de vitesse.",                                                                            "4pcs":["speed"],     "5pcs":["p_def"],      "6pcs":["m_def"],      "7pcs":"+20% de vitesse."},
    "paladin_donjon_elite":      {cls:"Paladin", source:"donjon_elite",     name:"Lumière Divine",           theme:"Divin",             "2pcs":["m_def"],      "3pcs":"Bonus de ×0.25 de ressources.",                                                               "4pcs":["p_def"],     "5pcs":["hp"],         "6pcs":["p_atk"],      "7pcs":"Bonus de ×0.5 de ressources."},
    "paladin_donjon_abyssal":    {cls:"Paladin", source:"donjon_abyssal",   name:"Bouclier de la Foi",       theme:"de la Foi",         "2pcs":["speed"],      "3pcs":"Bonus de ×0.5 de passif de classe.",                                                          "4pcs":["hp"],        "5pcs":["p_def"],      "6pcs":["p_atk"],      "7pcs":"Bonus de ×1.0 de passif de classe."},
    "paladin_raid":              {cls:"Paladin", source:"raid",             name:"Avatar Sacré",             theme:"de l'Avatar",       "2pcs":["hp"],         "3pcs":"1.5% de chance de te rendre immortel pendant 2 tours à la fin de ton tour.",                 "4pcs":["m_def"],     "5pcs":["p_def"],      "6pcs":["speed"],      "7pcs":"3% de chance de te rendre immortel pendant 2 tours à la fin de ton tour."},
  };

  // class + source → set key (match by cls+source)
  function findSetKey(cls, source) {
    return Object.keys(SET_BONUSES).find(k => SET_BONUSES[k].cls === cls && SET_BONUSES[k].source === source) || null;
  }

  /* ── Drop rarity keyframes (zone_rarity_weights from items.py) ── */
  const DROP_KEYFRAMES = [
    [   1, [65.0, 25.0,  8.0,  2.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0]],
    [ 500, [ 2.0,  8.0, 20.0, 35.0, 22.0,  8.0,  2.8,  1.3,  0.5,  0.4]],
    [1000, [ 0.0,  0.0,  0.0,  3.0, 12.0, 22.0, 30.0, 20.0,  8.0,  5.0]],
    [2000, [ 0.0,  0.0,  0.0,  1.5,  6.0, 13.0, 22.0, 25.0, 20.0, 12.5]],
    [3000, [ 0.0,  0.0,  0.0,  0.0,  0.0,  4.0, 14.0, 30.0, 32.0, 20.0]],
  ];
  const DROP_ZONE_BONUS = { monde:0, donjon_classique:200, donjon_elite:500, donjon_abyssal:1000 };
  // raid: +200 × level

  function dropWeights(zone, bonus) {
    const z = Math.min(Math.max(zone + bonus, 1), 3000);
    let w = DROP_KEYFRAMES[DROP_KEYFRAMES.length-1][1].slice();
    for (let i = 0; i < DROP_KEYFRAMES.length-1; i++) {
      const [z0,w0] = DROP_KEYFRAMES[i], [z1,w1] = DROP_KEYFRAMES[i+1];
      if (z0 <= z && z <= z1) { const t=(z-z0)/(z1-z0); w=w0.map((a,j)=>a+(w1[j]-a)*t); break; }
    }
    return w.map(v => Math.max(0.01, v));
  }

  /* ── Rarités UI ────────────────────────────────────────────── */
  const RARITIES = [
    {id:"commun",       label:"⬜ Commun",       color:"#9E9E9E"},
    {id:"peu commun",   label:"🟩 Peu Commun",   color:"#4CAF50"},
    {id:"rare",         label:"🟦 Rare",          color:"#2196F3"},
    {id:"épique",       label:"🟪 Épique",        color:"#9C27B0"},
    {id:"légendaire",   label:"🟧 Légendaire",    color:"#FF9800"},
    {id:"mythique",     label:"🟥 Mythique",      color:"#F44336"},
    {id:"artefact",     label:"🔶 Artefact",      color:"#FF5722"},
    {id:"divin",        label:"🌟 Divin",         color:"#FFD700"},
    {id:"transcendant", label:"💠 Transcendant",  color:"#00BCD4"},
    {id:"prismatique",  label:"🌈 Prismatique",   color:"#E91E63"},
  ];
  const SLOTS_LIST = ["casque","plastron","pantalon","chaussures","arme","amulette","anneau"];
  const SLOT_EMOJI = {casque:"⛑️",plastron:"🦺",pantalon:"👖",chaussures:"👟",arme:"⚔️",amulette:"📿",anneau:"💍"};
  const SOURCES = [
    {id:"monde",           label:"🌍 Monde"},
    {id:"donjon_classique",label:"🏰 Donjon Classique"},
    {id:"donjon_elite",    label:"⚔️ Donjon Élite"},
    {id:"donjon_abyssal",  label:"🌑 Donjon Abyssal"},
    {id:"raid",            label:"👑 Raid"},
    {id:"craft",           label:"⚒️ Craft"},
  ];
  const STAT_LABELS = {hp:"❤️ Points de Vie",p_atk:"⚔️ Attaque Physique",m_atk:"✨ Attaque Magique",p_pen:"🗡️ Pénétration Physique",m_pen:"💫 Pénétration Magique",p_def:"🛡️ Défense Physique",m_def:"🔮 Défense Magique",speed:"💨 Vitesse",crit_chance:"🎯 Chance Critique",crit_damage:"💥 Dégâts Critiques"};
  const STAT_ORDER = ["hp","p_atk","m_atk","p_pen","m_pen","p_def","m_def","speed","crit_chance","crit_damage"];

  /* ── État ──────────────────────────────────────────────────── */
  let equipped = {}; // slot → {slot,cls,level,source,craftTier,rarity,forge,stats,setKey}

  function fmtStat(k, v) {
    if (k === "crit_chance") return v.toFixed(1)+"%";
    if (k === "crit_damage") return "+"+(100+v).toFixed(1)+"%";
    return Math.round(v).toLocaleString("fr-FR");
  }
  function statsBlock(stats) {
    const lines = STAT_ORDER.filter(k => (stats[k]||0) > 0)
      .map(k => `<div class="eq-stat-line">${STAT_LABELS[k]||k} <strong>${fmtStat(k, stats[k])}</strong></div>`);
    return lines.length ? lines.join("") : `<div style="opacity:.4">—</div>`;
  }
  function itemName(slot, cls, source, craftTier) {
    const prefix = (SLOT_PREFIX[cls]||{})[slot] || slot;
    const sk = findSetKey(cls, source);
    const theme = sk ? SET_BONUSES[sk].theme : (source === "craft" ? `(T${craftTier})` : "");
    return `${prefix} ${theme}`;
  }

  /* ── Render : Constructeur ─────────────────────────────────── */
  function renderBuilder() {
    const wrap = document.getElementById("eq-builder");
    if (!wrap || wrap.dataset.init) return;
    wrap.dataset.init = "1";

    // Source → show/hide craft tier
    const srcSel = document.getElementById("eq-source");
    const craftRow = document.getElementById("eq-craft-row");
    if (srcSel && craftRow) {
      srcSel.addEventListener("change", () => {
        craftRow.style.display = srcSel.value === "craft" ? "" : "none";
      });
    }

    // Add button
    const addBtn = document.getElementById("eq-add-btn");
    if (addBtn) addBtn.addEventListener("click", addItem);

    // Preview on input change
    ["eq-slot","eq-class","eq-level","eq-source","eq-craft-tier","eq-rarity","eq-forge"].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.addEventListener("change", renderPreview);
      if (el) el.addEventListener("input",  renderPreview);
    });
    renderPreview();
  }

  function getBuilderValues() {
    const g = id => document.getElementById(id);
    return {
      slot:      (g("eq-slot")       ||{}).value || "casque",
      cls:       (g("eq-class")      ||{}).value || "Guerrier",
      level:     Math.max(1, Math.min(1000, parseInt((g("eq-level")||{}).value)||1)),
      source:    (g("eq-source")     ||{}).value || "monde",
      craftTier: Math.max(1, Math.min(10,  parseInt((g("eq-craft-tier")||{}).value)||1)),
      rarity:    (g("eq-rarity")     ||{}).value || "commun",
      forge:     Math.max(0, Math.min(10,  parseInt((g("eq-forge")||{}).value)||0)),
    };
  }

  function renderPreview() {
    const v = getBuilderValues();
    const stats = computeItemStats(v.slot, v.cls, v.level, v.source, v.craftTier, v.rarity, v.forge);
    const el = document.getElementById("eq-preview");
    if (!el) return;
    const name = itemName(v.slot, v.cls, v.source, v.craftTier);
    const src = SOURCES.find(s=>s.id===v.source);
    const rar = RARITIES.find(r=>r.id===v.rarity);
    el.innerHTML = `<div class="eq-preview-header">${SLOT_EMOJI[v.slot]||""} <strong>${name}</strong> — ${rar?rar.label:""} ${src?src.label:""} niv.${v.level} +${v.forge}</div>${statsBlock(stats)}`;
  }

  function addItem() {
    const v = getBuilderValues();
    const stats = computeItemStats(v.slot, v.cls, v.level, v.source, v.craftTier, v.rarity, v.forge);
    equipped[v.slot] = { ...v, stats, setKey: findSetKey(v.cls, v.source) };
    renderEquipped();
  }

  /* ── Render : Équipement test ──────────────────────────────── */
  function renderEquipped() {
    const tbody = document.getElementById("eq-test-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    // Totaux
    const total = {};
    Object.values(equipped).forEach(eq => {
      Object.entries(eq.stats).forEach(([k,v]) => { total[k] = (total[k]||0) + v; });
    });

    // Bonus panoplie
    const setCount = {};
    const setMinLevel = {};
    const setMinRarity = {};
    const RARITY_ORDER = ["commun","peu commun","rare","épique","légendaire","mythique","artefact","divin","transcendant","prismatique"];
    Object.values(equipped).forEach(eq => {
      if (!eq.setKey) return;
      setCount[eq.setKey]    = (setCount[eq.setKey]||0) + 1;
      if (setMinLevel[eq.setKey] === undefined || eq.level < setMinLevel[eq.setKey]) setMinLevel[eq.setKey] = eq.level;
      const ri = RARITY_ORDER.indexOf(eq.rarity);
      if (setMinRarity[eq.setKey] === undefined || ri < setMinRarity[eq.setKey]) setMinRarity[eq.setKey] = ri;
    });

    const setBonus = {};
    const setPassives = [];
    const TIER_MULT = {"2pcs":0.125,"4pcs":0.25,"5pcs":0.375,"6pcs":0.50};
    Object.entries(setCount).forEach(([sk, cnt]) => {
      const sd = SET_BONUSES[sk]; if (!sd) return;
      const lvl = setMinLevel[sk] || 1;
      const rMult = RARITY_MULT[RARITY_ORDER[setMinRarity[sk]||0]] || 1.0;
      [["2pcs",2],["4pcs",4],["5pcs",5],["6pcs",6]].forEach(([tier,thr]) => {
        if (cnt >= thr && sd[tier]) {
          sd[tier].forEach(stat => {
            const base = statAt(sd.cls, stat, lvl);
            const flat = base * rMult * TIER_MULT[tier];
            setBonus[stat] = (setBonus[stat]||0) + flat;
          });
        }
      });
      [["3pcs",3],["7pcs",7]].forEach(([tier,thr]) => {
        if (cnt >= thr && sd[tier]) setPassives.push(`[${sd.name} ${cnt}/${cnt>=7?7:thr}pcs] ${sd[tier]}`);
      });
    });

    // Lignes équipement
    SLOTS_LIST.forEach(slot => {
      const eq = equipped[slot];
      const tr = document.createElement("tr");
      if (eq) {
        const name = itemName(slot, eq.cls, eq.source, eq.craftTier);
        const rar  = RARITIES.find(r=>r.id===eq.rarity);
        tr.innerHTML = `
          <td>${SLOT_EMOJI[slot]||""} ${slot}</td>
          <td style="color:${rar?rar.color:'inherit'}">${name} <small style="opacity:.6">niv.${eq.level} +${eq.forge}</small></td>
          <td>${statsBlock(eq.stats)}</td>
          <td><button class="eq-del-btn" data-slot="${slot}">×</button></td>`;
      } else {
        tr.innerHTML = `<td>${SLOT_EMOJI[slot]||""} ${slot}</td><td style="opacity:.35">—</td><td></td><td></td>`;
        tr.style.opacity = ".5";
      }
      tbody.appendChild(tr);
    });

    // Totals section below table
    const hasSomething = Object.keys(equipped).length > 0;
    const totalsEl = document.getElementById("eq-totals");
    if (totalsEl) {
      if (!hasSomething) { totalsEl.innerHTML = ""; }
      else {
        let html = '<div class="eq-totals-section">';

        // Part 1 — cumul items
        const statLines = STAT_ORDER.filter(k => (total[k]||0) > 0);
        if (statLines.length) {
          html += `<div class="eq-totals-group"><div class="eq-totals-title">Cumul des items (${Object.keys(equipped).length}/7 slots)</div>`;
          statLines.forEach(k => { html += `<div class="eq-stat-line">${STAT_LABELS[k]||k} <strong>${fmtStat(k, total[k])}</strong></div>`; });
          html += '</div>';
        }

        // Part 2 — bonus panoplie par stat
        const bonusStatLines = STAT_ORDER.filter(k => (setBonus[k]||0) > 0);
        if (bonusStatLines.length) {
          html += '<div class="eq-totals-group"><div class="eq-totals-title">Bonus panoplie</div>';
          bonusStatLines.forEach(k => { html += `<div class="eq-stat-line eq-bonus-stat-line">${STAT_LABELS[k]||k} <strong>+${fmtStat(k, setBonus[k])}</strong></div>`; });
          html += '</div>';
        }

        // Part 3 — passifs spéciaux
        if (setPassives.length) {
          html += '<div class="eq-totals-group"><div class="eq-totals-title">Passifs spéciaux</div>';
          setPassives.forEach(p => { html += `<div class="eq-passive-line">🔮 ${p}</div>`; });
          html += '</div>';
        }

        html += '</div>';
        totalsEl.innerHTML = html;
      }
    }

    // Wire delete buttons
    tbody.querySelectorAll(".eq-del-btn").forEach(btn => {
      btn.addEventListener("click", () => { delete equipped[btn.dataset.slot]; renderEquipped(); });
    });
  }

  /* ── Render : Taux de drop ─────────────────────────────────── */
  function renderDropTable() {
    const srcSel  = document.getElementById("dr-source");
    const lvlInp  = document.getElementById("dr-level");
    const lvlLbl  = document.getElementById("dr-level-label");
    const tbody   = document.getElementById("dr-tbody");
    if (!srcSel || !lvlInp || !tbody) return;

    const source = srcSel.value;
    const level  = Math.max(1, Math.min(1000, parseInt(lvlInp.value)||1));
    lvlInp.value = level;

    // Zone effective
    let zone, bonus;
    if (source === "raid") {
      const rl = Math.max(1, Math.min(10, level));
      zone  = rl * 100; // approx zone for raid level r
      bonus = 200 * rl;
      if (lvlLbl) lvlLbl.textContent = "Niveau de raid (1–10)";
    } else {
      zone  = level;
      bonus = DROP_ZONE_BONUS[source] || 0;
      if (lvlLbl) lvlLbl.textContent = "Zone (1–1000)";
    }

    const weights = dropWeights(zone, bonus);
    const total   = weights.reduce((a,b)=>a+b, 0);
    tbody.innerHTML = "";
    weights.forEach((w, i) => {
      const pct = (w/total*100).toFixed(1);
      if (parseFloat(pct) < 0.1) return;
      const r = RARITIES[i];
      const bw = Math.round(parseFloat(pct));
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="color:${r.color}">${r.label}</td>
        <td><strong>${pct}%</strong></td>
        <td><div class="cc-bar"><div class="cc-bar-fill" style="width:${bw}%;background:${r.color}"></div></div></td>`;
      tbody.appendChild(tr);
    });
  }

  /* ── Browser de panoplie ───────────────────────────────────── */
  function initSetBrowser() {
    const CLASSES  = ["Guerrier","Assassin","Mage","Tireur","Support","Vampire","Gardien du Temps","Ombre Venin","Pyromancien","Paladin"];
    const SOURCES  = [
      {key:"monde",            label:"🌍 Monde"},
      {key:"donjon_classique", label:"🏰 Classique"},
      {key:"donjon_elite",     label:"⚔️ Élite"},
      {key:"donjon_abyssal",   label:"🌑 Abyssal"},
      {key:"raid",             label:"👑 Raid"},
      {key:"craft",            label:"⚒️ Craft"},
    ];
    const STAT_SHORT = {
      hp:"❤️ PV", p_atk:"⚔️ ATK Phys.", m_atk:"✨ ATK Mag.",
      p_pen:"🗡️ Pén. Phys.", m_pen:"💫 Pén. Mag.",
      p_def:"🛡️ Déf. Phys.", m_def:"🔮 Déf. Mag.",
      speed:"💨 Vitesse", crit_chance:"🎯 Crit. Chance", crit_damage:"💥 Crit. Dégâts",
    };

    const classTabs  = document.getElementById("set-class-tabs");
    const sourceTabs = document.getElementById("set-source-tabs");
    const tableWrap  = document.getElementById("set-table-wrap");
    if (!classTabs || !sourceTabs || !tableWrap) return;

    let selClass  = CLASSES[0];
    let selSource = "monde";

    function renderSourceTabs() {
      sourceTabs.innerHTML = "";
      SOURCES.forEach(s => {
        const btn = document.createElement("button");
        btn.className = "set-tab-btn" + (s.key === selSource ? " active" : "");
        btn.textContent = s.label;
        btn.addEventListener("click", () => { selSource = s.key; renderAll(); });
        sourceTabs.appendChild(btn);
      });
      sourceTabs.style.display = "";
    }

    function renderTable() {
      const setKey = findSetKey(selClass, selSource);
      if (!setKey) { tableWrap.innerHTML = '<p style="opacity:.5;padding:.5rem">Aucune panoplie trouvée.</p>'; return; }
      const d = SET_BONUSES[setKey];
      const rows = [
        {pcs:"2 pcs", content:(d["2pcs"]||[]).map(k=>STAT_SHORT[k]||k).join(", "), passive:false},
        {pcs:"3 pcs", content:d["3pcs"]||"—",                                       passive:true,  tier:"D"},
        {pcs:"4 pcs", content:(d["4pcs"]||[]).map(k=>STAT_SHORT[k]||k).join(", "), passive:false},
        {pcs:"5 pcs", content:(d["5pcs"]||[]).map(k=>STAT_SHORT[k]||k).join(", "), passive:false},
        {pcs:"6 pcs", content:(d["6pcs"]||[]).map(k=>STAT_SHORT[k]||k).join(", "), passive:false},
        {pcs:"7 pcs", content:d["7pcs"]||"—",                                       passive:true,  tier:"C"},
      ];
      let html = `<div class="set-name-badge">${d.name}</div>`;
      html += '<table class="cc-table" style="margin-top:.6rem"><thead><tr><th>Pièces</th><th>Bonus</th></tr></thead><tbody>';
      rows.forEach(r => {
        if (r.passive) {
          html += `<tr class="set-passive-row"><td><strong>${r.pcs}</strong> <span class="set-tier set-tier-${r.tier}">Tier ${r.tier}</span></td><td>🔮 ${r.content}</td></tr>`;
        } else {
          html += `<tr><td>${r.pcs}</td><td>${r.content}</td></tr>`;
        }
      });
      html += '</tbody></table>';
      tableWrap.innerHTML = html;
    }

    function renderAll() {
      classTabs.querySelectorAll(".set-tab-btn").forEach(b => b.classList.toggle("active", b.dataset.cls === selClass));
      renderSourceTabs();
      renderTable();
    }

    CLASSES.forEach(cls => {
      const btn = document.createElement("button");
      btn.className = "set-tab-btn" + (cls === selClass ? " active" : "");
      btn.textContent = cls;
      btn.dataset.cls = cls;
      btn.addEventListener("click", () => { selClass = cls; renderAll(); });
      classTabs.appendChild(btn);
    });

    renderAll();
  }

  /* ── Init ──────────────────────────────────────────────────── */
  function init() {
    renderBuilder();
    renderEquipped();

    const srcSel = document.getElementById("dr-source");
    const lvlInp = document.getElementById("dr-level");
    if (srcSel) srcSel.addEventListener("change", renderDropTable);
    if (lvlInp) lvlInp.addEventListener("input",  renderDropTable);
    renderDropTable();
    initSetBrowser();
  }

  if (typeof document$ !== "undefined") document$.subscribe(init);
  else document.addEventListener("DOMContentLoaded", init);

})();
