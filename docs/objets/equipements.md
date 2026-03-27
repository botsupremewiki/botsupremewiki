# 🛡️ Équipements & Panoplies

Les équipements améliorent tes statistiques en combat. Il existe **7 emplacements** à équiper, et des **panoplies** (sets) qui donnent des bonus supplémentaires quand plusieurs pièces du même set sont portées ensemble.

Il y a au total **60 panoplies** : 6 par classe × 10 classes.

---

## Les 7 emplacements

| Emplacement | Guerrier | Assassin | Mage | Tireur | Support | Vampire | Gardien | Ombre Venin | Pyromancien | Paladin |
|-------------|----------|----------|------|--------|---------|---------|---------|-------------|-------------|---------|
| Tête | Heaume | Capuche | Chapeau | Cagoule | Bassinet | Masque | Couronne | Voile | Coiffe | Armet |
| Torse | Cuirasse | Mantelet | Robe | Veste | Brigandine | Cape | Manteau | Suaire | Tunique | Haubert |
| Jambes | Braies | Grègues | Jupe | Jambières | Cuissardes | Collant | Bas | Guêtres | Pantalon | Tassettes |
| Pieds | Sollerets | Chaussons | Sandales | Bottes | Grèves | Bottines | Escarpes | Mocassins | Sabots | Éperons |
| Arme | Épée | Dague | Bâton | Arc | Bouclier | Crocs | Sablier | Aiguille | Torche | Marteau |
| Amulette | Médaillon | Pendentif | Talisman | Collier | Amulette | Breloque | Relique | Fiole | Phylactère | Croix |
| Anneau | Chevalière | Signet | Bague | Jonc | Sceau | Cachet | Alliance | Annelet | Gemme | Insigne |

---

## Multiplicateurs

### Rareté

La rareté d'un équipement détermine la puissance de ses statistiques.

| Rareté | Multiplicateur |
|--------|---------------|
| ⬜ Commun | ×1,0 |
| 🟩 Peu Commun | ×1,2 |
| 🟦 Rare | ×1,4 |
| 🟪 Épique | ×1,6 |
| 🟧 Légendaire | ×1,8 |
| 🟥 Mythique | ×2,0 |
| 🔶 Artefact | ×2,2 |
| 🟡 Divin | ×2,4 |
| 🩵 Transcendant | ×2,6 |
| 🌈 Prismatique | ×3,0 |

#### Distribution des raretés selon la zone (drops Monde)

La rareté des drops d'équipements dans le **Monde** évolue progressivement avec la zone :

| Zone | ⬜ Com. | 🟩 P.Com. | 🟦 Rare | 🟪 Épiq. | 🟧 Légend. | 🟥 Myth. | 🔶 Artef. | 🟡 Divin | 🩵 Trans. | 🌈 Prism. |
|:----:|:------:|:--------:|:------:|:-------:|:---------:|:-------:|:--------:|:-------:|:--------:|:--------:|
| 1 | 100% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% | 0% |
| 1 000 | 64% | 25% | 10% | 1% | 0% | 0% | 0% | 0% | 0% | 0% |
| 2 000 | 20% | 50% | 20% | 8% | 2% | 0% | 0% | 0% | 0% | 0% |
| 3 000 | 10% | 30% | 20% | 14% | 10% | 8% | 5% | 3% | 1% | 0% |
| 4 000 | 0% | 10% | 20% | 20% | 18% | 15% | 10% | 5% | 2% | 0% |
| 5 000 | 0% | 6% | 15% | 19% | 19% | 18% | 14% | 7% | 2% | 1% |
| 6 000 | 0% | 2% | 10% | 18% | 20% | 20% | 18% | 8% | 3% | 1% |
| 7 000 | 0% | 1% | 9% | 16% | 19% | 20% | 19% | 12% | 4% | 1% |
| 8 000 | 0% | 0% | 8% | 14% | 18% | 20% | 20% | 15% | 4% | 1% |
| 9 000 | 0% | 0% | 7% | 12% | 17% | 20% | 20% | 15% | 7% | 3% |
| 10 000 | 0% | 0% | 5% | 10% | 15% | 20% | 20% | 15% | 10% | 5% |

!!! info "Interpolation continue"
    Les pourcentages sont interpolés en continu entre ces paliers — chaque zone a sa distribution unique. Les boss Emblématiques et Antiques bénéficient d'un bonus supplémentaire vers les raretés hautes.

### Source

La source détermine le multiplicateur de puissance de base de l'équipement.

| Source | Comment l'obtenir | Multiplicateur |
|--------|-------------------|---------------|
| **Monde** | Drop en battant des ennemis dans les zones | ×1,0 |
| **Donjon Classique** | Drop de boss dans les donjons classiques | ×1,2 |
| **Craft** | Fabriqué par les métiers (Heaumier, Armurier…) | ×1,09 → ×2,00 |
| **Donjon Élite** | Drop de boss dans les donjons élite | ×1,4 |
| **Donjon Abyssal** | Drop de boss dans les donjons abyssaux | ×1,6 |
| **Raid** | Drop dans les raids | ×1,8 |

!!! tip "Craft : multiplicateur par tier de maîtrise"
    Le multiplicateur Craft est **déterministe** et croît avec le niveau de métier. Tier 1 (niv. 1) = ×1,09 · Tier 10 (niv. 90) = ×1,90 · Ultime (niv. 100) = ×2,00. Un artisan niveau 100 dépasse systématiquement tous les donjons.
    → [Recettes d'artisanat complètes](../metiers/artisanat.md)

!!! info "Niveau de l'item"
    Chaque pièce possède un **niveau propre** (1–1000) qui détermine sa puissance ET le niveau minimum du joueur pour l'équiper. Monde = zone ÷ 10, Donjon = niveau donjon × 10, Raid = niveau raid × 100, Craft = niveau métier × 10.

---

## L'amélioration (Forge)

Les équipements peuvent être améliorés à la **Forge** (bouton ⚒️ dans le Hub Profil) jusqu'au **niveau +10**. Chaque niveau d'amélioration augmente toutes les stats de **+10%**, soit un multiplicateur maximum de **×2,0** à +10.

**Formule :** `stats × (1 + amélioration × 0,1)`

| Niveau | Multiplicateur | Coût en or |
|--------|---------------|------------|
| +1 | ×1,1 | 500 |
| +2 | ×1,2 | 1 500 |
| +3 | ×1,3 | 4 000 |
| +4 | ×1,4 | 10 000 |
| +5 | ×1,5 | 25 000 |
| +6 | ×1,6 | 60 000 |
| +7 | ×1,7 | 150 000 |
| +8 | ×1,8 | 400 000 |
| +9 | ×1,9 | 1 000 000 |
| +10 | ×2,0 | 3 000 000 |

---

## Simulateur d'équipement

<div style="background:var(--md-code-bg-color,#f8f8f8);border:1px solid var(--md-default-fg-color--lightest,#ddd);border-radius:8px;padding:20px;margin:16px 0">
<h3 style="margin-top:0">⚔️ Simulateur d'équipement</h3>
<p style="margin-bottom:16px;opacity:.8">Calcule les stats d'un emplacement selon la classe, le niveau d'item, la source, la rareté et l'amélioration.</p>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">
  <div>
    <label style="display:block;font-size:.85em;margin-bottom:4px;font-weight:600">Classe</label>
    <select id="eq-class" onchange="eqUpdateSlots();eqSimulate()" style="width:100%;padding:6px;border-radius:4px;border:1px solid #aaa">
      <option>Guerrier</option><option>Assassin</option><option>Mage</option><option>Tireur</option>
      <option>Support</option><option>Vampire</option><option>Gardien du Temps</option>
      <option>Ombre Venin</option><option>Pyromancien</option><option>Paladin</option>
    </select>
  </div>
  <div>
    <label style="display:block;font-size:.85em;margin-bottom:4px;font-weight:600">Emplacement</label>
    <select id="eq-slot" onchange="eqSimulate()" style="width:100%;padding:6px;border-radius:4px;border:1px solid #aaa"></select>
  </div>
</div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">
  <div>
    <label style="display:block;font-size:.85em;margin-bottom:4px;font-weight:600">Niveau d'item : <span id="eq-level-lbl">100</span></label>
    <input type="range" id="eq-level" min="1" max="1000" value="100" oninput="document.getElementById('eq-level-lbl').textContent=this.value;eqSimulate()" style="width:100%">
  </div>
  <div>
    <label style="display:block;font-size:.85em;margin-bottom:4px;font-weight:600">Source</label>
    <select id="eq-source" onchange="eqToggleCraft();eqSimulate()" style="width:100%;padding:6px;border-radius:4px;border:1px solid #aaa">
      <option value="1.0">Monde (×1,0)</option>
      <option value="1.2">Donjon Classique (×1,2)</option>
      <option value="craft">Craft (×1,0 → ×2,0)</option>
      <option value="1.4">Donjon Élite (×1,4)</option>
      <option value="1.6">Donjon Abyssal (×1,6)</option>
      <option value="1.8">Raid (×1,8)</option>
    </select>
  </div>
</div>

<div id="eq-craft-row" style="display:none;margin-bottom:12px">
  <label style="display:block;font-size:.85em;margin-bottom:4px;font-weight:600">Mult. Craft : ×<span id="eq-craft-lbl">1.50</span></label>
  <input type="range" id="eq-craft" min="1.00" max="2.00" step="0.01" value="1.50" oninput="document.getElementById('eq-craft-lbl').textContent=parseFloat(this.value).toFixed(2);eqSimulate()" style="width:100%">
</div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px">
  <div>
    <label style="display:block;font-size:.85em;margin-bottom:4px;font-weight:600">Rareté</label>
    <select id="eq-rarity" onchange="eqSimulate()" style="width:100%;padding:6px;border-radius:4px;border:1px solid #aaa">
      <option value="1.0">⬜ Commun</option><option value="1.2">🟩 Peu Commun</option>
      <option value="1.4">🟦 Rare</option><option value="1.6">🟪 Épique</option>
      <option value="1.8">🟧 Légendaire</option><option value="2.0">🟥 Mythique</option>
      <option value="2.2">🔶 Artefact</option><option value="2.4">🟡 Divin</option>
      <option value="2.6">🩵 Transcendant</option><option value="3.0">🌈 Prismatique</option>
    </select>
  </div>
  <div>
    <label style="display:block;font-size:.85em;margin-bottom:4px;font-weight:600">Amélioration Forge : <span id="eq-enh-lbl">+0 (×1,0)</span></label>
    <input type="range" id="eq-enh" min="0" max="10" value="0" oninput="document.getElementById('eq-enh-lbl').textContent='+'+this.value+' (×'+(1+this.value*0.1).toFixed(1)+')';eqSimulate()" style="width:100%">
  </div>
</div>

<div id="eq-result" style="border-top:1px solid var(--md-default-fg-color--lightest,#ddd);padding-top:12px"></div>
</div>

<script>
(function(){
const EQ_BASE={
  "Guerrier":{hp:600,p_atk:60,m_atk:0,p_pen:8,m_pen:0,p_def:28,m_def:6,speed:80,crit_chance:5.0,crit_damage:150.0},
  "Assassin":{hp:500,p_atk:50,m_atk:0,p_pen:10,m_pen:0,p_def:4,m_def:3,speed:160,crit_chance:20.0,crit_damage:175.0},
  "Mage":{hp:400,p_atk:0,m_atk:40,p_pen:0,m_pen:8,p_def:3,m_def:10,speed:90,crit_chance:12.0,crit_damage:175.0},
  "Tireur":{hp:440,p_atk:44,m_atk:0,p_pen:8,m_pen:0,p_def:4,m_def:4,speed:130,crit_chance:18.0,crit_damage:175.0},
  "Support":{hp:600,p_atk:34,m_atk:34,p_pen:6,m_pen:6,p_def:25,m_def:25,speed:55,crit_chance:5.0,crit_damage:140.0},
  "Vampire":{hp:450,p_atk:45,m_atk:0,p_pen:9,m_pen:0,p_def:12,m_def:7,speed:90,crit_chance:15.0,crit_damage:175.0},
  "Gardien du Temps":{hp:400,p_atk:22,m_atk:22,p_pen:4,m_pen:4,p_def:15,m_def:15,speed:85,crit_chance:8.0,crit_damage:155.0},
  "Ombre Venin":{hp:300,p_atk:30,m_atk:12,p_pen:6,m_pen:2,p_def:5,m_def:5,speed:115,crit_chance:16.0,crit_damage:170.0},
  "Pyromancien":{hp:400,p_atk:0,m_atk:40,p_pen:0,m_pen:8,p_def:2,m_def:10,speed:85,crit_chance:12.0,crit_damage:175.0},
  "Paladin":{hp:560,p_atk:30,m_atk:0,p_pen:6,m_pen:0,p_def:35,m_def:22,speed:55,crit_chance:5.0,crit_damage:150.0}
};
const EQ_GROWTH={
  "Guerrier":{hp:35.45,p_atk:3.143,m_atk:0,p_pen:0.632,m_pen:0,p_def:0.572,m_def:0.114,speed:0.195,crit_chance:0.007,crit_damage:0.015},
  "Assassin":{hp:39.54,p_atk:2.953,m_atk:0,p_pen:0.591,m_pen:0,p_def:0.076,m_def:0.047,speed:0.340,crit_chance:0.010,crit_damage:0.025},
  "Mage":{hp:34.64,p_atk:0,m_atk:2.462,p_pen:0,m_pen:0.492,p_def:0.047,m_def:0.190,speed:0.260,crit_chance:0.016,crit_damage:0.020},
  "Tireur":{hp:37.60,p_atk:2.760,m_atk:0,p_pen:0.552,m_pen:0,p_def:0.076,m_def:0.076,speed:0.270,crit_chance:0.014,crit_damage:0.020},
  "Support":{hp:64.46,p_atk:2.168,m_atk:2.168,p_pen:0.434,m_pen:0.434,p_def:0.475,m_def:0.475,speed:0.195,crit_chance:0.003,crit_damage:0.010},
  "Vampire":{hp:39.59,p_atk:2.758,m_atk:0,p_pen:0.551,m_pen:0,p_def:0.188,m_def:0.113,speed:0.260,crit_chance:0.007,crit_damage:0.020},
  "Gardien du Temps":{hp:37.64,p_atk:1.480,m_atk:1.480,p_pen:0.296,m_pen:0.296,p_def:0.335,m_def:0.335,speed:0.245,crit_chance:0.010,crit_damage:0.015},
  "Ombre Venin":{hp:43.74,p_atk:2.172,m_atk:1.189,p_pen:0.434,m_pen:0.168,p_def:0.075,m_def:0.075,speed:0.300,crit_chance:0.008,crit_damage:0.015},
  "Pyromancien":{hp:41.60,p_atk:0,m_atk:2.462,p_pen:0,m_pen:0.492,p_def:0.048,m_def:0.190,speed:0.245,crit_chance:0.013,crit_damage:0.020},
  "Paladin":{hp:54.50,p_atk:2.973,m_atk:0,p_pen:0.594,m_pen:0,p_def:0.665,m_def:0.429,speed:0.195,crit_chance:0.003,crit_damage:0.005}
};
const EQ_ARMOR={casque:["hp","p_def","m_def"],plastron:["hp","p_def","m_def"],pantalon:["hp","p_def","m_def","speed"],chaussures:["speed","p_def","m_def"]};
const EQ_OFFENSE={
  "Guerrier":{arme:["p_atk","p_pen","crit_chance","crit_damage"],amulette:["p_atk"],anneau:["p_atk","p_pen"]},
  "Assassin":{arme:["p_atk","p_pen","speed","crit_chance","crit_damage"],amulette:["speed","crit_chance","crit_damage"],anneau:["p_atk","p_pen","crit_chance","crit_damage"]},
  "Mage":{arme:["m_atk","m_pen","crit_chance","crit_damage"],amulette:["m_atk","m_pen","hp"],anneau:["m_atk","m_pen"]},
  "Tireur":{arme:["p_atk","p_pen","crit_chance","crit_damage"],amulette:["speed","crit_chance","crit_damage"],anneau:["p_atk","p_pen","crit_chance","crit_damage"]},
  "Support":{arme:["p_atk","m_atk","p_pen","m_pen"],amulette:["m_atk","m_pen","speed"],anneau:["p_atk","p_pen","speed"]},
  "Vampire":{arme:["p_atk","p_pen","crit_chance","crit_damage"],amulette:["p_atk","hp"],anneau:["p_atk","p_pen","hp"]},
  "Gardien du Temps":{arme:["p_atk","m_atk","p_pen","m_pen"],amulette:["m_atk","m_pen","crit_chance","crit_damage"],anneau:["p_atk","p_pen","crit_chance","crit_damage"]},
  "Ombre Venin":{arme:["p_atk","m_atk","p_pen","speed","crit_chance"],amulette:["m_atk","m_pen","speed","crit_chance"],anneau:["p_atk","p_pen","crit_damage"]},
  "Pyromancien":{arme:["m_atk","m_pen","crit_chance","crit_damage"],amulette:["m_atk","m_pen"],anneau:["m_atk","m_pen"]},
  "Paladin":{arme:["p_atk","p_pen","crit_chance","crit_damage"],amulette:["p_atk","hp"],anneau:["p_atk","hp"]}
};
const EQ_SLOT_NAMES={
  "Guerrier":{casque:"Heaume",plastron:"Cuirasse",pantalon:"Braies",chaussures:"Sollerets",arme:"Épée",amulette:"Médaillon",anneau:"Chevalière"},
  "Assassin":{casque:"Capuche",plastron:"Mantelet",pantalon:"Grègues",chaussures:"Chaussons",arme:"Dague",amulette:"Pendentif",anneau:"Signet"},
  "Mage":{casque:"Chapeau",plastron:"Robe",pantalon:"Jupe",chaussures:"Sandales",arme:"Bâton",amulette:"Talisman",anneau:"Bague"},
  "Tireur":{casque:"Cagoule",plastron:"Veste",pantalon:"Jambières",chaussures:"Bottes",arme:"Arc",amulette:"Collier",anneau:"Jonc"},
  "Support":{casque:"Bassinet",plastron:"Brigandine",pantalon:"Cuissardes",chaussures:"Grèves",arme:"Bouclier",amulette:"Amulette",anneau:"Sceau"},
  "Vampire":{casque:"Masque",plastron:"Cape",pantalon:"Collant",chaussures:"Bottines",arme:"Crocs",amulette:"Breloque",anneau:"Cachet"},
  "Gardien du Temps":{casque:"Couronne",plastron:"Manteau",pantalon:"Bas",chaussures:"Escarpes",arme:"Sablier",amulette:"Relique",anneau:"Alliance"},
  "Ombre Venin":{casque:"Voile",plastron:"Suaire",pantalon:"Guêtres",chaussures:"Mocassins",arme:"Aiguille",amulette:"Fiole",anneau:"Annelet"},
  "Pyromancien":{casque:"Coiffe",plastron:"Tunique",pantalon:"Pantalon",chaussures:"Sabots",arme:"Torche",amulette:"Phylactère",anneau:"Gemme"},
  "Paladin":{casque:"Armet",plastron:"Haubert",pantalon:"Tassettes",chaussures:"Éperons",arme:"Marteau",amulette:"Croix",anneau:"Insigne"}
};
const EQ_STAT_FR={hp:"HP",p_atk:"ATK Physique",m_atk:"ATK Magique",p_pen:"Pén. Physique",m_pen:"Pén. Magique",p_def:"Déf. Physique",m_def:"Déf. Magique",speed:"Vitesse",crit_chance:"Chance de Crit.",crit_damage:"Dégâts Crit."};
const EQ_IS_PCT={crit_chance:true,crit_damage:true};

function eqGetSlotStats(cls,slot){
  if(EQ_ARMOR[slot])return EQ_ARMOR[slot];
  return(EQ_OFFENSE[cls]||{})[slot]||[];
}
function eqStatCount(cls){
  const counts={};
  for(const slot of["casque","plastron","pantalon","chaussures","arme","amulette","anneau"]){
    for(const s of eqGetSlotStats(cls,slot))counts[s]=(counts[s]||0)+1;
  }
  return counts;
}
const EQ_SLOT_FR={casque:'Casque',plastron:'Torse',pantalon:'Jambes',chaussures:'Pieds',arme:'Arme',amulette:'Amulette',anneau:'Anneau'};
window.eqUpdateSlots=function(){
  const cls=document.getElementById('eq-class').value;
  const sel=document.getElementById('eq-slot');
  const prev=sel.value;
  sel.innerHTML='';
  for(const[k,v]of Object.entries(EQ_SLOT_NAMES[cls])){
    const o=document.createElement('option');o.value=k;o.textContent=v+' ('+(EQ_SLOT_FR[k]||k)+')';sel.appendChild(o);
  }
  if([...sel.options].some(o=>o.value===prev))sel.value=prev;
};
window.eqToggleCraft=function(){
  const v=document.getElementById('eq-source').value;
  document.getElementById('eq-craft-row').style.display=v==='craft'?'block':'none';
};
window.eqSimulate=function(){
  const cls=document.getElementById('eq-class').value;
  const slot=document.getElementById('eq-slot').value;
  const L=parseInt(document.getElementById('eq-level').value)||1;
  const srcVal=document.getElementById('eq-source').value;
  const srcMult=srcVal==='craft'?parseFloat(document.getElementById('eq-craft').value):parseFloat(srcVal);
  const rarMult=parseFloat(document.getElementById('eq-rarity').value);
  const enh=parseInt(document.getElementById('eq-enh').value)||0;
  const enhMult=1+enh*0.1;
  const base=EQ_BASE[cls],growth=EQ_GROWTH[cls];
  const counts=eqStatCount(cls);
  const slotStats=eqGetSlotStats(cls,slot);
  if(!slotStats.length){document.getElementById('eq-result').innerHTML='<em>Aucune stat pour cet emplacement.</em>';return;}
  let html='<table style="width:100%;border-collapse:collapse;font-size:.9em"><thead><tr><th style="text-align:left;padding:6px 8px;border-bottom:2px solid var(--md-default-fg-color--lightest,#ddd)">Statistique</th><th style="text-align:right;padding:6px 8px;border-bottom:2px solid var(--md-default-fg-color--lightest,#ddd)">Valeur</th></tr></thead><tbody>';
  for(const stat of slotStats){
    const n=counts[stat]||1;
    const g=(growth[stat]||0)/n;
    const c=((base[stat]||0)-(growth[stat]||0))/n;
    const raw=L*g+c;
    const final=raw*srcMult*rarMult*enhMult;
    const disp=EQ_IS_PCT[stat]?final.toFixed(2)+'%':Math.round(final).toLocaleString('fr-FR');
    html+=`<tr><td style="padding:5px 8px;border-bottom:1px solid var(--md-default-fg-color--lightest,#eee)">${EQ_STAT_FR[stat]||stat}</td><td style="text-align:right;padding:5px 8px;border-bottom:1px solid var(--md-default-fg-color--lightest,#eee);font-weight:600">${disp}</td></tr>`;
  }
  html+='</tbody></table>';
  document.getElementById('eq-result').innerHTML=html;
};
// Init
eqUpdateSlots();eqSimulate();
})();
</script>

---

## Simulateur de panoplie

<div style="background:var(--md-code-bg-color,#f8f8f8);border:1px solid var(--md-default-fg-color--lightest,#ddd);border-radius:8px;padding:20px;margin:16px 0">
<h3 style="margin-top:0">🛡️ Simulateur de panoplie</h3>
<p style="margin-bottom:16px;opacity:.8">Calcule les bonus actifs d'une panoplie selon le nombre de pièces équipées et la rareté minimale.</p>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">
  <div>
    <label style="display:block;font-size:.85em;margin-bottom:4px;font-weight:600">Panoplie</label>
    <select id="set-id" onchange="setSimulate()" style="width:100%;padding:6px;border-radius:4px;border:1px solid #aaa">
      <optgroup label="⚔️ Guerrier">
        <option value="guerrier_monde">Acier de Fer (Monde)</option>
        <option value="guerrier_donjon_classique">Rempart de Fer (Classique)</option>
        <option value="guerrier_craft">Métal Forgé (Craft)</option>
        <option value="guerrier_donjon_elite">Titan Écarlate (Élite)</option>
        <option value="guerrier_donjon_abyssal">Seigneur de l'Abîme (Abyssal)</option>
        <option value="guerrier_raid">Colosse de Guerre (Raid)</option>
      </optgroup>
      <optgroup label="🗡️ Assassin">
        <option value="assassin_monde">Ombre Légère (Monde)</option>
        <option value="assassin_donjon_classique">Lame du Crépuscule (Classique)</option>
        <option value="assassin_craft">Acier Trempé (Craft)</option>
        <option value="assassin_donjon_elite">Fantôme Acéré (Élite)</option>
        <option value="assassin_donjon_abyssal">Voile de Sang (Abyssal)</option>
        <option value="assassin_raid">Exécuteur des Ombres (Raid)</option>
      </optgroup>
      <optgroup label="🔮 Mage">
        <option value="mage_monde">Novice Arcane (Monde)</option>
        <option value="mage_donjon_classique">Manteau Astral (Classique)</option>
        <option value="mage_craft">Tissu Enchanté (Craft)</option>
        <option value="mage_donjon_elite">Voile du Prophète (Élite)</option>
        <option value="mage_donjon_abyssal">Suaire Primordial (Abyssal)</option>
        <option value="mage_raid">Nexus Primordial (Raid)</option>
      </optgroup>
      <optgroup label="🏹 Tireur">
        <option value="tireur_monde">Carquois de Chasse (Monde)</option>
        <option value="tireur_donjon_classique">Arc du Faucon (Classique)</option>
        <option value="tireur_craft">Bois Taillé (Craft)</option>
        <option value="tireur_donjon_elite">Tempête d'Acier (Élite)</option>
        <option value="tireur_donjon_abyssal">Œil de l'Horizon (Abyssal)</option>
        <option value="tireur_raid">Ouragan d'Acier (Raid)</option>
      </optgroup>
      <optgroup label="🛡️ Support">
        <option value="support_monde">Médaillon du Novice (Monde)</option>
        <option value="support_donjon_classique">Armure du Défenseur (Classique)</option>
        <option value="support_craft">Métal Béni (Craft)</option>
        <option value="support_donjon_elite">Bénédiction Sacrée (Élite)</option>
        <option value="support_donjon_abyssal">Bouclier du Gardien (Abyssal)</option>
        <option value="support_raid">Lumière Éternelle (Raid)</option>
      </optgroup>
      <optgroup label="🧛 Vampire">
        <option value="vampire_monde">Crocs de la Nuit (Monde)</option>
        <option value="vampire_donjon_classique">Manteau Maudit (Classique)</option>
        <option value="vampire_craft">Acier Ensanglanté (Craft)</option>
        <option value="vampire_donjon_elite">Suaire des Ténèbres (Élite)</option>
        <option value="vampire_donjon_abyssal">Seigneur des Ténèbres (Abyssal)</option>
        <option value="vampire_raid">Prince Immortel (Raid)</option>
      </optgroup>
      <optgroup label="⏳ Gardien du Temps">
        <option value="gardien_monde">Brisé (Monde)</option>
        <option value="gardien_donjon_classique">Horloge Fractale (Classique)</option>
        <option value="gardien_craft">Tissu Temporel (Craft)</option>
        <option value="gardien_donjon_elite">Chrono Maudit (Élite)</option>
        <option value="gardien_donjon_abyssal">Paradoxe Temporel (Abyssal)</option>
        <option value="gardien_raid">Maître du Destin (Raid)</option>
      </optgroup>
      <optgroup label="☠️ Ombre Venin">
        <option value="ombre_monde">Distillat Vénéneux (Monde)</option>
        <option value="ombre_donjon_classique">Aiguille Toxique (Classique)</option>
        <option value="ombre_craft">Venin Distillé (Craft)</option>
        <option value="ombre_donjon_elite">Brume Toxique (Élite)</option>
        <option value="ombre_donjon_abyssal">Essence Corrompue (Abyssal)</option>
        <option value="ombre_raid">Nécrosis Primordiale (Raid)</option>
      </optgroup>
      <optgroup label="🔥 Pyromancien">
        <option value="pyro_monde">Tison Ardent (Monde)</option>
        <option value="pyro_donjon_classique">Flamme Enflammée (Classique)</option>
        <option value="pyro_craft">Pierre Incandescente (Craft)</option>
        <option value="pyro_donjon_elite">Brasier Infernal (Élite)</option>
        <option value="pyro_donjon_abyssal">Âme Volcanique (Abyssal)</option>
        <option value="pyro_raid">Phénix Éternel (Raid)</option>
      </optgroup>
      <optgroup label="✝️ Paladin">
        <option value="paladin_monde">Armure Consacrée (Monde)</option>
        <option value="paladin_donjon_classique">Vœu du Croisé (Classique)</option>
        <option value="paladin_craft">Métal Sanctifié (Craft)</option>
        <option value="paladin_donjon_elite">Lumière Divine (Élite)</option>
        <option value="paladin_donjon_abyssal">Bouclier de la Foi (Abyssal)</option>
        <option value="paladin_raid">Avatar Sacré (Raid)</option>
      </optgroup>
    </select>
  </div>
  <div>
    <label style="display:block;font-size:.85em;margin-bottom:4px;font-weight:600">Pièces équipées : <span id="set-pcs-lbl">4</span></label>
    <input type="range" id="set-pcs" min="1" max="7" value="4" oninput="document.getElementById('set-pcs-lbl').textContent=this.value;setSimulate()" style="width:100%;margin-top:8px">
    <div style="display:flex;justify-content:space-between;font-size:.75em;opacity:.6"><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span><span>6</span><span>7</span></div>
  </div>
</div>

<div style="margin-bottom:16px">
  <label style="display:block;font-size:.85em;margin-bottom:4px;font-weight:600">Rareté minimale (pièce la moins rare)</label>
  <select id="set-rarity" onchange="setSimulate()" style="width:100%;padding:6px;border-radius:4px;border:1px solid #aaa">
    <option value="1.0">⬜ Commun</option><option value="1.2">🟩 Peu Commun</option>
    <option value="1.4">🟦 Rare</option><option value="1.6">🟪 Épique</option>
    <option value="1.8">🟧 Légendaire</option><option value="2.0">🟥 Mythique</option>
    <option value="2.2">🔶 Artefact</option><option value="2.4">🟡 Divin</option>
    <option value="2.6">🩵 Transcendant</option><option value="3.0">🌈 Prismatique</option>
  </select>
</div>

<div id="set-result" style="border-top:1px solid var(--md-default-fg-color--lightest,#ddd);padding-top:12px"></div>
</div>

<script>
(function(){
const SET_SRC_MULT={monde:1.0,donjon_classique:1.2,craft:1.5,donjon_elite:1.4,donjon_abyssal:1.6,raid:1.8};
const SET_SRC_LABEL={monde:"Monde ×1,0",donjon_classique:"Donjon Classique ×1,2",craft:"Craft ×1,5 (médiane)",donjon_elite:"Donjon Élite ×1,4",donjon_abyssal:"Donjon Abyssal ×1,6",raid:"Raid ×1,8"};
const SET_PCT_FR={hp_pct:"HP",p_atk_pct:"ATK Physique",m_atk_pct:"ATK Magique",p_pen_pct:"Pén. Physique",m_pen_pct:"Pén. Magique",p_def_pct:"Déf. Physique",m_def_pct:"Déf. Magique",speed_pct:"Vitesse",crit_chance_pct:"Chance de Crit.",crit_damage_pct:"Dégâts Crit."};
const SETS={
  guerrier_monde:{n:"Acier de Fer",c:"Guerrier",s:"monde",t:{2:{hp_pct:2},4:{p_def_pct:3},5:{hp_pct:3},6:{p_def_pct:4}},p:{3:"Régénère 2% de tes HP max à la fin de chaque tour.",7:"Chaque ennemi vaincu régénère 8% de tes HP max. +5% dégâts physiques."}},
  guerrier_donjon_classique:{n:"Rempart de Fer",c:"Guerrier",s:"donjon_classique",t:{2:{p_def_pct:2},4:{m_def_pct:3},5:{p_def_pct:3},6:{m_def_pct:4}},p:{3:"Réduit les dégâts reçus de 5%.",7:"Immunisé aux réductions de stats ennemies. Chaque attaque reçue régénère 2% HP max."}},
  guerrier_craft:{n:"Métal Forgé",c:"Guerrier",s:"craft",t:{2:{p_atk_pct:2},4:{p_pen_pct:3},5:{hp_pct:3},6:{p_atk_pct:4}},p:{3:"Chaque attaque physique reçue augmente tes dégâts de 2% (max +20%).",7:"Contre-attaque : après avoir reçu un coup, 25% de chance de riposter avec 60% ATK Physique."}},
  guerrier_donjon_elite:{n:"Titan Écarlate",c:"Guerrier",s:"donjon_elite",t:{2:{p_atk_pct:2},4:{p_pen_pct:3},5:{p_atk_pct:3},6:{p_atk_pct:4}},p:{3:"Si HP < 50% : tes dégâts physiques sont augmentés de 12%.",7:"+2% dégâts physiques par 5% HP manquants. Dégâts critiques +30% quand HP < 30%."}},
  guerrier_donjon_abyssal:{n:"Seigneur de l'Abîme",c:"Guerrier",s:"donjon_abyssal",t:{2:{p_atk_pct:2},4:{p_pen_pct:3},5:{p_atk_pct:3},6:{p_pen_pct:4}},p:{3:"Ignore 10% de la DEF Physique ennemie.",7:"Ignore 25% DEF Physique ennemie. Chaque critique régénère 4% HP max."}},
  guerrier_raid:{n:"Colosse de Guerre",c:"Guerrier",s:"raid",t:{2:{hp_pct:2},4:{p_atk_pct:3},5:{p_pen_pct:3},6:{hp_pct:4}},p:{3:"+10% dégâts physiques et +5% réduction dégâts reçus.",7:"Immunité aux stun. +20% dégâts quand HP < 30%. Régénère 5% HP max/tour."}},
  assassin_monde:{n:"Ombre Légère",c:"Assassin",s:"monde",t:{2:{speed_pct:2},4:{p_atk_pct:3},5:{speed_pct:3},6:{p_atk_pct:4}},p:{3:"Le premier coup de chaque combat est toujours un critique.",7:"Le premier coup inflige +25% dégâts. Si l'ennemi est à plein HP, +50% à la place."}},
  assassin_donjon_classique:{n:"Lame du Crépuscule",c:"Assassin",s:"donjon_classique",t:{2:{p_atk_pct:2},4:{p_pen_pct:3},5:{p_atk_pct:3},6:{p_atk_pct:4}},p:{3:"Chaque critique consécutif augmente ton crit_damage de 5% (max +25%).",7:"Après 3 critiques consécutifs, ta prochaine attaque ignore toute la DEF Physique ennemie."}},
  assassin_craft:{n:"Acier Trempé",c:"Assassin",s:"craft",t:{2:{speed_pct:2},4:{p_atk_pct:3},5:{speed_pct:3},6:{p_atk_pct:4}},p:{3:"Chaque esquive réussie augmente tes dégâts de 6% pour 2 tours (max +30%).",7:"Après une esquive, +15% de chance d'esquiver le prochain coup. Dégâts +40% si esquive active."}},
  assassin_donjon_elite:{n:"Fantôme Acéré",c:"Assassin",s:"donjon_elite",t:{2:{speed_pct:2},4:{p_atk_pct:3},5:{speed_pct:3},6:{p_atk_pct:4}},p:{3:"+8% de chance d'esquive supplémentaires (cumul avec le passif de classe).",7:"Après une esquive réussie, ta prochaine attaque inflige +40% dégâts et est toujours un critique."}},
  assassin_donjon_abyssal:{n:"Voile de Sang",c:"Assassin",s:"donjon_abyssal",t:{2:{p_atk_pct:2},4:{p_pen_pct:3},5:{p_atk_pct:3},6:{p_pen_pct:4}},p:{3:"Chaque critique applique une saignée (1% HP max/tour, 3 tours). Stackable.",7:"La saignée monte à 3% HP max/tour et stack jusqu'à 3 fois. Ennemis saignants subissent +10% dégâts physiques."}},
  assassin_raid:{n:"Exécuteur des Ombres",c:"Assassin",s:"raid",t:{2:{p_atk_pct:2},4:{speed_pct:3},5:{p_atk_pct:3},6:{p_pen_pct:4}},p:{3:"Dégâts +20% sur les cibles à moins de 30% HP.",7:"Dégâts +40% sur ennemis à moins de 20% HP. Chaque coup critique régénère 2 combo."}},
  mage_monde:{n:"Novice Arcane",c:"Mage",s:"monde",t:{2:{m_atk_pct:2},4:{m_pen_pct:3},5:{m_atk_pct:3},6:{m_atk_pct:4}},p:{3:"Tes sorts ont 10% de chance de ne pas consommer de tour.",7:"Chaque sort lancé augmente ton ATK Magique de 2% (max +20%). Reset à chaque combat."}},
  mage_donjon_classique:{n:"Manteau Astral",c:"Mage",s:"donjon_classique",t:{2:{hp_pct:2},4:{m_def_pct:3},5:{m_atk_pct:3},6:{hp_pct:4}},p:{3:"+0,2% dégâts magiques par % de HP actuels (max +20%).",7:"À plein HP : +30% dégâts magiques. Le passif de classe commence à +0,8%/% HP."}},
  mage_craft:{n:"Tissu Enchanté",c:"Mage",s:"craft",t:{2:{m_atk_pct:2},4:{m_pen_pct:3},5:{m_atk_pct:3},6:{m_atk_pct:4}},p:{3:"Chaque sort accumule 1 charge de Focale. À 3 charges, la prochaine attaque est un critique garanti.",7:"Les critiques magiques infligent +20% dégâts supplémentaires et réinitialisent les charges de Focale."}},
  mage_donjon_elite:{n:"Voile du Prophète",c:"Mage",s:"donjon_elite",t:{2:{m_pen_pct:2},4:{m_atk_pct:3},5:{m_pen_pct:3},6:{m_pen_pct:4}},p:{3:"Ignore 10% de la DEF Magique ennemie.",7:"Ignore 25% DEF Magique ennemie. Chaque 3e sort inflige +60% dégâts magiques."}},
  mage_donjon_abyssal:{n:"Suaire Primordial",c:"Mage",s:"donjon_abyssal",t:{2:{m_atk_pct:2},4:{m_pen_pct:3},5:{m_atk_pct:3},6:{m_atk_pct:4}},p:{3:"Tes critiques magiques appliquent une brûlure arcane (5% ATK Magique/tour, 2 tours).",7:"Brûlure arcane monte à 10% ATK Magique/tour. Réduit aussi la DEF Magique ennemie de 12% pour 2 tours."}},
  mage_raid:{n:"Nexus Primordial",c:"Mage",s:"raid",t:{2:{m_atk_pct:2},4:{m_pen_pct:3},5:{m_atk_pct:3},6:{m_atk_pct:4}},p:{3:"+25% dégâts magiques sur les ennemis avec moins de 50% HP.",7:"+25% dégâts magiques permanents. Sorts brûlent l'ennemi (5% ATK Magique/tour, 2 tours). 15% de chance de rejouer."}},
  tireur_monde:{n:"Carquois de Chasse",c:"Tireur",s:"monde",t:{2:{speed_pct:2},4:{p_atk_pct:3},5:{speed_pct:3},6:{p_atk_pct:4}},p:{3:"+8% de chance de double coup supplémentaires.",7:"Chaque double coup inflige +15% dégâts sur le second tir. Si Vitesse > ennemi : double coup garanti."}},
  tireur_donjon_classique:{n:"Arc du Faucon",c:"Tireur",s:"donjon_classique",t:{2:{p_atk_pct:2},4:{p_pen_pct:3},5:{p_atk_pct:3},6:{p_atk_pct:4}},p:{3:"Le double coup a 25% de chance de devenir un triple coup.",7:"Triple coup disponible à chaque attaque (25%). Chaque coup supplémentaire inflige +10% dégâts additionnels."}},
  tireur_craft:{n:"Bois Taillé",c:"Tireur",s:"craft",t:{2:{p_atk_pct:2},4:{p_pen_pct:3},5:{p_atk_pct:3},6:{p_atk_pct:4}},p:{3:"Chaque attaque consécutive sans rater de critique ajoute +3% dégâts (max +30%).",7:"À 10 critiques consécutifs, ta prochaine attaque est un tir chargé : +100% dégâts et ignore la DEF Physique."}},
  tireur_donjon_elite:{n:"Tempête d'Acier",c:"Tireur",s:"donjon_elite",t:{2:{speed_pct:2},4:{p_atk_pct:3},5:{speed_pct:3},6:{p_atk_pct:4}},p:{3:"Attaque toujours en premier si vitesse égale à l'ennemi.",7:"Chaque double coup réduit la vitesse ennemie de 12%. +30% dégâts sur cibles ralenties."}},
  tireur_donjon_abyssal:{n:"Œil de l'Horizon",c:"Tireur",s:"donjon_abyssal",t:{2:{p_atk_pct:2},4:{p_pen_pct:3},5:{p_atk_pct:3},6:{p_pen_pct:4}},p:{3:"Dégâts critiques +20% supplémentaires.",7:"Si critique lors d'un double coup, les deux tirs sont critiques. +30% dégâts sur cibles à moins de 50% HP."}},
  tireur_raid:{n:"Ouragan d'Acier",c:"Tireur",s:"raid",t:{2:{p_atk_pct:2},4:{speed_pct:3},5:{p_atk_pct:3},6:{p_pen_pct:4}},p:{3:"+30% dégâts physiques. Double coup garanti au premier tour.",7:"Triple coup possible à chaque attaque (25%). Double coup garanti à chaque tour. Chaque tir supplémentaire +15% dégâts."}},
  support_monde:{n:"Médaillon du Novice",c:"Support",s:"monde",t:{2:{hp_pct:2},4:{p_def_pct:3},5:{m_def_pct:3},6:{hp_pct:4}},p:{3:"+5% de chance de bouclier supplémentaires. Le bouclier absorbe 10% HP max.",7:"Si bouclier actif en début de tour, régénère 3% HP max. Bouclier = 12% HP max."}},
  support_donjon_classique:{n:"Armure du Défenseur",c:"Support",s:"donjon_classique",t:{2:{p_def_pct:2},4:{m_def_pct:3},5:{p_def_pct:3},6:{m_def_pct:4}},p:{3:"Chaque bouclier généré augmente tes dégâts de 8% pour le tour suivant.",7:"Les boucliers durent 2 tours. Un bouclier actif augmente tes dégâts de 15% en permanence."}},
  support_craft:{n:"Métal Béni",c:"Support",s:"craft",t:{2:{hp_pct:2},4:{m_def_pct:3},5:{hp_pct:3},6:{m_def_pct:4}},p:{3:"Le bouclier absorbe également 40% des dégâts magiques reçus.",7:"Le bouclier absorbe 70% des dégâts magiques. Réduit les dégâts reçus de 5% supplémentaires."}},
  support_donjon_elite:{n:"Bénédiction Sacrée",c:"Support",s:"donjon_elite",t:{2:{hp_pct:2},4:{p_def_pct:3},5:{m_def_pct:3},6:{hp_pct:4}},p:{3:"Si le bouclier tient 2 tours, il explose et inflige 10% de tes HP max en dégâts purs.",7:"Bouclier explosif monte à 18% HP max. L'explosion réduit la vitesse ennemie de 15% pour 2 tours."}},
  support_donjon_abyssal:{n:"Bouclier du Gardien",c:"Support",s:"donjon_abyssal",t:{2:{p_def_pct:2},4:{m_def_pct:3},5:{hp_pct:3},6:{p_def_pct:4}},p:{3:"Chaque bouclier généré soigne 4% HP max.",7:"Bouclier = 14% HP max et soigne 6% HP max à la génération. Réduit les dégâts reçus de 15%."}},
  support_raid:{n:"Lumière Éternelle",c:"Support",s:"raid",t:{2:{hp_pct:2},4:{p_def_pct:3},5:{m_def_pct:3},6:{hp_pct:4}},p:{3:"Bouclier = 15% HP max. +20% HP max total.",7:"Bouclier se régénère toutes les 2 tours. Si bouclier actif : soin 4% HP max/tour et -12% dégâts reçus."}},
  vampire_monde:{n:"Crocs de la Nuit",c:"Vampire",s:"monde",t:{2:{p_atk_pct:2},4:{hp_pct:3},5:{p_atk_pct:3},6:{p_atk_pct:4}},p:{3:"+8% vol de vie supplémentaires (total 33%).",7:"Le vol de vie génère aussi un bouclier de 20% du soin effectué. +5% vol de vie supplémentaires."}},
  vampire_donjon_classique:{n:"Manteau Maudit",c:"Vampire",s:"donjon_classique",t:{2:{p_atk_pct:2},4:{hp_pct:3},5:{p_atk_pct:3},6:{p_atk_pct:4}},p:{3:"Chaque critique draine 5% HP max ennemi directement (en plus du vol de vie normal).",7:"Drain critique monte à 8% HP max. 3 critiques consécutifs → régénère 15% HP max instantanément."}},
  vampire_craft:{n:"Acier Ensanglanté",c:"Vampire",s:"craft",t:{2:{speed_pct:2},4:{p_atk_pct:3},5:{speed_pct:3},6:{p_atk_pct:4}},p:{3:"Le vol de vie génère un bouclier pour 50% du soin reçu.",7:"Bouclier du vol de vie monte à 80% du soin. Si bouclier actif, +15% dégâts physiques."}},
  vampire_donjon_elite:{n:"Suaire des Ténèbres",c:"Vampire",s:"donjon_elite",t:{2:{hp_pct:2},4:{p_atk_pct:3},5:{hp_pct:3},6:{p_atk_pct:4}},p:{3:"Si HP > 80% : +20% dégâts. Vol de vie augmenté de +10%.",7:"Régénère 3% HP max/tour. Vol de vie total = 40%. Si HP > 80%, +30% dégâts physiques."}},
  vampire_donjon_abyssal:{n:"Seigneur des Ténèbres",c:"Vampire",s:"donjon_abyssal",t:{2:{p_atk_pct:2},4:{p_pen_pct:3},5:{p_atk_pct:3},6:{p_atk_pct:4}},p:{3:"Chaque critique pompe 4% HP max ennemi directement.",7:"Drain critique monte à 6% HP max. Dégâts +20% sur cibles à moins de 50% HP. Vol de vie +15%."}},
  vampire_raid:{n:"Prince Immortel",c:"Vampire",s:"raid",t:{2:{p_atk_pct:2},4:{hp_pct:3},5:{p_atk_pct:3},6:{p_pen_pct:4}},p:{3:"Vol de vie = 40% dégâts. +10% dégâts par 10% HP manquants (cumul avec passif de classe).",7:"Une fois par combat, si tu meurs, reviens à 25% HP et soigne via le vol de vie sur le prochain coup."}},
  gardien_monde:{n:"Brisé",c:"Gardien du Temps",s:"monde",t:{2:{speed_pct:2},4:{m_atk_pct:3},5:{p_atk_pct:3},6:{speed_pct:4}},p:{3:"Les debuffs de réduction de stats durent 1 tour supplémentaire.",7:"Les debuffs actifs sur l'ennemi augmentent tes dégâts de 3% chacun (max +30%)."}},
  gardien_donjon_classique:{n:"Horloge Fractale",c:"Gardien du Temps",s:"donjon_classique",t:{2:{p_atk_pct:2},4:{m_atk_pct:3},5:{p_atk_pct:3},6:{m_atk_pct:4}},p:{3:"25% de chance de réduire 2 stats ennemies au lieu d'une par tour.",7:"Chance de double debuff monte à 40%. Chaque stat réduite amplifie tes dégâts de 4%."}},
  gardien_craft:{n:"Tissu Temporel",c:"Gardien du Temps",s:"craft",t:{2:{hp_pct:2},4:{p_atk_pct:3},5:{m_atk_pct:3},6:{hp_pct:4}},p:{3:"Au début du combat, réduit immédiatement 2 stats ennemies de 8% chacune.",7:"Début de combat : réduit 3 stats ennemies de 8% pour toute la durée du combat."}},
  gardien_donjon_elite:{n:"Chrono Maudit",c:"Gardien du Temps",s:"donjon_elite",t:{2:{p_atk_pct:2},4:{m_atk_pct:3},5:{p_atk_pct:3},6:{m_atk_pct:4}},p:{3:"Les stats réduites de l'ennemi ne peuvent pas être restaurées pendant le combat.",7:"Debuffs permanents ET chaque nouvelle réduction s'ajoute sans limite de -50%."}},
  gardien_donjon_abyssal:{n:"Paradoxe Temporel",c:"Gardien du Temps",s:"donjon_abyssal",t:{2:{p_atk_pct:2},4:{m_atk_pct:3},5:{speed_pct:3},6:{p_atk_pct:4}},p:{3:"Chaque 10% de stat réduite chez l'ennemi t'octroie +5% dégâts (max +50%).",7:"À -50% de réduction, l'ennemi perd 1 action par tour. Dégâts doublés contre les ennemis à -50%."}},
  gardien_raid:{n:"Maître du Destin",c:"Gardien du Temps",s:"raid",t:{2:{p_atk_pct:2},4:{m_atk_pct:3},5:{speed_pct:3},6:{p_atk_pct:4}},p:{3:"Réduction max passe à 75%. Chaque debuff appliqué soigne 3% HP max.",7:"Dégâts +15% par debuff actif (max +60%). L'ennemi à -75% perd 1 action par tour. Dégâts non-esquivables."}},
  ombre_monde:{n:"Distillat Vénéneux",c:"Ombre Venin",s:"monde",t:{2:{p_atk_pct:2},4:{m_atk_pct:3},5:{p_atk_pct:3},6:{p_atk_pct:4}},p:{3:"Le poison inflige +1% HP max ennemi/tour supplémentaire (4% au lieu de 3%).",7:"Le poison monte à 5% HP max/tour. Chaque tour empoisonné, l'ennemi subit -2% à une stat aléatoire."}},
  ombre_donjon_classique:{n:"Aiguille Toxique",c:"Ombre Venin",s:"donjon_classique",t:{2:{speed_pct:2},4:{p_atk_pct:3},5:{speed_pct:3},6:{p_atk_pct:4}},p:{3:"30% de chance d'appliquer une dose de poison supplémentaire par attaque.",7:"Chaque attaque empoisonne à coup sûr. Le poison s'applique avant les dégâts physiques."}},
  ombre_craft:{n:"Venin Distillé",c:"Ombre Venin",s:"craft",t:{2:{p_atk_pct:2},4:{m_atk_pct:3},5:{p_atk_pct:3},6:{p_pen_pct:4}},p:{3:"Le premier poison appliqué inflige directement 8% HP max en dégâts instantanés.",7:"Chaque re-application de poison inflige +5% HP max instantanément. Stack infini."}},
  ombre_donjon_elite:{n:"Brume Toxique",c:"Ombre Venin",s:"donjon_elite",t:{2:{p_atk_pct:2},4:{p_pen_pct:3},5:{p_atk_pct:3},6:{p_atk_pct:4}},p:{3:"Chaque critique applique automatiquement 1 dose de poison.",7:"Le poison appliqué par les critiques inflige 6% HP max/tour. Dégâts critiques +15% sur cibles empoisonnées."}},
  ombre_donjon_abyssal:{n:"Essence Corrompue",c:"Ombre Venin",s:"donjon_abyssal",t:{2:{p_atk_pct:2},4:{m_pen_pct:3},5:{p_atk_pct:3},6:{p_pen_pct:4}},p:{3:"Le poison réduit la DEF Physique et DEF Magique ennemies de 5%/tour de poison actif (max -25%).",7:"Réduction DEF du poison monte à 8%/tour (max -40%). Dégâts physiques +15% sur cibles avec DEF réduite."}},
  ombre_raid:{n:"Nécrosis Primordiale",c:"Ombre Venin",s:"raid",t:{2:{p_atk_pct:2},4:{m_pen_pct:3},5:{p_atk_pct:3},6:{p_pen_pct:4}},p:{3:"Le poison peut stacker 3 fois (3% + 6% + 9% HP max ennemi/tour).",7:"Au max de stacks, nécrosis : perd 20% HP max/tour et toutes ses stats sont réduites de 15%."}},
  pyro_monde:{n:"Tison Ardent",c:"Pyromancien",s:"monde",t:{2:{m_atk_pct:2},4:{m_pen_pct:3},5:{m_atk_pct:3},6:{m_atk_pct:4}},p:{3:"La brûlure peut monter jusqu'à 6 stacks au lieu de 5.",7:"La brûlure inflige +2% ATK Magique/stack supplémentaires. Au max, inflige instantanément 20% ATK Magique."}},
  pyro_donjon_classique:{n:"Flamme Enflammée",c:"Pyromancien",s:"donjon_classique",t:{2:{m_atk_pct:2},4:{m_pen_pct:3},5:{m_atk_pct:3},6:{m_atk_pct:4}},p:{3:"Chaque critique ajoute automatiquement 1 stack de brûlure.",7:"Les critiques appliquent 2 stacks de brûlure au lieu d'1. Dégâts critiques +10% par stack actif."}},
  pyro_craft:{n:"Pierre Incandescente",c:"Pyromancien",s:"craft",t:{2:{m_atk_pct:2},4:{m_pen_pct:3},5:{m_atk_pct:3},6:{m_atk_pct:4}},p:{3:"Tes sorts ont 20% de chance d'appliquer directement 2 stacks de brûlure.",7:"ATK Magique +3% par stack de brûlure actif. Sorts : 30% de chance d'appliquer 2 stacks. Double lancé 10%."}},
  pyro_donjon_elite:{n:"Brasier Infernal",c:"Pyromancien",s:"donjon_elite",t:{2:{m_atk_pct:2},4:{m_pen_pct:3},5:{m_atk_pct:3},6:{m_atk_pct:4}},p:{3:"La brûlure dure 1 tour supplémentaire avant de se dissiper.",7:"La brûlure ne se dissipe jamais tant que l'ennemi reste en vie. À 5 stacks, l'ennemi perd 4 points de speed/tour."}},
  pyro_donjon_abyssal:{n:"Âme Volcanique",c:"Pyromancien",s:"donjon_abyssal",t:{2:{m_atk_pct:2},4:{m_pen_pct:3},5:{m_atk_pct:3},6:{m_atk_pct:4}},p:{3:"Au max de stacks, l'ennemi subit +20% dégâts magiques supplémentaires.",7:"Brûlure max = 7 stacks. Au max, la brûlure inflige 25% ATK Magique/stack. Chaque critique ajoute 1 stack."}},
  pyro_raid:{n:"Phénix Éternel",c:"Pyromancien",s:"raid",t:{2:{m_atk_pct:2},4:{m_pen_pct:3},5:{m_atk_pct:3},6:{m_atk_pct:4}},p:{3:"Brûlure max = 8 stacks. Au max, l'ennemi prend +30% dégâts magiques.",7:"Une fois par combat, si tu meurs, ressuscite à 30% HP et applique immédiatement 8 stacks de brûlure."}},
  paladin_monde:{n:"Armure Consacrée",c:"Paladin",s:"monde",t:{2:{hp_pct:2},4:{p_def_pct:3},5:{hp_pct:3},6:{p_def_pct:4}},p:{3:"Le ramp du passif démarre à +5% dès le tour 1 au lieu de 0%.",7:"Le ramp démarre à +10%. Régénère 2% HP max/tour grâce à la foi."}},
  paladin_donjon_classique:{n:"Vœu du Croisé",c:"Paladin",s:"donjon_classique",t:{2:{p_atk_pct:2},4:{p_def_pct:3},5:{m_def_pct:3},6:{p_atk_pct:4}},p:{3:"Le ramp augmente de +4% par tour au lieu de +3% (max atteint plus vite).",7:"Ramp à +4%/tour. Le ramp offensif s'applique aussi aux dégâts magiques."}},
  paladin_craft:{n:"Métal Sanctifié",c:"Paladin",s:"craft",t:{2:{hp_pct:2},4:{p_def_pct:3},5:{m_def_pct:3},6:{hp_pct:4}},p:{3:"Réduit les dégâts reçus de 4% supplémentaires par tour de combat (max -30%).",7:"+8% au ramp défensif de départ. La réduction dégâts par tour ne plafonne plus à -30% mais à -45%."}},
  paladin_donjon_elite:{n:"Lumière Divine",c:"Paladin",s:"donjon_elite",t:{2:{hp_pct:2},4:{p_def_pct:3},5:{m_def_pct:3},6:{hp_pct:4}},p:{3:"Le ramp max passe à +40%/+40% en réduction et dégâts.",7:"Ramp max +40%. Dégâts sacrés : tes attaques ignorent 10% DEF ennemie quand le ramp est au max."}},
  paladin_donjon_abyssal:{n:"Bouclier de la Foi",c:"Paladin",s:"donjon_abyssal",t:{2:{p_def_pct:2},4:{m_def_pct:3},5:{hp_pct:3},6:{p_def_pct:4}},p:{3:"La réduction de dégâts du ramp s'applique aussi aux dégâts purs.",7:"Dégâts purs réduits par le ramp. Reflète 15% des dégâts reçus à l'ennemi."}},
  paladin_raid:{n:"Avatar Sacré",c:"Paladin",s:"raid",t:{2:{hp_pct:2},4:{p_def_pct:3},5:{m_def_pct:3},6:{hp_pct:4}},p:{3:"Ramp max +50%/+50%. Le ramp ne se réinitialise pas entre les vagues de donjon.",7:"Une fois par combat, reflète 30% des dégâts reçus. Au max du ramp, chaque attaque soigne 5% HP max."}}
};

window.setSimulate=function(){
  const id=document.getElementById('set-id').value;
  const pcs=parseInt(document.getElementById('set-pcs').value);
  const rar=parseFloat(document.getElementById('set-rarity').value);
  const set=SETS[id];
  if(!set){document.getElementById('set-result').innerHTML='';return;}
  const srcMult=SET_SRC_MULT[set.s]||1.0;
  let html=`<div style="font-size:.85em;margin-bottom:10px;opacity:.7">${set.c} — ${SET_SRC_LABEL[set.s]}</div>`;
  const TIER_LABELS={2:"2 pièces",3:"3 pièces",4:"4 pièces",5:"5 pièces",6:"6 pièces",7:"7 pièces"};
  let hasAny=false;
  for(let tier=2;tier<=7;tier++){
    if(pcs<tier)break;
    const statData=set.t[tier];
    const passData=set.p[tier];
    hasAny=true;
    html+=`<div style="padding:8px 10px;margin-bottom:6px;border-radius:6px;background:var(--md-default-fg-color--lightest,rgba(0,0,0,.06));border-left:3px solid #4CAF50">`;
    html+=`<strong style="font-size:.85em;opacity:.7">${TIER_LABELS[tier]}</strong><br>`;
    if(statData){
      for(const[k,base]of Object.entries(statData)){
        const real=(base*srcMult*rar).toFixed(2);
        html+=`<span style="font-size:1.05em;font-weight:600">+${real}% ${SET_PCT_FR[k]||k}</span>`;
        html+=`<span style="font-size:.8em;opacity:.6"> (base ${base}% × ×${srcMult.toFixed(1)} × ×${rar.toFixed(1)})</span>`;
      }
    }
    if(passData){
      html+=`<span style="font-size:.9em;font-style:italic">📜 ${passData}</span>`;
    }
    html+='</div>';
  }
  if(!hasAny)html+='<em>Équipe au moins 2 pièces pour voir les bonus.</em>';
  document.getElementById('set-result').innerHTML=html;
};
setSimulate();
})();
</script>

---

## Les panoplies (sets)

Une panoplie est un **ensemble de 7 pièces** liées entre elles. Équiper plusieurs pièces d'une même panoplie débloque des **bonus de set** progressifs :

| Pièces équipées | Bonus débloqué |
|-----------------|---------------|
| 2 pièces | +2% d'une stat (valeur de base) |
| 3 pièces | Passif spécial |
| 4 pièces | +3% d'une stat (valeur de base) |
| 5 pièces | +3% d'une stat (valeur de base) |
| 6 pièces | +4% d'une stat (valeur de base) |
| 7 pièces | Passif ultime |

!!! warning "La rareté de la pièce la plus faible limite TOUTE la panoplie"
    La formule exacte des bonus de set est :

    **Bonus réel (%) = valeur de base × multiplicateur de source × multiplicateur de rareté**

    La rareté utilisée dans ce calcul est celle de la **pièce la moins rare** dans ton set. Si tu portes 6 pièces Légendaires et 1 pièce Commune, tous les bonus de set sont calculés comme si tu portais du **Commun**.

    **Exemple :** Panoplie Colosse de Guerre (Raid ×1,8), bonus 2 pièces = +2% HP (base). Avec rareté min Épique (×1,6) → **+5,76% HP réels**. Avec rareté min Prismatique (×3,0) → **+10,8% HP réels**.

---

## Toutes les panoplies par classe

=== "⚔️ Guerrier"

    Le Guerrier est un combattant physique polyvalent — certains builds axent sur la survie, d'autres sur la contre-attaque ou le burst.

    **Emplacements :** Heaume · Cuirasse · Braies · Sollerets · Épée · Médaillon · Chevalière

    | Panoplie | Source | Passif 3 pièces | Passif 7 pièces |
    |----------|--------|-----------------|-----------------|
    | **Acier de Fer** | Monde | Régénère 2% HP max à chaque fin de tour. | Chaque ennemi vaincu régénère 8% HP max. +5% dégâts physiques. |
    | **Rempart de Fer** | Donjon Classique | Réduit les dégâts reçus de 5%. | Immunisé aux réductions de stats ennemies. Chaque attaque reçue régénère 2% HP max. |
    | **Métal Forgé** | Craft | Chaque attaque physique reçue augmente tes dégâts de 2% (max +20%). | Contre-attaque : après avoir reçu un coup, 25% de chance de riposter avec 60% ATK Physique. |
    | **Titan Écarlate** | Donjon Élite | Si HP < 50% : tes dégâts physiques sont augmentés de 12%. | +2% dégâts physiques par 5% HP manquants. Dégâts critiques +30% quand HP < 30%. |
    | **Seigneur de l'Abîme** | Donjon Abyssal | Ignore 10% de la DEF Physique ennemie. | Ignore 25% DEF Physique ennemie. Chaque critique régénère 4% HP max. |
    | **Colosse de Guerre** | Raid | +10% dégâts physiques et +5% réduction dégâts reçus. | Immunité aux stun. +20% dégâts quand HP < 30%. Régénère 5% HP max/tour. |

    ??? info "Bonus de stats (2 / 4 / 5 / 6 pièces) — valeurs de base"
        Les valeurs indiquées sont des **bases** (Commun, Monde). Multipliez par rareté min × source pour le bonus réel.

        | Panoplie | 2 pcs | 4 pcs | 5 pcs | 6 pcs |
        |----------|-------|-------|-------|-------|
        | Acier de Fer | +2% HP | +3% Déf. Phy. | +3% HP | +4% Déf. Phy. |
        | Rempart de Fer | +2% Déf. Phy. | +3% Déf. Mag. | +3% Déf. Phy. | +4% Déf. Mag. |
        | Métal Forgé | +2% ATK Phy. | +3% Pén. Phy. | +3% HP | +4% ATK Phy. |
        | Titan Écarlate | +2% ATK Phy. | +3% Pén. Phy. | +3% ATK Phy. | +4% ATK Phy. |
        | Seigneur de l'Abîme | +2% ATK Phy. | +3% Pén. Phy. | +3% ATK Phy. | +4% Pén. Phy. |
        | Colosse de Guerre | +2% HP | +3% ATK Phy. | +3% Pén. Phy. | +4% HP |

=== "🗡️ Assassin"

    L'Assassin frappe vite et fort — ses builds exploitent les critiques, l'esquive ou la saignée.

    **Emplacements :** Capuche · Mantelet · Grègues · Chaussons · Dague · Pendentif · Signet

    | Panoplie | Source | Passif 3 pièces | Passif 7 pièces |
    |----------|--------|-----------------|-----------------|
    | **Ombre Légère** | Monde | Le premier coup de chaque combat est toujours un critique. | Le premier coup inflige +25% dégâts. Si l'ennemi est à plein HP : +50%. |
    | **Lame du Crépuscule** | Donjon Classique | Chaque critique consécutif augmente ton crit_damage de 5% (max +25%). | Après 3 critiques consécutifs, ta prochaine attaque ignore toute la DEF Physique ennemie. |
    | **Acier Trempé** | Craft | Chaque esquive réussie augmente tes dégâts de 6% pour 2 tours (max +30%). | Après une esquive, +15% de chance d'esquiver le prochain coup. Dégâts +40% si esquive active. |
    | **Fantôme Acéré** | Donjon Élite | +8% de chance d'esquive supplémentaires (cumul avec le passif de classe). | Après esquive réussie, ta prochaine attaque inflige +40% dégâts et est toujours un critique. |
    | **Voile de Sang** | Donjon Abyssal | Chaque critique applique une saignée (1% HP max/tour, 3 tours). Stackable. | La saignée monte à 3% HP max/tour et stack jusqu'à 3 fois. Ennemis saignants subissent +10% dégâts physiques. |
    | **Exécuteur des Ombres** | Raid | Dégâts +20% sur les cibles à moins de 30% HP. | Dégâts +40% sur ennemis à moins de 20% HP. Chaque coup critique régénère 2 combo. |

    ??? info "Bonus de stats (2 / 4 / 5 / 6 pièces) — valeurs de base"
        | Panoplie | 2 pcs | 4 pcs | 5 pcs | 6 pcs |
        |----------|-------|-------|-------|-------|
        | Ombre Légère | +2% Vit. | +3% ATK Phy. | +3% Vit. | +4% ATK Phy. |
        | Lame du Crépuscule | +2% ATK Phy. | +3% Pén. Phy. | +3% ATK Phy. | +4% ATK Phy. |
        | Acier Trempé | +2% Vit. | +3% ATK Phy. | +3% Vit. | +4% ATK Phy. |
        | Fantôme Acéré | +2% Vit. | +3% ATK Phy. | +3% Vit. | +4% ATK Phy. |
        | Voile de Sang | +2% ATK Phy. | +3% Pén. Phy. | +3% ATK Phy. | +4% Pén. Phy. |
        | Exécuteur des Ombres | +2% ATK Phy. | +3% Vit. | +3% ATK Phy. | +4% Pén. Phy. |

=== "🔮 Mage"

    Le Mage inflige des dégâts magiques massifs — builds axés sur le burst, la pénétration, ou la survie via les HP.

    **Emplacements :** Chapeau · Robe · Jupe · Sandales · Bâton · Talisman · Bague

    | Panoplie | Source | Passif 3 pièces | Passif 7 pièces |
    |----------|--------|-----------------|-----------------|
    | **Novice Arcane** | Monde | Tes sorts ont 10% de chance de ne pas consommer de tour. | Chaque sort lancé augmente ATK Magique de 2% (max +20%). Reset à chaque combat. |
    | **Manteau Astral** | Donjon Classique | +0,2% dégâts magiques par % de HP actuels (max +20%). | À plein HP : +30% dégâts magiques. Le passif de classe commence à +0,8%/% HP. |
    | **Tissu Enchanté** | Craft | Chaque sort accumule 1 charge de Focale. À 3 charges, la prochaine attaque est un critique garanti. | Les critiques magiques infligent +20% dégâts supplémentaires et réinitialisent les charges de Focale. |
    | **Voile du Prophète** | Donjon Élite | Ignore 10% de la DEF Magique ennemie. | Ignore 25% DEF Magique ennemie. Chaque 3e sort inflige +60% dégâts magiques. |
    | **Suaire Primordial** | Donjon Abyssal | Tes critiques magiques appliquent une brûlure arcane (5% ATK Magique/tour, 2 tours). | Brûlure arcane monte à 10% ATK Magique/tour. Réduit DEF Magique ennemie de 12% pour 2 tours. |
    | **Nexus Primordial** | Raid | +25% dégâts magiques sur les ennemis avec moins de 50% HP. | +25% dégâts magiques permanents. Sorts brûlent l'ennemi (5% ATK Mag/tour). 15% de rejouer. |

    ??? info "Bonus de stats (2 / 4 / 5 / 6 pièces) — valeurs de base"
        | Panoplie | 2 pcs | 4 pcs | 5 pcs | 6 pcs |
        |----------|-------|-------|-------|-------|
        | Novice Arcane | +2% ATK Mag. | +3% Pén. Mag. | +3% ATK Mag. | +4% ATK Mag. |
        | Manteau Astral | +2% HP | +3% Déf. Mag. | +3% ATK Mag. | +4% HP |
        | Tissu Enchanté | +2% ATK Mag. | +3% Pén. Mag. | +3% ATK Mag. | +4% ATK Mag. |
        | Voile du Prophète | +2% Pén. Mag. | +3% ATK Mag. | +3% Pén. Mag. | +4% Pén. Mag. |
        | Suaire Primordial | +2% ATK Mag. | +3% Pén. Mag. | +3% ATK Mag. | +4% ATK Mag. |
        | Nexus Primordial | +2% ATK Mag. | +3% Pén. Mag. | +3% ATK Mag. | +4% ATK Mag. |

=== "🏹 Tireur"

    Le Tireur mise sur la vitesse et les attaques multiples (double/triple coups) pour surpasser ses adversaires.

    **Emplacements :** Cagoule · Veste · Jambières · Bottes · Arc · Collier · Jonc

    | Panoplie | Source | Passif 3 pièces | Passif 7 pièces |
    |----------|--------|-----------------|-----------------|
    | **Carquois de Chasse** | Monde | +8% de chance de double coup supplémentaires. | Chaque double coup inflige +15% dégâts sur le 2e tir. Si Vitesse > ennemi : double coup garanti. |
    | **Arc du Faucon** | Donjon Classique | Le double coup a 25% de chance de devenir un triple coup. | Triple coup (25%) disponible à chaque attaque. Chaque coup suppl. inflige +10% dégâts additionnels. |
    | **Bois Taillé** | Craft | Chaque attaque consécutive sans rater de critique ajoute +3% dégâts (max +30%). | À 10 critiques consécutifs : tir chargé (+100% dégâts, ignore la DEF Physique). |
    | **Tempête d'Acier** | Donjon Élite | Attaque toujours en premier si vitesse égale à l'ennemi. | Chaque double coup réduit la vitesse ennemie de 12%. +30% dégâts sur cibles ralenties. |
    | **Œil de l'Horizon** | Donjon Abyssal | Dégâts critiques +20% supplémentaires. | Si critique lors d'un double coup, les deux tirs sont critiques. +30% dégâts sur cibles à moins de 50% HP. |
    | **Ouragan d'Acier** | Raid | +30% dégâts physiques. Double coup garanti au premier tour. | Triple coup à chaque attaque (25%). Double coup garanti/tour. Chaque tir suppl. +15% dégâts. |

    ??? info "Bonus de stats (2 / 4 / 5 / 6 pièces) — valeurs de base"
        | Panoplie | 2 pcs | 4 pcs | 5 pcs | 6 pcs |
        |----------|-------|-------|-------|-------|
        | Carquois de Chasse | +2% Vit. | +3% ATK Phy. | +3% Vit. | +4% ATK Phy. |
        | Arc du Faucon | +2% ATK Phy. | +3% Pén. Phy. | +3% ATK Phy. | +4% ATK Phy. |
        | Bois Taillé | +2% ATK Phy. | +3% Pén. Phy. | +3% ATK Phy. | +4% ATK Phy. |
        | Tempête d'Acier | +2% Vit. | +3% ATK Phy. | +3% Vit. | +4% ATK Phy. |
        | Œil de l'Horizon | +2% ATK Phy. | +3% Pén. Phy. | +3% ATK Phy. | +4% Pén. Phy. |
        | Ouragan d'Acier | +2% ATK Phy. | +3% Vit. | +3% ATK Phy. | +4% Pén. Phy. |

=== "🛡️ Support"

    Le Support génère des boucliers et mélange défense et dégâts explosifs.

    **Emplacements :** Bassinet · Brigandine · Cuissardes · Grèves · Bouclier · Amulette · Sceau

    | Panoplie | Source | Passif 3 pièces | Passif 7 pièces |
    |----------|--------|-----------------|-----------------|
    | **Médaillon du Novice** | Monde | +5% de chance de bouclier supplémentaires. Le bouclier absorbe 10% HP max. | Si bouclier actif en début de tour, régénère 3% HP max. Bouclier = 12% HP max. |
    | **Armure du Défenseur** | Donjon Classique | Chaque bouclier généré augmente tes dégâts de 8% pour le tour suivant. | Les boucliers durent 2 tours. Un bouclier actif augmente tes dégâts de 15% en permanence. |
    | **Métal Béni** | Craft | Le bouclier absorbe également 40% des dégâts magiques reçus. | Le bouclier absorbe 70% des dégâts magiques. Réduit les dégâts reçus de 5% suppl. |
    | **Bénédiction Sacrée** | Donjon Élite | Si le bouclier tient 2 tours, il explose et inflige 10% de tes HP max en dégâts purs. | Bouclier explosif = 18% HP max. L'explosion réduit la vitesse ennemie de 15% pour 2 tours. |
    | **Bouclier du Gardien** | Donjon Abyssal | Chaque bouclier généré soigne 4% HP max. | Bouclier = 14% HP max et soigne 6% HP max à la génération. Réduit les dégâts reçus de 15%. |
    | **Lumière Éternelle** | Raid | Bouclier = 15% HP max. +20% HP max total. | Bouclier se régénère toutes les 2 tours. Si bouclier actif : soin 4% HP max/tour et -12% dégâts reçus. |

    ??? info "Bonus de stats (2 / 4 / 5 / 6 pièces) — valeurs de base"
        | Panoplie | 2 pcs | 4 pcs | 5 pcs | 6 pcs |
        |----------|-------|-------|-------|-------|
        | Médaillon du Novice | +2% HP | +3% Déf. Phy. | +3% Déf. Mag. | +4% HP |
        | Armure du Défenseur | +2% Déf. Phy. | +3% Déf. Mag. | +3% Déf. Phy. | +4% Déf. Mag. |
        | Métal Béni | +2% HP | +3% Déf. Mag. | +3% HP | +4% Déf. Mag. |
        | Bénédiction Sacrée | +2% HP | +3% Déf. Phy. | +3% Déf. Mag. | +4% HP |
        | Bouclier du Gardien | +2% Déf. Phy. | +3% Déf. Mag. | +3% HP | +4% Déf. Phy. |
        | Lumière Éternelle | +2% HP | +3% Déf. Phy. | +3% Déf. Mag. | +4% HP |

=== "🦇 Vampire"

    Le Vampire vole de la vie à chaque frappe — builds orientés drain, survie ou burst avec bouclier.

    **Emplacements :** Masque · Cape · Collant · Bottines · Crocs · Breloque · Cachet

    | Panoplie | Source | Passif 3 pièces | Passif 7 pièces |
    |----------|--------|-----------------|-----------------|
    | **Crocs de la Nuit** | Monde | +8% vol de vie supplémentaires (total 33%). | Le vol de vie génère un bouclier de 20% du soin. +5% vol de vie suppl. |
    | **Manteau Maudit** | Donjon Classique | Chaque critique draine 5% HP max ennemi directement (en plus du vol de vie normal). | Drain critique = 8% HP max. 3 critiques consécutifs → régénère 15% HP max instantanément. |
    | **Acier Ensanglanté** | Craft | Le vol de vie génère un bouclier pour 50% du soin reçu. | Bouclier du vol de vie = 80% du soin. Si bouclier actif, +15% dégâts physiques. |
    | **Suaire des Ténèbres** | Donjon Élite | Si HP > 80% : +20% dégâts. Vol de vie augmenté de +10%. | Régénère 3% HP max/tour. Vol de vie total = 40%. Si HP > 80%, +30% dégâts physiques. |
    | **Seigneur des Ténèbres** | Donjon Abyssal | Chaque critique pompe 4% HP max ennemi directement. | Drain critique monte à 6% HP max. +20% dégâts sur cibles à moins de 50% HP. Vol de vie +15%. |
    | **Prince Immortel** | Raid | Vol de vie = 40% dégâts. +10% dégâts par 10% HP manquants (cumul avec passif de classe). | Une fois par combat, si tu meurs, reviens à 25% HP et soigne via vol de vie sur le prochain coup. |

    ??? info "Bonus de stats (2 / 4 / 5 / 6 pièces) — valeurs de base"
        | Panoplie | 2 pcs | 4 pcs | 5 pcs | 6 pcs |
        |----------|-------|-------|-------|-------|
        | Crocs de la Nuit | +2% ATK Phy. | +3% HP | +3% ATK Phy. | +4% ATK Phy. |
        | Manteau Maudit | +2% ATK Phy. | +3% HP | +3% ATK Phy. | +4% ATK Phy. |
        | Acier Ensanglanté | +2% Vit. | +3% ATK Phy. | +3% Vit. | +4% ATK Phy. |
        | Suaire des Ténèbres | +2% HP | +3% ATK Phy. | +3% HP | +4% ATK Phy. |
        | Seigneur des Ténèbres | +2% ATK Phy. | +3% Pén. Phy. | +3% ATK Phy. | +4% ATK Phy. |
        | Prince Immortel | +2% ATK Phy. | +3% HP | +3% ATK Phy. | +4% Pén. Phy. |

=== "⏳ Gardien du Temps"

    Le Gardien affaiblit progressivement l'ennemi en réduisant ses stats — plus il debuff, plus il fait mal.

    **Emplacements :** Couronne · Manteau · Bas · Escarpes · Sablier · Relique · Alliance

    | Panoplie | Source | Passif 3 pièces | Passif 7 pièces |
    |----------|--------|-----------------|-----------------|
    | **Brisé** | Monde | Les debuffs de réduction de stats durent 1 tour supplémentaire. | Les debuffs actifs sur l'ennemi augmentent tes dégâts de 3% chacun (max +30%). |
    | **Horloge Fractale** | Donjon Classique | 25% de chance de réduire 2 stats ennemies au lieu d'une par tour. | Chance de double debuff = 40%. Chaque stat réduite amplifie tes dégâts de 4%. |
    | **Tissu Temporel** | Craft | Au début du combat, réduit immédiatement 2 stats ennemies de 8% chacune. | Début de combat : réduit 3 stats ennemies de 8% pour toute la durée du combat. |
    | **Chrono Maudit** | Donjon Élite | Les stats réduites de l'ennemi ne peuvent pas être restaurées pendant le combat. | Debuffs permanents ET chaque nouvelle réduction s'ajoute sans limite de -50%. |
    | **Paradoxe Temporel** | Donjon Abyssal | Chaque 10% de stat réduite chez l'ennemi t'octroie +5% dégâts (max +50%). | À -50% de réduction, l'ennemi perd 1 action par tour. Dégâts doublés contre ennemis à -50%. |
    | **Maître du Destin** | Raid | Réduction max passe à 75%. Chaque debuff appliqué soigne 3% HP max. | Dégâts +15% par debuff actif (max +60%). Ennemi à -75% perd 1 action/tour. Dégâts non-esquivables. |

    ??? info "Bonus de stats (2 / 4 / 5 / 6 pièces) — valeurs de base"
        | Panoplie | 2 pcs | 4 pcs | 5 pcs | 6 pcs |
        |----------|-------|-------|-------|-------|
        | Brisé | +2% Vit. | +3% ATK Mag. | +3% ATK Phy. | +4% Vit. |
        | Horloge Fractale | +2% ATK Phy. | +3% ATK Mag. | +3% ATK Phy. | +4% ATK Mag. |
        | Tissu Temporel | +2% HP | +3% ATK Phy. | +3% ATK Mag. | +4% HP |
        | Chrono Maudit | +2% ATK Phy. | +3% ATK Mag. | +3% ATK Phy. | +4% ATK Mag. |
        | Paradoxe Temporel | +2% ATK Phy. | +3% ATK Mag. | +3% Vit. | +4% ATK Phy. |
        | Maître du Destin | +2% ATK Phy. | +3% ATK Mag. | +3% Vit. | +4% ATK Phy. |

=== "☠️ Ombre Venin"

    L'Ombre Venin empoisonne et ronge ses ennemis — builds axés sur le poison, la vitesse ou la brûlure progressive.

    **Emplacements :** Voile · Suaire · Guêtres · Mocassins · Aiguille · Fiole · Annelet

    | Panoplie | Source | Passif 3 pièces | Passif 7 pièces |
    |----------|--------|-----------------|-----------------|
    | **Distillat Vénéneux** | Monde | Le poison inflige +1% HP max ennemi/tour supplémentaire (4% au lieu de 3%). | Le poison monte à 5% HP max/tour. Chaque tour empoisonné, l'ennemi subit -2% à une stat aléatoire. |
    | **Aiguille Toxique** | Donjon Classique | 30% de chance d'appliquer une dose de poison supplémentaire par attaque. | Chaque attaque empoisonne à coup sûr. Le poison s'applique avant les dégâts physiques. |
    | **Venin Distillé** | Craft | Le premier poison appliqué inflige directement 8% HP max en dégâts instantanés. | Chaque re-application de poison inflige +5% HP max instantanément. Stack infini. |
    | **Brume Toxique** | Donjon Élite | Chaque critique applique automatiquement 1 dose de poison. | Le poison par critique inflige 6% HP max/tour. Dégâts critiques +15% sur cibles empoisonnées. |
    | **Essence Corrompue** | Donjon Abyssal | Le poison réduit la DEF Physique et la DEF Magique ennemies de 5% par tour (max -25%). | Réduction DEF du poison = 8%/tour (max -40%). Dégâts physiques +15% sur cibles avec DEF réduite. |
    | **Nécrosis Primordiale** | Raid | Le poison peut stacker 3 fois (3% + 6% + 9% HP max ennemi/tour). | Au max de stacks : nécrosis — 20% HP max/tour + toutes les stats réduites de 15%. |

    ??? info "Bonus de stats (2 / 4 / 5 / 6 pièces) — valeurs de base"
        | Panoplie | 2 pcs | 4 pcs | 5 pcs | 6 pcs |
        |----------|-------|-------|-------|-------|
        | Distillat Vénéneux | +2% ATK Phy. | +3% ATK Mag. | +3% ATK Phy. | +4% ATK Phy. |
        | Aiguille Toxique | +2% Vit. | +3% ATK Phy. | +3% Vit. | +4% ATK Phy. |
        | Venin Distillé | +2% ATK Phy. | +3% ATK Mag. | +3% ATK Phy. | +4% Pén. Phy. |
        | Brume Toxique | +2% ATK Phy. | +3% Pén. Phy. | +3% ATK Phy. | +4% ATK Phy. |
        | Essence Corrompue | +2% ATK Phy. | +3% Pén. Mag. | +3% ATK Phy. | +4% Pén. Phy. |
        | Nécrosis Primordiale | +2% ATK Phy. | +3% Pén. Mag. | +3% ATK Phy. | +4% Pén. Phy. |

=== "🔥 Pyromancien"

    Le Pyromancien accumule des stacks de brûlure pour des dégâts magiques dévastateurs.

    **Emplacements :** Coiffe · Tunique · Pantalon · Sabots · Torche · Phylactère · Gemme

    | Panoplie | Source | Passif 3 pièces | Passif 7 pièces |
    |----------|--------|-----------------|-----------------|
    | **Tison Ardent** | Monde | La brûlure peut monter jusqu'à 6 stacks au lieu de 5. | Brûlure inflige +2% ATK Mag/stack suppl. Au max, inflige 20% ATK Magique instantanément. |
    | **Flamme Enflammée** | Donjon Classique | Chaque critique ajoute automatiquement 1 stack de brûlure. | Les critiques appliquent 2 stacks de brûlure. Dégâts critiques +10% par stack actif. |
    | **Pierre Incandescente** | Craft | Tes sorts ont 20% de chance d'appliquer directement 2 stacks de brûlure. | ATK Magique +3% par stack de brûlure. Sorts : 30% de chance d'appliquer 2 stacks. Double lancé 10%. |
    | **Brasier Infernal** | Donjon Élite | La brûlure dure 1 tour supplémentaire avant de se dissiper. | La brûlure ne se dissipe jamais. À 5 stacks, l'ennemi perd 4 points de vitesse/tour. |
    | **Âme Volcanique** | Donjon Abyssal | Au max de stacks, l'ennemi subit +20% dégâts magiques supplémentaires. | Brûlure max = 7 stacks, inflige 25% ATK Mag/stack. Chaque critique ajoute 1 stack. |
    | **Phénix Éternel** | Raid | Brûlure max = 8 stacks. Au max, l'ennemi prend +30% dégâts magiques. | Une fois/combat : si tu meurs, ressuscite à 30% HP et applique immédiatement 8 stacks. |

    ??? info "Bonus de stats (2 / 4 / 5 / 6 pièces) — valeurs de base"
        | Panoplie | 2 pcs | 4 pcs | 5 pcs | 6 pcs |
        |----------|-------|-------|-------|-------|
        | Tison Ardent | +2% ATK Mag. | +3% Pén. Mag. | +3% ATK Mag. | +4% ATK Mag. |
        | Flamme Enflammée | +2% ATK Mag. | +3% Pén. Mag. | +3% ATK Mag. | +4% ATK Mag. |
        | Pierre Incandescente | +2% ATK Mag. | +3% Pén. Mag. | +3% ATK Mag. | +4% ATK Mag. |
        | Brasier Infernal | +2% ATK Mag. | +3% Pén. Mag. | +3% ATK Mag. | +4% ATK Mag. |
        | Âme Volcanique | +2% ATK Mag. | +3% Pén. Mag. | +3% ATK Mag. | +4% ATK Mag. |
        | Phénix Éternel | +2% ATK Mag. | +3% Pén. Mag. | +3% ATK Mag. | +4% ATK Mag. |

=== "⚒️ Paladin"

    Le Paladin monte en puissance au fil des tours grâce à son passif de ramp défensif et offensif.

    **Emplacements :** Armet · Haubert · Tassettes · Éperons · Marteau · Croix · Insigne

    | Panoplie | Source | Passif 3 pièces | Passif 7 pièces |
    |----------|--------|-----------------|-----------------|
    | **Armure Consacrée** | Monde | Le ramp du passif démarre à +5% dès le tour 1 au lieu de 0%. | Le ramp démarre à +10%. Régénère 2% HP max/tour. |
    | **Vœu du Croisé** | Donjon Classique | Le ramp augmente de +4% par tour au lieu de +3% (max atteint plus vite). | Ramp à +4%/tour. Le ramp offensif s'applique aussi aux dégâts magiques. |
    | **Métal Sanctifié** | Craft | Réduit les dégâts reçus de 4% supplémentaires par tour de combat (max -30%). | +8% au ramp défensif de départ. La réduction dégâts par tour ne plafonne plus à -30% mais à -45%. |
    | **Lumière Divine** | Donjon Élite | Le ramp max passe à +40%/+40% en réduction et dégâts. | Ramp max +40%. Dégâts sacrés : ignorent 10% DEF ennemie quand le ramp est au max. |
    | **Bouclier de la Foi** | Donjon Abyssal | La réduction de dégâts du ramp s'applique aussi aux dégâts purs. | Dégâts purs réduits par le ramp. Reflète 15% des dégâts reçus à l'ennemi. |
    | **Avatar Sacré** | Raid | Ramp max +50%/+50%. Le ramp ne se réinitialise pas entre les vagues de donjon. | Une fois par combat, reflète 30% des dégâts reçus. Au max du ramp, chaque attaque soigne 5% HP max. |

    ??? info "Bonus de stats (2 / 4 / 5 / 6 pièces) — valeurs de base"
        | Panoplie | 2 pcs | 4 pcs | 5 pcs | 6 pcs |
        |----------|-------|-------|-------|-------|
        | Armure Consacrée | +2% HP | +3% Déf. Phy. | +3% HP | +4% Déf. Phy. |
        | Vœu du Croisé | +2% ATK Phy. | +3% Déf. Phy. | +3% Déf. Mag. | +4% ATK Phy. |
        | Métal Sanctifié | +2% HP | +3% Déf. Phy. | +3% Déf. Mag. | +4% HP |
        | Lumière Divine | +2% HP | +3% Déf. Phy. | +3% Déf. Mag. | +4% HP |
        | Bouclier de la Foi | +2% Déf. Phy. | +3% Déf. Mag. | +3% HP | +4% Déf. Phy. |
        | Avatar Sacré | +2% HP | +3% Déf. Phy. | +3% Déf. Mag. | +4% HP |

---

## Comment optimiser son équipement ?

1. **Complète un set** avant de tout maximiser — les bonus 7 pièces sont souvent plus importants que les stats individuelles
2. **Monte la rareté** de toutes tes pièces uniformément — une pièce trop faible tire tout le set vers le bas
3. **Améliore à la Forge** — même des pièces communes améliorées +10 peuvent être très efficaces
4. **Vise la source correspondant à ton niveau** — inutile de chercher des pièces de Raid si tu ne fais pas encore de Raids
5. **Choisis selon ton style** — chaque panoplie correspond à un build différent pour la même classe

!!! success "Meilleur DPS par classe"
    | Classe | Panoplie recommandée (endgame) |
    |--------|-------------------------------|
    | Guerrier | Seigneur de l'Abîme (burst) ou Colosse de Guerre (survie) |
    | Assassin | Exécuteur des Ombres (exécuteur) ou Voile de Sang (saignée) |
    | Mage | Nexus Primordial (polyvalent) ou Voile du Prophète (pénétration) |
    | Tireur | Ouragan d'Acier (multi-hits) ou Œil de l'Horizon (critiques) |
    | Support | Lumière Éternelle (survie) ou Bouclier du Gardien (bouclier offensif) |
    | Vampire | Prince Immortel (burst + survie) ou Seigneur des Ténèbres (drain) |
    | Gardien du Temps | Maître du Destin (contrôle total) ou Paradoxe Temporel (burst debuff) |
    | Ombre Venin | Nécrosis Primordiale (poison létal) ou Essence Corrompue (DEF shred) |
    | Pyromancien | Phénix Éternel (burst + résurrection) ou Âme Volcanique (accumulation) |
    | Paladin | Avatar Sacré (indestructible) ou Bouclier de la Foi (reflet de dégâts) |
