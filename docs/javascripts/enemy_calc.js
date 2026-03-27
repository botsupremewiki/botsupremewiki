/* ============================================================
   Simulateur d'Ennemis — Bot Suprême Wiki
   Reproduit fidèlement la logique de enemies.py + models.py
   ============================================================ */
(function () {
  'use strict';

  // ─── Données statiques ────────────────────────────────────────────────────

  var ALL_CLASSES = [
    'Guerrier','Assassin','Mage','Tireur','Support',
    'Vampire','Gardien du Temps','Ombre Venin','Pyromancien','Paladin'
  ];

  var CLASS_EMOJI = {
    'Guerrier':'⚔️','Assassin':'🗡️','Mage':'🔮','Tireur':'🏹','Support':'💚',
    'Vampire':'🧛','Gardien du Temps':'⏳','Ombre Venin':'☠️','Pyromancien':'🔥',
    'Paladin':'🛡️','Titan':'🐉'
  };

  var ZONE_THEMES = [
    ['Plaine Verdoyante','🌿'],['Forêt Ombreuse','🌲'],['Marais Pestilentiel','🌫️'],
    ['Désert Ardent','🏜️'],['Toundra Glacée','❄️'],['Volcans Ardents','🌋'],
    ['Cités en Ruines','🏚️'],['Abysses Marines','🌊'],['Nécropole Maudite','💀'],
    ['Royaume Céleste','☁️']
  ];

  var ENEMY_FIRST = {
    'Guerrier':'Berserker','Assassin':'Rôdeur','Mage':'Sorcier','Tireur':'Archer Maudit',
    'Support':'Chaman Vénéneux','Vampire':'Vampire Ancien','Gardien du Temps':'Chronomancien',
    'Ombre Venin':'Araignée Toxique','Pyromancien':'Élémentaire de Feu','Paladin':'Croisé Déchu'
  };

  var EMBLEMATIC_NAMES = [
    "Malachar l'Éternel","Zephyros le Tempétueux","Mordreth la Dévoreuse",
    "Xanathos l'Omniscient","Valdris l'Implacable","Sylvara la Tisseuse",
    "Grudnak le Colossal","Elysia la Corrompue","Tharax le Venimeux",
    "Drakonus le Chromate","Abyssion le Profond","Ignaris le Volcanique",
    "Glacialis le Glaçant","Umbrath l'Ombral","Pyrion l'Incandescent",
    "Temporis le Figé","Necrosis la Putride","Aetherion l'Astral",
    "Tenebris le Ténébreux","Primordius l'Ancestral"
  ];

  var ANTIQUE_NAMES = [
    "Vrethax le Primordial","Azkoth la Conscience Noire","Solarius le Dévoreur d'Étoiles",
    "Mortifax l'Impérissable","Chronaxis le Maître Absolu","Nexuvor l'Indicible",
    "Erebos la Nuit Éternelle","Pantheos le Dieu-Bête","Ultharak l'Abomination",
    "Omegaris la Fin du Monde"
  ];

  // ─── Stats de base — models.py BASE_STATS ─────────────────────────────────

  var BASE_STATS = {
    'Guerrier':         {hp:600,  p_atk:57,  m_atk:0,   p_pen:8,  m_pen:0,  p_def:28, m_def:6,  speed:80,  crit_chance:5.0,  crit_damage:150.0},
    'Assassin':         {hp:500,  p_atk:50,  m_atk:0,   p_pen:10, m_pen:0,  p_def:4,  m_def:3,  speed:160, crit_chance:20.0, crit_damage:175.0},
    'Mage':             {hp:400,  p_atk:0,   m_atk:38,  p_pen:0,  m_pen:8,  p_def:3,  m_def:10, speed:90,  crit_chance:12.0, crit_damage:175.0},
    'Tireur':           {hp:440,  p_atk:44,  m_atk:0,   p_pen:8,  m_pen:0,  p_def:4,  m_def:4,  speed:130, crit_chance:18.0, crit_damage:175.0},
    'Support':          {hp:650,  p_atk:48,  m_atk:48,  p_pen:6,  m_pen:6,  p_def:25, m_def:25, speed:80,  crit_chance:5.0,  crit_damage:140.0},
    'Vampire':          {hp:450,  p_atk:45,  m_atk:0,   p_pen:9,  m_pen:0,  p_def:12, m_def:7,  speed:90,  crit_chance:15.0, crit_damage:175.0},
    'Gardien du Temps': {hp:480,  p_atk:35,  m_atk:35,  p_pen:6,  m_pen:6,  p_def:18, m_def:18, speed:100, crit_chance:8.0,  crit_damage:155.0},
    'Ombre Venin':      {hp:370,  p_atk:30,  m_atk:15,  p_pen:6,  m_pen:3,  p_def:5,  m_def:5,  speed:115, crit_chance:17.0, crit_damage:170.0},
    'Pyromancien':      {hp:420,  p_atk:0,   m_atk:43,  p_pen:0,  m_pen:9,  p_def:2,  m_def:10, speed:85,  crit_chance:13.0, crit_damage:175.0},
    'Paladin':          {hp:560,  p_atk:42,  m_atk:0,   p_pen:8,  m_pen:0,  p_def:35, m_def:22, speed:72,  crit_chance:5.0,  crit_damage:150.0}
  };

  // ─── Croissance par niveau — models.py LEVEL_GROWTH ──────────────────────

  var LEVEL_GROWTH = {
    'Guerrier':         {hp:35.45, p_atk:2.986, m_atk:0.0,   p_pen:0.632, m_pen:0.0,   p_def:0.572, m_def:0.114, speed:0.195, crit_chance:0.007, crit_damage:0.015},
    'Assassin':         {hp:39.54, p_atk:2.953, m_atk:0.0,   p_pen:0.591, m_pen:0.0,   p_def:0.076, m_def:0.047, speed:0.340, crit_chance:0.010, crit_damage:0.025},
    'Mage':             {hp:34.64, p_atk:0.0,   m_atk:2.339, p_pen:0.0,   m_pen:0.492, p_def:0.047, m_def:0.190, speed:0.260, crit_chance:0.016, crit_damage:0.020},
    'Tireur':           {hp:37.60, p_atk:2.760, m_atk:0.0,   p_pen:0.552, m_pen:0.0,   p_def:0.076, m_def:0.076, speed:0.270, crit_chance:0.014, crit_damage:0.020},
    'Support':          {hp:64.46, p_atk:2.168, m_atk:2.168, p_pen:0.434, m_pen:0.434, p_def:0.475, m_def:0.475, speed:0.195, crit_chance:0.003, crit_damage:0.010},
    'Vampire':          {hp:39.59, p_atk:2.758, m_atk:0.0,   p_pen:0.551, m_pen:0.0,   p_def:0.188, m_def:0.113, speed:0.260, crit_chance:0.007, crit_damage:0.020},
    'Gardien du Temps': {hp:37.64, p_atk:1.480, m_atk:1.480, p_pen:0.296, m_pen:0.296, p_def:0.335, m_def:0.335, speed:0.245, crit_chance:0.010, crit_damage:0.015},
    'Ombre Venin':      {hp:43.74, p_atk:2.172, m_atk:1.487, p_pen:0.434, m_pen:0.210, p_def:0.075, m_def:0.075, speed:0.300, crit_chance:0.008, crit_damage:0.015},
    'Pyromancien':      {hp:41.60, p_atk:0.0,   m_atk:2.647, p_pen:0.0,   m_pen:0.529, p_def:0.048, m_def:0.190, speed:0.245, crit_chance:0.013, crit_damage:0.020},
    'Paladin':          {hp:54.50, p_atk:2.973, m_atk:0.0,   p_pen:0.594, m_pen:0.0,   p_def:0.665, m_def:0.429, speed:0.195, crit_chance:0.003, crit_damage:0.005}
  };

  var STAT_KEYS = ['hp','p_atk','m_atk','p_pen','m_pen','p_def','m_def','speed','crit_chance','crit_damage'];

  // ─── Passifs par classe — enemies.py ─────────────────────────────────────

  var RUNIC_PASSIFS = {
    'Guerrier':         "Furie Mineure : +3% dégâts par tranche de 25% HP perdus (max +12%)",
    'Assassin':         "Réflexes : 5% de chance d'esquiver une attaque physique",
    'Mage':             "Résonance Arcanique : ignore 8% de ta Déf. Mag.",
    'Tireur':           "Visée Précise : +8% chance de critique",
    'Support':          "Régénération : récupère 0.5% HP max au début de chaque tour",
    'Vampire':          "Siphon Mineur : récupère 5% des dégâts infligés en HP",
    'Gardien du Temps': "Distorsion Légère : ta vitesse réduite de 5%",
    'Ombre Venin':      "Glandes Actives : 10% de chance de poison additionnel à chaque attaque",
    'Pyromancien':      "Braises : 20% de chance d'appliquer 1 stack de brûlure à chaque attaque",
    'Paladin':          "Résistance : dégâts reçus réduits de 5%"
  };

  var EMBLEMATIC_PASSIFS = {
    'Guerrier':         "Furie Guerrière : +5% dégâts par tranche de 25% HP perdus (max +20%)",
    'Assassin':         "Instinct : 10% de chance d'esquiver une attaque physique",
    'Mage':             "Voile Arcanique : ignore 12% de ta Déf. Mag.",
    'Tireur':           "Œil Affûté : +12% chance de critique",
    'Support':          "Régénération Active : récupère 1% HP max/tour",
    'Vampire':          "Siphon de Vie : récupère 8% des dégâts infligés",
    'Gardien du Temps': "Ralentissement : ta vitesse réduite de 10%",
    'Ombre Venin':      "Venin Persistant : 15% de chance de poison additionnel à chaque attaque",
    'Pyromancien':      "Embrasement : 30% de chance d'appliquer 1 stack de brûlure à chaque attaque",
    'Paladin':          "Aura Défensive : dégâts reçus réduits de 8%"
  };

  var ANTIQUE_PASSIFS = {
    'Guerrier':         "Rage Ancienne : +8% dégâts par 25% HP perdus (max +32%) + immunité aux stuns",
    'Assassin':         "Ombre Persistante : 15% esquive + ses critiques ignorent 15% de ta Déf. Phy.",
    'Mage':             "Annihilation Partielle : ignore 20% de ta Déf. Mag. + tous les 5 tours : dégâts purs 10% HP max",
    'Tireur':           "Salve Précise : +18% chance de critique + tes défenses physiques -10%",
    'Support':          "Bastion : récupère 1.5% HP max/tour + dégâts reçus -10%",
    'Vampire':          "Avidité Sanguine : récupère 12% des dégâts infligés + te vole 1% HP max/tour",
    'Gardien du Temps': "Distorsion Temporelle : ta vitesse -15%, sa vitesse +15%",
    'Ombre Venin':      "Nuée Venimeuse : 20% de chance de poison additionnel + dégâts DoT ×1.2",
    'Pyromancien':      "Combustion : 40% de chance d'appliquer 1 stack de brûlure + dégâts brûlure ×1.2",
    'Paladin':          "Jugement : dégâts reçus -12% + tous les 5 tours : dégâts purs 8% HP max"
  };

  // ─── Donjons (7 boss par slot d'équipement) ───────────────────────────────

  var DUNGEON_BOSSES = [
    {id:'d_casque',     name:'Gardien des Crânes',  emoji:'🪖', boost:'p_def',       passif:'Protection Céphalique : réduit les dégâts critiques reçus de 20%.'},
    {id:'d_plastron',   name:'Titan Cuirassé',       emoji:'🛡️', boost:'hp',          passif:'Endurance Absolue : récupère 3% de ses HP max au début de chaque tour.'},
    {id:'d_pantalon',   name:'Danseur de Guerre',    emoji:'🌪️', boost:'speed',       passif:"Esquive Naturelle : 10% de chance d'éviter complètement une attaque."},
    {id:'d_chaussures', name:'Spectre Fulgurant',    emoji:'⚡', boost:'speed',       passif:"Foulée Redoublée : 20% de chance d'attaquer deux fois lors de son tour."},
    {id:'d_arme',       name:'Lame Dévastatrice',    emoji:'⚔️', boost:'p_atk',       passif:'Tranchant Absolu : ignore 20% de ta Défense Physique et 20% de ta Défense Magique.'},
    {id:'d_amulette',   name:'Mystique Absolu',      emoji:'📿', boost:'m_atk',       passif:'Renvoi Mystique : renvoie 8% des dégâts reçus sous forme de dégâts purs (avant défense).'},
    {id:'d_anneau',     name:'Catalyseur Éternel',   emoji:'💍', boost:'crit_chance', passif:'Empowerment Runique : gagne +2.5% dégâts par tour (cumulé, max 10 fois, +25% au maximum).'}
  ];

  // ─── Raids (noms et classes corrects — enemies.py RAID_BOSSES) ───────────

  var RAID_BOSSES_DATA = [
    {id:'raid_1',  name:"Vorgath l'Implacable",    emoji:'🐉', level:1,  req:100,  cls:'Guerrier'},
    {id:'raid_2',  name:"Shivra l'Ombre Mortelle", emoji:'🗡️', level:2,  req:200,  cls:'Assassin'},
    {id:'raid_3',  name:"Zyrex l'Archmage",        emoji:'⚡', level:3,  req:300,  cls:'Mage'},
    {id:'raid_4',  name:"Karek le Chasseur",        emoji:'🏹', level:4,  req:400,  cls:'Tireur'},
    {id:'raid_5',  name:"Serath le Corrupteur",     emoji:'🕸️', level:5,  req:500,  cls:'Support'},
    {id:'raid_6',  name:"Mordas le Sans-Âme",       emoji:'🧛', level:6,  req:600,  cls:'Vampire'},
    {id:'raid_7',  name:"Chronovex l'Invariant",    emoji:'⏳', level:7,  req:700,  cls:'Gardien du Temps'},
    {id:'raid_8',  name:"Nyxara la Corrompue",      emoji:'🐍', level:8,  req:800,  cls:'Ombre Venin'},
    {id:'raid_9',  name:"Ignareth le Phénix",       emoji:'🔥', level:9,  req:900,  cls:'Pyromancien'},
    {id:'raid_10', name:"Omnifax le Divin",         emoji:'🌑', level:10, req:1000, cls:'Paladin'}
  ];

  // ─── Formule de calcul — enemies.py compute_enemy_stats ──────────────────

  function computeEnemyStats(level, cls) {
    level = Math.max(1, level);
    var pct = 0.3 + 0.7 * (level - 1) / 9999;
    var resolved = BASE_STATS[cls] ? cls : 'Guerrier';
    var base   = BASE_STATS[resolved];
    var growth = LEVEL_GROWTH[resolved] || LEVEL_GROWTH['Guerrier'];
    var stats  = {};
    STAT_KEYS.forEach(function(stat) {
      var playerVal = (base[stat] || 0) + (growth[stat] || 0) * (level - 1);
      if (stat === 'crit_chance' || stat === 'crit_damage') {
        stats[stat] = Math.round(playerVal * pct * 100) / 100;
      } else {
        stats[stat] = Math.floor(playerVal * pct);
      }
    });
    return stats;
  }

  function computeEnemyStatsAvg(level) {
    var allStats = ALL_CLASSES.map(function(c) { return computeEnemyStats(level, c); });
    var r = {};
    STAT_KEYS.forEach(function(k) {
      var sum = allStats.reduce(function(s, st) { return s + st[k]; }, 0);
      if (k === 'crit_chance' || k === 'crit_damage') {
        r[k] = Math.round(sum / allStats.length * 100) / 100;
      } else {
        r[k] = Math.floor(sum / allStats.length);
      }
    });
    return r;
  }

  function classForIndex(n) {
    return ALL_CLASSES[((n % 10) + 10) % 10];
  }

  function getTheme(zone) {
    return ZONE_THEMES[Math.floor((zone - 1) / 1000) % ZONE_THEMES.length];
  }

  // ── Monde : ennemis normaux ────────────────────────────────────────────────

  function calcMondeEnemy(zone, stage) {
    var cls   = ALL_CLASSES[(stage - 1) % ALL_CLASSES.length];
    var stats = computeEnemyStats(zone, cls);
    var th    = getTheme(zone);
    return {
      name: ENEMY_FIRST[cls] || cls,
      nameNote: 'Le nom exact varie à chaque combat',
      cls: cls, theme: th[0], themeEmoji: th[1],
      typeLabel: 'Stage ' + stage, typeBadge: 'Monde', typeEmoji: '👿',
      passif: null,
      xp:   Math.max(1, Math.floor(zone * 15) + stage),
      gold: Math.max(1, Math.floor(zone * 8)  + stage),
      drops: '10% : 1 item (ta classe) · 1% : 1 item (autre classe) — Panoplie Monde, slot aléatoire',
      matZone: zone,
      stats: stats
    };
  }

  // ── Monde : boss classique ─────────────────────────────────────────────────

  function calcMondeBossClassique(zone) {
    var cls   = classForIndex(zone - 1);
    var stats = computeEnemyStats(zone, cls);
    stats.hp  = Math.floor(stats.hp * 1.2);
    var th    = getTheme(zone);
    return {
      name: '[Préfixe aléatoire] ' + (ENEMY_FIRST[cls] || cls),
      nameNote: 'Le nom exact varie à chaque combat',
      cls: cls, theme: th[0], themeEmoji: th[1],
      typeLabel: 'Boss de Zone', typeBadge: 'Boss Zone', typeEmoji: '⚔️',
      passif: null,
      xp:   Math.max(3,  Math.floor(zone * 18)),
      gold: Math.max(2,  Math.floor(zone * 10)),
      drops: '50% : 1 item (ta classe) · 10% : 1 item (autre classe) — Panoplie Monde, slot aléatoire',
      matZone: zone,
      stats: stats
    };
  }

  // ── Monde : boss runique (toutes les 10 zones, sauf emblématiques/antiques)

  function calcRunicBoss(zone) {
    var cls   = classForIndex(Math.floor(zone / 10) - 1);
    var stats = computeEnemyStats(zone, cls);
    stats.hp  = Math.floor(stats.hp * 1.5);
    var th    = getTheme(zone);
    return {
      name: '[Préfixe aléatoire] ' + (ENEMY_FIRST[cls] || cls),
      nameNote: 'Le nom exact varie à chaque combat',
      cls: cls, theme: th[0], themeEmoji: '🔮',
      typeLabel: 'Boss Runique', typeBadge: 'Runique', typeEmoji: '🔮',
      passif: RUNIC_PASSIFS[cls] || null,
      xp:   Math.max(5,  Math.floor(zone * 23)),
      gold: Math.max(3,  Math.floor(zone * 12)),
      drops: '50% : 1 item (ta classe) · 10% : 1 item (autre classe) — Panoplie Monde, slot aléatoire',
      matZone: zone,
      stats: stats
    };
  }

  // ── Monde : boss emblématique (toutes les 100 zones, sauf antiques) ────────

  function calcEmblematique(zone, clsOverride) {
    var idx     = Math.floor(zone / 100) - 1;
    var autoCls = classForIndex(idx);
    var cls     = clsOverride || autoCls;
    var stats   = computeEnemyStats(zone, cls);
    stats.hp    = Math.floor(stats.hp * 2);
    return {
      name: EMBLEMATIC_NAMES[idx % EMBLEMATIC_NAMES.length],
      nameNote: null,
      cls: cls, theme: 'Boss Emblématique', themeEmoji: '🌟',
      typeLabel: 'Boss Emblématique', typeBadge: 'Emblématique', typeEmoji: '🌟',
      passif: EMBLEMATIC_PASSIFS[cls] || null,
      xp:   Math.max(50,  Math.floor(zone * 30)),
      gold: Math.max(30,  Math.floor(zone * 16)),
      drops: '100% : 1 item (ta classe) + 50% : 1 item (autre classe) — Panoplie Monde, slot aléatoire',
      matZone: zone,
      stats: stats
    };
  }

  // ── Monde : boss antique (toutes les 1000 zones, dont zone 10 000) ─────────

  function calcAntique(zone, clsOverride) {
    var idx     = Math.floor(zone / 1000) - 1;
    var autoCls = classForIndex(idx);
    var cls     = clsOverride || autoCls;
    var stats   = computeEnemyStats(zone, cls);
    stats.hp    = Math.floor(stats.hp * 3);
    return {
      name: ANTIQUE_NAMES[idx % ANTIQUE_NAMES.length],
      nameNote: null,
      cls: cls, theme: 'Boss Antique', themeEmoji: '⚠️',
      typeLabel: 'Boss Antique', typeBadge: 'Antique', typeEmoji: '⚠️',
      passif: ANTIQUE_PASSIFS[cls] || null,
      xp:   Math.max(200, Math.floor(zone * 45)),
      gold: Math.max(100, Math.floor(zone * 24)),
      drops: '3× items (ta classe, garantis) + 1× item (autre classe, garanti) — Panoplie Monde, slot aléatoire',
      matZone: zone,
      stats: stats
    };
  }

  // ── Donjon ─────────────────────────────────────────────────────────────────

  function calcDonjon(bossId, difficulty, level) {
    var boss      = DUNGEON_BOSSES.filter(function(b){ return b.id === bossId; })[0] || DUNGEON_BOSSES[0];
    var offsets   = {classique:0, elite:3333, abyssal:6666};
    var zoneEquiv = (offsets[difficulty] || 0) + level * 33;
    var cls       = classForIndex(level - 1);
    var diffMult  = {classique:1.2, elite:1.4, abyssal:1.6}[difficulty] || 1.2;
    var rewardM   = {classique:2,   elite:3,   abyssal:4}[difficulty]   || 2;
    var diffLabel = {classique:'Classique', elite:'Élite', abyssal:'Abyssal'}[difficulty] || difficulty;

    var stats = computeEnemyStats(zoneEquiv, cls);
    STAT_KEYS.forEach(function(k) {
      if (k === 'crit_chance' || k === 'crit_damage') {
        stats[k] = Math.round(stats[k] * diffMult * 100) / 100;
      } else {
        stats[k] = Math.floor(stats[k] * diffMult);
      }
    });
    // Boost stat spéciale du boss ×diffMult supplémentaire
    if (boss.boost && stats[boss.boost] !== undefined) {
      if (boss.boost === 'crit_chance' || boss.boost === 'crit_damage') {
        stats[boss.boost] = Math.round(stats[boss.boost] * diffMult * 100) / 100;
      } else {
        stats[boss.boost] = Math.floor(stats[boss.boost] * diffMult);
      }
    }

    return {
      name: boss.name, nameNote: null,
      cls: cls,
      theme: 'Donjon ' + diffLabel + ' Niv.' + level, themeEmoji: boss.emoji,
      typeLabel: 'Donjon ' + diffLabel + ' — Niv.' + level,
      typeBadge: 'Donjon ' + diffLabel, typeEmoji: boss.emoji,
      passif: boss.passif, boostStat: boss.boost,
      xp:   Math.max(1, Math.floor(zoneEquiv * 15 * rewardM)),
      gold: Math.max(1, Math.floor(zoneEquiv * 8  * rewardM)),
      drops: '1 item garanti (slot : ' + boss.emoji + ' ' + boss.name + ') — 80% ta classe / 20% autre classe — Panoplie Donjon ' + diffLabel,
      matZone: zoneEquiv, matMult: diffMult,
      zoneEquiv: zoneEquiv,
      stats: stats
    };
  }

  // ── Raid ───────────────────────────────────────────────────────────────────

  function calcRaid(raidId) {
    var boss      = RAID_BOSSES_DATA.filter(function(b){ return b.id === raidId; })[0] || RAID_BOSSES_DATA[0];
    var zoneEquiv = boss.level * 1000;
    var stats     = computeEnemyStats(zoneEquiv, boss.cls);

    // ×2.5 toutes stats (combat 5 joueurs), puis HP ×4 supplémentaire → HP ×10 total
    STAT_KEYS.forEach(function(k) {
      if (k === 'crit_chance' || k === 'crit_damage') {
        stats[k] = Math.round(stats[k] * 2.5 * 100) / 100;
      } else {
        stats[k] = Math.floor(stats[k] * 2.5);
      }
    });
    stats.hp = Math.floor(stats.hp * 4);

    // raid_10 : stats offensives + défensives doublées (hors HP, vitesse, crit)
    if (raidId === 'raid_10') {
      ['p_atk','m_atk','p_pen','m_pen','p_def','m_def'].forEach(function(k) {
        stats[k] = Math.floor(stats[k] * 2);
      });
    }

    return {
      name: boss.name, nameNote: null,
      cls: boss.cls, theme: 'Raid', themeEmoji: boss.emoji,
      typeLabel: 'Raid ' + boss.level + ' — Niveau requis : ' + boss.req,
      typeBadge: 'Raid ' + boss.level, typeEmoji: boss.emoji,
      passif: null, req: boss.req,
      xp:   Math.floor(zoneEquiv * 150),
      gold: Math.floor(zoneEquiv * 50),
      drops: '7 items garantis (1 par slot) — classe totalement aléatoire — Panoplie Raid Niv. ' + boss.level,
      matZone: zoneEquiv, matMult: 9,
      stats: stats
    };
  }

  // ── World Boss ─────────────────────────────────────────────────────────────

  function calcWorldBoss(tourPersonnel) {
    // Tour 1 → turn=0 → zone 1000, Tour 2 → turn=1 → zone 1250, etc.
    var turn      = Math.max(0, tourPersonnel - 1);
    var zoneEquiv = Math.round(1000 * Math.pow(1.25, turn));
    var stats     = computeEnemyStatsAvg(zoneEquiv);
    delete stats.hp; // HP fixe hebdomadaire (collectif), non affiché ici
    return {
      name: 'Bot Suprême', nameNote: null,
      cls: 'Titan', theme: 'World Boss', themeEmoji: '🐉',
      typeLabel: 'Tour WB #' + tourPersonnel + ' — Zone ' + fmt(zoneEquiv),
      typeBadge: 'World Boss T' + tourPersonnel, typeEmoji: '🐉',
      passif: "Escalade ×1.25 : zone équivalente ×1.25 par attaque WB de la semaine. Tour 20 maximum — en cas de défaite, le tour repart à 1.",
      xp:   Math.floor(zoneEquiv * 500),
      gold: Math.floor(zoneEquiv * 200),
      drops: 'Récompenses hebdomadaires (classement) : 🥇 Prismatique +300 000g · 🥈 Transcendant +250 000g · 🥉 Divin +200 000g · Top 10 : Légendaire +150 000g · Top 50 : Épique +100 000g · Top 100 : Rare +75 000g · Tous les participants : Commun +50 000g',
      matZone: zoneEquiv,
      stats: stats
    };
  }

  // ─── Matériaux ────────────────────────────────────────────────────────────

  var MATERIALS_DATA = [
    {prof:'mineur',     tier:1,  name:'Minerai de Fer',        emoji:'🪨'},
    {prof:'mineur',     tier:2,  name:"Minerai d'Acier",       emoji:'⛏️'},
    {prof:'mineur',     tier:3,  name:'Minerai de Mithril',    emoji:'💎'},
    {prof:'mineur',     tier:4,  name:'Adamantium Brut',       emoji:'🔷'},
    {prof:'mineur',     tier:5,  name:'Pierre de Feu',         emoji:'🔥'},
    {prof:'mineur',     tier:6,  name:'Pierre de Glace',       emoji:'❄️'},
    {prof:'mineur',     tier:7,  name:'Orichalque',            emoji:'🟠'},
    {prof:'mineur',     tier:8,  name:'Pierre de Foudre',      emoji:'⚡'},
    {prof:'mineur',     tier:9,  name:'Cristal Brut',          emoji:'🔮'},
    {prof:'mineur',     tier:10, name:'Diamant Brut',          emoji:'💠'},
    {prof:'bucheron',   tier:1,  name:'Bois de Chêne',         emoji:'🌳'},
    {prof:'bucheron',   tier:2,  name:'Bois de Sapin',         emoji:'🌲'},
    {prof:'bucheron',   tier:3,  name:"Bois d'Ébène",          emoji:'🪵'},
    {prof:'bucheron',   tier:4,  name:'Bois de Teck',          emoji:'🪵'},
    {prof:'bucheron',   tier:5,  name:'Bois de Cèdre',         emoji:'🪵'},
    {prof:'bucheron',   tier:6,  name:'Bois Enchanté',         emoji:'✨'},
    {prof:'bucheron',   tier:7,  name:'Bois de Sang',          emoji:'🔴'},
    {prof:'bucheron',   tier:8,  name:'Bois de Lune',          emoji:'🌙'},
    {prof:'bucheron',   tier:9,  name:'Bois de Feu',           emoji:'🔥'},
    {prof:'bucheron',   tier:10, name:'Bois de Dragon',        emoji:'🐉'},
    {prof:'herboriste', tier:1,  name:'Herbe de Soin',         emoji:'🌿'},
    {prof:'herboriste', tier:2,  name:'Herbe de Mana',         emoji:'💧'},
    {prof:'herboriste', tier:3,  name:'Racine de Force',       emoji:'🌱'},
    {prof:'herboriste', tier:4,  name:'Fleur de Lune',         emoji:'🌸'},
    {prof:'herboriste', tier:5,  name:'Pollen Doré',           emoji:'🌼'},
    {prof:'herboriste', tier:6,  name:'Champignon Vénéneux',   emoji:'🍄'},
    {prof:'herboriste', tier:7,  name:'Cristal Végétal',       emoji:'🔮'},
    {prof:'herboriste', tier:8,  name:'Mousse Ancienne',       emoji:'🌾'},
    {prof:'herboriste', tier:9,  name:'Épine de Dragon',       emoji:'🌵'},
    {prof:'herboriste', tier:10, name:"Lotus de l'Ombre",      emoji:'🖤'},
    {prof:'chasseur',   tier:1,  name:'Cuir de Loup',          emoji:'🐺'},
    {prof:'chasseur',   tier:2,  name:'Cuir de Cerf',          emoji:'🦌'},
    {prof:'chasseur',   tier:3,  name:'Écailles de Serpent',   emoji:'🐍'},
    {prof:'chasseur',   tier:4,  name:'Plumes de Phénix',      emoji:'🦅'},
    {prof:'chasseur',   tier:5,  name:'Croc de Goule',         emoji:'🦷'},
    {prof:'chasseur',   tier:6,  name:'Griffe de Griffon',     emoji:'🦁'},
    {prof:'chasseur',   tier:7,  name:'Peau de Dragon',        emoji:'🐉'},
    {prof:'chasseur',   tier:8,  name:'Os de Chimère',         emoji:'💀'},
    {prof:'chasseur',   tier:9,  name:'Venin de Basilic',      emoji:'☠️'},
    {prof:'chasseur',   tier:10, name:'Cœur de Bête',          emoji:'❤️'},
    {prof:'fermier',    tier:1,  name:'Blé',                   emoji:'🌾'},
    {prof:'fermier',    tier:2,  name:'Orge',                  emoji:'🌾'},
    {prof:'fermier',    tier:3,  name:'Farine de Maïs',        emoji:'🌽'},
    {prof:'fermier',    tier:4,  name:'Herbes Aromatiques',    emoji:'🌿'},
    {prof:'fermier',    tier:5,  name:'Baies Sauvages',        emoji:'🫐'},
    {prof:'fermier',    tier:6,  name:'Lait de Licorne',       emoji:'🦄'},
    {prof:'fermier',    tier:7,  name:'Miel Enchanté',         emoji:'🍯'},
    {prof:'fermier',    tier:8,  name:'Sel de Mer',            emoji:'🧂'},
    {prof:'fermier',    tier:9,  name:'Épices Rares',          emoji:'🌶️'},
    {prof:'fermier',    tier:10, name:'Fruit du Paradis',      emoji:'🍑'}
  ];

  var PROF_LABELS = {
    mineur:'⛏️ Mineur', bucheron:'🪓 Bûcheron', herboriste:'🌿 Herboriste',
    chasseur:'🏹 Chasseur', fermier:'🌾 Fermier'
  };
  var PROF_ORDER = ['mineur','bucheron','herboriste','chasseur','fermier'];

  // ─── Affichage ───────────────────────────────────────────────────────────

  function fmt(n) {
    return Math.floor(n).toLocaleString('fr-FR');
  }

  var STAT_ORDER  = ['hp','p_atk','m_atk','p_def','m_def','p_pen','m_pen','speed','crit_chance','crit_damage'];
  var STAT_LABELS = {
    hp:'Points de Vie', p_atk:'Att. Physique', m_atk:'Att. Magique',
    p_def:'Déf. Physique', m_def:'Déf. Magique', p_pen:'Pén. Physique',
    m_pen:'Pén. Magique', speed:'Vitesse', crit_chance:'Critique', crit_damage:'Dég. Critique'
  };
  var STAT_EMOJIS = {
    hp:'❤️', p_atk:'⚔️', m_atk:'🔮', p_def:'🛡️', m_def:'🔷',
    p_pen:'🗡️', m_pen:'💫', speed:'⚡', crit_chance:'🎯', crit_damage:'💥'
  };

  function fmtChance(eff) {
    if (eff >= 100) {
      var g = Math.floor(eff / 100);
      var r = Math.round((eff % 100) * 10) / 10;
      return g + '× garanti' + (r > 0 ? ' +' + r + '%' : '');
    }
    return Math.round(eff * 10) / 10 + '%';
  }

  function renderMaterialDrops(zone, matMult) {
    matMult = matMult || 1;
    var zoneMult  = Math.round((1 + zone / 1000) * 100) / 100;
    var totalMult = Math.round(zoneMult * matMult * 100) / 100;
    // Index by prof
    var byProf = {};
    PROF_ORDER.forEach(function(p) { byProf[p] = []; });
    MATERIALS_DATA.forEach(function(m) { byProf[m.prof].push(m); });

    var html = '<div class="ec-mat-scroll"><div class="ec-mat-grid">';
    PROF_ORDER.forEach(function(p) {
      html += '<div class="ec-mat-prof"><div class="ec-mat-prof-lbl">' + PROF_LABELS[p] + '</div>';
      byProf[p].forEach(function(m) {
        var base = Math.max(0.25, (26 - m.tier * 2.5) / 2);
        var eff  = base * totalMult;
        html += '<div class="ec-mat-item">' +
          '<span class="ec-mat-emoji">' + m.emoji + '</span>' +
          '<span class="ec-mat-name">T' + m.tier + ' ' + m.name + '</span>' +
          '<span class="ec-mat-chance">' + fmtChance(eff) + '</span>' +
          '</div>';
      });
      html += '</div>';
    });
    html += '</div></div>';
    var multNote = matMult > 1
      ? '×' + zoneMult + ' zone × ×' + matMult + ' difficulté = ×' + totalMult + ' total'
      : '×' + totalMult + ' zone';
    html += '<div class="ec-mat-note">Taux indiqués = votre métier de récolte (' + multNote + '). Hors métier : ÷10. Niveau de récolte insuffisant = tier verrouillé.</div>';
    return html;
  }

  var BADGE_COLORS = {
    'Emblématique': '#d97706', 'Antique': '#dc2626', 'Runique': '#7c3aed'
  };

  function badgeColor(badge) {
    if (BADGE_COLORS[badge]) return BADGE_COLORS[badge];
    if (badge.indexOf('World Boss') === 0) return '#16a34a';
    if (badge.indexOf('Raid') === 0)       return '#2563eb';
    if (badge.indexOf('Donjon') === 0)     return '#0891b2';
    return '#6b7280';
  }

  function renderEnemy(data, resultEl) {
    var s = data.stats;
    var statsHtml = '';
    var isWorldBoss = data.typeBadge && data.typeBadge.indexOf('World Boss') === 0;
    STAT_ORDER.forEach(function(k){
      var v = s[k]; if (v === undefined) return;
      if (k === 'hp' && isWorldBoss) return;
      var valStr    = (k === 'crit_chance' || k === 'crit_damage') ? v + '%' : fmt(v);
      var isBoosted = data.boostStat === k;
      var isHp      = k === 'hp';
      statsHtml +=
        '<div class="ec-stat' + (isHp ? ' ec-stat-hp' : '') + (isBoosted ? ' ec-stat-boosted' : '') + '">' +
        '<span class="ec-stat-icon">'  + STAT_EMOJIS[k]  + '</span>' +
        '<span class="ec-stat-name">'  + STAT_LABELS[k]  + '</span>' +
        '<span class="ec-stat-val">'   + valStr + (isBoosted ? ' ★' : '') + '</span></div>';
    });

    var passifHtml = data.passif
      ? '<div class="ec-passif"><div class="ec-passif-lbl">⚡ Passif</div>' +
        '<div class="ec-passif-txt">' + data.passif + '</div></div>'
      : '';

    var noteHtml = data.nameNote
      ? '<div class="ec-note">ℹ️ ' + data.nameNote + '</div>' : '';

    var reqHtml = data.req
      ? '<div class="ec-req">🔓 Niveau requis : <strong>' + data.req + '</strong></div>' : '';

    var zoneHtml = data.zoneEquiv
      ? '<div class="ec-note">⚙️ Zone équivalente : ' + fmt(data.zoneEquiv) + '</div>' : '';

    var bc = badgeColor(data.typeBadge);
    resultEl.innerHTML =
      '<div class="ec-header">' +
        '<div class="ec-emoji">'        + data.themeEmoji + '</div>' +
        '<div class="ec-title-block">' +
          '<div class="ec-name">'       + data.name + '</div>' +
          '<div class="ec-meta">'       + (CLASS_EMOJI[data.cls] || '👹') + ' ' + data.cls +
            ' &nbsp;·&nbsp; '           + data.theme + '</div>' + noteHtml +
        '</div>' +
        '<div class="ec-badge" style="background:' + bc + '">' + data.typeBadge + '</div>' +
      '</div>' +
      reqHtml +
      '<div class="ec-stats-grid">' + statsHtml + '</div>' +
      passifHtml + zoneHtml +
      '<div class="ec-rewards">' +
        '<span>✨ XP : <strong>'  + fmt(data.xp)   + '</strong></span>' +
        '<span>🪙 Or : <strong>' + fmt(data.gold) + '</strong></span>' +
      '</div>' +
      (data.drops || data.matZone ? '<details class="ec-drops-detail"><summary>🎁 Récompenses possibles</summary>' +
        (data.drops ? '<div class="ec-drops-equip">⚔️ <strong>Équipement</strong> : ' + data.drops + '</div>' : '') +
        (data.matZone ? '<div class="ec-drops-mats"><strong>📦 Matériaux</strong> (hors bonus niveau récolte)</div>' + renderMaterialDrops(data.matZone, data.matMult) : '') +
      '</details>' : '');

    resultEl.style.display = 'block';
  }

  // ─── Initialisation UI ────────────────────────────────────────────────────

  function setupCalculator(container) {
    var tabs   = container.querySelectorAll('.ec-tab');
    var panels = {
      monde:  container.querySelector('#ec-ctrl-monde'),
      donjon: container.querySelector('#ec-ctrl-donjon'),
      raid:   container.querySelector('#ec-ctrl-raid'),
      wb:     container.querySelector('#ec-ctrl-wb')
    };
    var resultEl = container.querySelector('#ec-result');
    var mode = 'monde';

    function showPanel(m) {
      mode = m;
      Object.keys(panels).forEach(function(k){
        if (panels[k]) panels[k].style.display = k === m ? '' : 'none';
      });
      tabs.forEach(function(t){
        t.className = 'ec-tab' + (t.dataset.mode === m ? ' ec-tab-active' : '');
      });
      refresh();
    }

    function updateMondeStageOptions(zone) {
      var sel = container.querySelector('#ec-stage');
      if (!sel) return;
      var cur = sel.value;
      sel.querySelectorAll('option').forEach(function(o) {
        if (o.value === 'boss_runique')      o.disabled = (zone % 10  !== 0);
        if (o.value === 'boss_emblematique') o.disabled = (zone % 100 !== 0);
        if (o.value === 'boss_antique')      o.disabled = (zone % 1000 !== 0);
      });
      var curOpt = sel.querySelector('option[value="' + cur + '"]');
      if (curOpt && curOpt.disabled) sel.value = 'boss_classique';
    }

    tabs.forEach(function(t){
      t.addEventListener('click', function(){ showPanel(t.dataset.mode); });
    });

    function refresh() {
      try {
        var data;
        if (mode === 'monde') {
          var zone      = Math.max(1, Math.min(10000, parseInt(container.querySelector('#ec-zone').value, 10) || 1));
          updateMondeStageOptions(zone);
          var stageVal  = container.querySelector('#ec-stage').value;
          var bossClass = container.querySelector('#ec-boss-class') ? (container.querySelector('#ec-boss-class').value || null) : null;
          var classRow  = container.querySelector('#ec-class-row');

          var showClass = (stageVal === 'boss_emblematique' || stageVal === 'boss_antique');
          if (classRow) classRow.style.display = showClass ? '' : 'none';

          if      (stageVal === 'boss_antique')      data = calcAntique(zone, bossClass);
          else if (stageVal === 'boss_emblematique') data = calcEmblematique(zone, bossClass);
          else if (stageVal === 'boss_runique')      data = calcRunicBoss(zone);
          else if (stageVal === 'boss_classique')    data = calcMondeBossClassique(zone);
          else                                       data = calcMondeEnemy(zone, parseInt(stageVal, 10));

        } else if (mode === 'donjon') {
          var bossId = container.querySelector('#ec-donjon-boss').value;
          var diff   = (container.querySelector('input[name="ec-diff"]:checked') || {}).value || 'classique';
          var lvl    = parseInt(container.querySelector('#ec-donjon-level').value, 10) || 1;
          data = calcDonjon(bossId, diff, lvl);

        } else if (mode === 'raid') {
          data = calcRaid(container.querySelector('#ec-raid-boss').value);

        } else {
          var wbInput = container.querySelector('#ec-wb-tour-input') || container.querySelector('#ec-wb-tour');
          data = calcWorldBoss(parseInt(wbInput.value, 10) || 1);
        }

        renderEnemy(data, resultEl);
      } catch(e) {
        console.error('[EnemyCalc]', e);
      }
    }

    // Sliders → label
    var djLvl = container.querySelector('#ec-donjon-level');
    var djVal = container.querySelector('#ec-donjon-level-val');
    if (djLvl && djVal) {
      djLvl.addEventListener('input', function(){ djVal.textContent = djLvl.value; refresh(); });
    }
    var wbTour      = container.querySelector('#ec-wb-tour');
    var wbVal       = container.querySelector('#ec-wb-tour-val');
    var wbTourInput = container.querySelector('#ec-wb-tour-input');

    function syncWbTour(val) {
      val = Math.max(1, Math.min(20, parseInt(val, 10) || 1));
      if (wbVal)       wbVal.textContent = val;
      if (wbTour)      wbTour.value      = val;
      if (wbTourInput) wbTourInput.value = val;
      var turn = Math.max(0, val - 1);
      var ze   = Math.round(1000 * Math.pow(1.25, turn));
      var zeEl = container.querySelector('#ec-wb-zone-equiv');
      if (zeEl) zeEl.textContent = 'Zone équivalente : ~' + ze.toLocaleString('fr-FR');
    }

    if (wbTour) {
      wbTour.addEventListener('input', function(){ syncWbTour(wbTour.value); refresh(); });
    }
    if (wbTourInput) {
      wbTourInput.addEventListener('input',  function(){ syncWbTour(wbTourInput.value); refresh(); });
      wbTourInput.addEventListener('change', function(){ syncWbTour(wbTourInput.value); refresh(); });
    }

    // Tous les autres inputs
    container.querySelectorAll('input:not([type="range"]):not([type="radio"]), select').forEach(function(el){
      el.addEventListener('change', refresh);
      el.addEventListener('input',  refresh);
    });
    container.querySelectorAll('input[type="radio"]').forEach(function(el){
      el.addEventListener('change', refresh);
    });

    // Initialise WB zone equiv display
    syncWbTour(1);

    // Render initial — auto-detect first available panel
    var defaultMode = null;
    ['monde', 'donjon', 'raid', 'wb'].forEach(function(m) {
      if (!defaultMode && panels[m]) defaultMode = m;
    });
    if (defaultMode) showPanel(defaultMode);
  }

  // ─── Point d'entrée ───────────────────────────────────────────────────────

  function init() {
    var el = document.getElementById('enemy-calculator');
    if (!el || el.dataset.calcInit) return;
    el.dataset.calcInit = '1';
    setupCalculator(el);
  }

  if (typeof document$ !== 'undefined') {
    document$.subscribe(init);
  }
  document.addEventListener('DOMContentLoaded', init);

})();
