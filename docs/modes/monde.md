# 🗺️ Le Monde

Le Monde est le **mode de jeu principal** pour progresser en solo. Il se compose de **10 000 zones** avec des ennemis de plus en plus puissants. À chaque zone, un ennemi thématique t'attend — et tous les X zones, un boss redoutable barre la route.

---

## Comment ça fonctionne ?

Chaque combat coûte de l'**énergie**. Tu choisis de combattre l'ennemi de ta zone, et le résultat est calculé automatiquement (combat simulé complet).

### Coûts en énergie

| Type d'ennemi | Coût en énergie |
|---|---|
| Ennemi normal | 1 ⚡ |
| Boss Classique | 2 ⚡ |
| Boss Runique | 3 ⚡ |
| Boss Emblématique | 5 ⚡ |
| Boss Antique | 10 ⚡ |

### En cas de victoire

- Tu gagnes de l'**expérience** pour monter de niveau
- Tu gagnes de l'**or**
- Tu as une chance de recevoir un **équipement** en butin (panoplie Monde de la classe de l'ennemi)

### En cas de défaite

- Tu perds une partie de tes **PV actuels**
- Tu perds une partie de ton **or**
- Une pénalité de mort bloque temporairement ta régénération passive

---

## Le mode Auto (boucle automatique)

Tu peux activer la **boucle automatique** pour combattre en continu sans intervenir. Le bot joue tout seul toutes les **3 secondes**, jusqu'à ce que tu l'arrêtes manuellement ou que ton énergie soit épuisée.

Un résumé final s'affiche à la fin : victoires, défaites, or gagné, XP gagnée.

!!! tip "Astuce Auto"
    Lance le mode Auto sur une zone où tu gagnes à coup sûr pour accumuler des récompenses passivement. Reviens arrêter la boucle quand tu es prêt.

---

## La progression de niveau

Chaque combat gagné apporte de l'XP. Monter de niveau augmente toutes tes statistiques de combat. À partir du **niveau 10**, tu peux effectuer un **Prestige** pour réinitialiser ta progression et gagner des bonus permanents.

### Le Prestige

Pour tout savoir sur le Prestige et comment il fonctionne, consulte la page dédiée : **[Prestige](../prestige.md)**.

---

## Thèmes des zones

Les 10 000 zones sont divisées en **10 thèmes cycliques** de 1 000 zones chacun. L'ambiance visuelle, les noms d'ennemis et le style des boss évoluent selon le thème actif.

| Zones | Thème | Emoji |
|---|---|:---:|
| 1 – 1 000 | Plaine Verdoyante | 🌿 |
| 1 001 – 2 000 | Forêt Ombreuse | 🌲 |
| 2 001 – 3 000 | Marais Pestilentiel | 🌫️ |
| 3 001 – 4 000 | Désert Ardent | 🏜️ |
| 4 001 – 5 000 | Toundra Glacée | ❄️ |
| 5 001 – 6 000 | Volcans Ardents | 🌋 |
| 6 001 – 7 000 | Cités en Ruines | 🏚️ |
| 7 001 – 8 000 | Abysses Marines | 🌊 |
| 8 001 – 9 000 | Nécropole Maudite | 💀 |
| 9 001 – 10 000 | Royaume Céleste | ☁️ |

!!! info "Cycle infini ?"
    Non — les 10 000 zones sont la limite absolue. La zone 10 000 abrite **Omegaris la Fin du Monde**, le Boss Antique ultime. Au-delà, il n'y a rien — atteindre la fin du Monde est un véritable exploit.

---

!!! tip "Récompenses d'équipement"
    Tous les ennemis (normaux et boss) peuvent droper un équipement de la **panoplie Monde** correspondant à leur classe. Les boss Emblématiques et Antiques ont une meilleure chance de drop et dropent des pièces de meilleure rareté.

---

## Les ennemis

Chaque zone possède un **stage** qui dicte la **classe** de l'ennemi rencontré. Les 10 classes se succèdent en rotation continue : la zone 1 commence par le Guerrier, la zone 2 par l'Assassin, et ainsi de suite jusqu'au Paladin en zone 10 — puis le cycle recommence à la zone 11. Il existe 10 classes d'ennemis, chacune avec 5 noms possibles tirés aléatoirement.

=== "Ennemis Classiques"

    ### Correspondance Stage → Classe → Noms

    | Stage | Classe | Noms possibles |
    |:---:|---|---|
    | 1 | Guerrier | Berserker, Paladin Noir, Chevalier Déchu, Colosse, Titan |
    | 2 | Assassin | Rôdeur, Ombre Tranchante, Spectre Lame, Fantôme Acéré, Tueur Silencieux |
    | 3 | Mage | Sorcier, Archimage Corrompu, Nécromancien, Mage du Chaos, Élémentaliste |
    | 4 | Tireur | Archer Maudit, Chasseur de Primes, Sniper Fantôme, Pistolier, Garde d'Élite |
    | 5 | Support | Chaman Vénéneux, Prêtre Obscur, Gardien Maudit, Moine Corrompu, Oracle Sombre |
    | 6 | Vampire | Vampire Ancien, Seigneur des Morts, Suçeur d'Âmes, Prince Ténébreux, Goule Noble |
    | 7 | Gardien du Temps | Chronomancien, Gardien Temporel, Distordeur du Temps, Maître des Ères, Briseur d'Âges |
    | 8 | Ombre Venin | Araignée Toxique, Serpent Mortel, Basilic, Hydre Venimeuse, Scorpion Géant |
    | 9 | Pyromancien | Élémentaire de Feu, Salamandre, Phénix Maudit, Dragon de Lave, Pyromage |
    | 10 | Paladin | Croisé Déchu, Inquisiteur, Chevalier Sacré Corrompu, Défenseur Maudit, Gardien Draconique |

    !!! info "Composition des stages"
        Les zones 1, 11, 21... (stage 1) ont toujours un ennemi Guerrier. Les zones 2, 12, 22... (stage 2) ont toujours un Assassin. Et ainsi de suite, en cycle continu.

=== "Boss Classiques"

    ### Boss Classiques (toutes les zones)

    Chaque zone possède un **Boss Classique** que tu peux affronter à la place de l'ennemi normal.

    - **Coût :** 2 énergie
    - **Classe :** identique au stage de la zone (rotation cyclique des 10 classes)
    - **Nom :** `{Préfixe} {nom_ennemi_de_classe}` — le préfixe est tiré aléatoirement parmi :

    | # | Préfixe |
    |:---:|---|
    | 1 | Seigneur |
    | 2 | Ancien |
    | 3 | Maître |
    | 4 | Grand |
    | 5 | Archonte |
    | 6 | Roi |
    | 7 | Prince |
    | 8 | Tyran |

    **Exemples de noms générés :**
    *"Seigneur Berserker"*, *"Archonte Nécromancien"*, *"Tyran Dragon de Lave"*, *"Roi Vampire Ancien"*...

    **Récompenses :** Plus d'XP et d'or qu'un ennemi normal — idéal pour un farm régulier.
    **Drop possible :** équipement panoplie Monde de la classe du boss

=== "Boss Runiques"

    ### Boss Runiques (zones multiples de 10, sauf 100/1000)

    Aux zones **10, 20, 30... 90, 110, 120...** (multiples de 10 mais pas de 100), un **Boss Runique** apparaît après le boss classique. Plus coriace, il possède un **passif lié à sa classe**.

    - **Coût :** 3 énergie
    - **Classe :** rotation cyclique (zone 10 = Guerrier, zone 20 = Assassin, ..., cycle de 10)
    - **HP :** ×1,5 par rapport aux stats de base de sa zone
    - **Nom :** `{Préfixe aléatoire} {nom_ennemi_de_classe}` — mêmes préfixes que le boss classique

    **Récompenses :** Plus d'XP et d'or qu'un boss classique — bon ratio énergie/récompense.

    #### Passifs Runiques (selon la classe du boss)

    | Classe | Passif | Effet |
    |---|---|---|
    | Guerrier | Furie Mineure | +3% dégâts par tranche de 25% HP perdus (max +12%) |
    | Assassin | Réflexes | 5% de chance d'esquiver une attaque physique |
    | Mage | Résonance Arcanique | Ignore 8% de ta Déf. Mag. |
    | Tireur | Visée Précise | +8% chance de critique |
    | Support | Régénération | Récupère 0,5% HP max au début de chaque tour |
    | Vampire | Siphon Mineur | Récupère 5% des dégâts infligés en HP |
    | Gardien du Temps | Distorsion Légère | Ta vitesse réduite de 5% |
    | Ombre Venin | Glandes Actives | 10% de chance de poison additionnel à chaque attaque |
    | Pyromancien | Braises | 20% de chance d'appliquer 1 stack de brûlure à chaque attaque |
    | Paladin | Résistance | Dégâts reçus réduits de 5% |

=== "Boss Emblématiques"

    ### Boss Emblématiques (zones multiples de 100, sauf 1000)

    Aux zones **100, 200, 300...** jusqu'à **9 900**, un **Boss Emblématique** apparaît. Il a un nom unique, des HP doublés et un **passif puissant lié à sa classe**.

    - **Coût :** 5 énergie
    - **Classe :** rotation cyclique (zone 100 = Guerrier, zone 200 = Assassin, ..., cycle de 10)
    - **HP :** ×2 par rapport aux stats de base de sa zone
    - **Nom :** unique parmi 20 noms cycliques

    **Récompenses :** Bien plus d'XP et d'or que les boss classiques — très rentables quand ton énergie est pleine.

    #### Les 20 noms Emblématiques (cycle par zone ÷ 100)

    | # | Nom |
    |:---:|---|
    | 1 | Malachar l'Éternel |
    | 2 | Zephyros le Tempétueux |
    | 3 | Mordreth la Dévoreuse |
    | 4 | Xanathos l'Omniscient |
    | 5 | Valdris l'Implacable |
    | 6 | Sylvara la Tisseuse |
    | 7 | Grudnak le Colossal |
    | 8 | Elysia la Corrompue |
    | 9 | Tharax le Venimeux |
    | 10 | Drakonus le Chromate |
    | 11 | Abyssion le Profond |
    | 12 | Ignaris le Volcanique |
    | 13 | Glacialis le Glaçant |
    | 14 | Umbrath l'Ombral |
    | 15 | Pyrion l'Incandescent |
    | 16 | Temporis le Figé |
    | 17 | Necrosis la Putride |
    | 18 | Aetherion l'Astral |
    | 19 | Tenebris le Ténébreux |
    | 20 | Primordius l'Ancestral |

    #### Passifs Emblématiques (selon la classe du boss)

    | Classe | Passif | Effet |
    |---|---|---|
    | Guerrier (zone 100) | Furie Guerrière | +5% dégâts par tranche de 25% HP perdus (max +20%) |
    | Assassin (zone 200) | Instinct | 10% de chance d'esquiver une attaque physique |
    | Mage (zone 300) | Voile Arcanique | Ignore 12% de ta Déf. Mag. |
    | Tireur (zone 400) | Œil Affûté | +12% chance de critique |
    | Support (zone 500) | Régénération Active | Récupère 1% HP max/tour |
    | Vampire (zone 600) | Siphon de Vie | Récupère 8% des dégâts infligés |
    | Gardien du Temps (zone 700) | Ralentissement | Ta vitesse réduite de 10% |
    | Ombre Venin (zone 800) | Venin Persistant | 15% de chance de poison additionnel à chaque attaque |
    | Pyromancien (zone 900) | Embrasement | 30% de chance d'appliquer 1 stack de brûlure |
    | Paladin (zone 1 100+) | Aura Défensive | Dégâts reçus réduits de 8% |

    !!! info "Rotation de classe"
        La classe du boss Emblématique suit une rotation cyclique de 10 en fonction de la zone. Zones 1000, 2000... sont des Boss Antiques (pas emblématiques).

=== "Boss Antiques"

    ### Boss Antiques (zones multiples de 1000)

    Aux zones **1 000, 2 000... 10 000**, un **Boss Antique** barre la route. Chacun a un nom unique, des HP triplés et un **passif dévastateur** — les épreuves les plus difficiles du mode Monde.

    - **Coût :** 10 énergie
    - **Classe :** rotation cyclique (zone 1 000 = Guerrier, zone 2 000 = Assassin, ..., cycle de 10)
    - **HP :** ×3 par rapport aux stats de base de sa zone

    **Récompenses :** Les meilleures récompenses du mode Monde — des quantités massives d'XP et d'or.

    #### Les 10 Boss Antiques

    | Zone | Nom | Classe | Passif |
    |:---:|---|---|---|
    | 1 000 | Vrethax le Primordial | Guerrier | Rage Ancienne |
    | 2 000 | Azkoth la Conscience Noire | Assassin | Ombre Persistante |
    | 3 000 | Solarius le Dévoreur d'Étoiles | Mage | Annihilation Partielle |
    | 4 000 | Mortifax l'Impérissable | Tireur | Salve Précise |
    | 5 000 | Chronaxis le Maître Absolu | Support | Bastion |
    | 6 000 | Nexuvor l'Indicible | Vampire | Avidité Sanguine |
    | 7 000 | Erebos la Nuit Éternelle | Gardien du Temps | Distorsion Temporelle |
    | 8 000 | Pantheos le Dieu-Bête | Ombre Venin | Nuée Venimeuse |
    | 9 000 | Ultharak l'Abomination | Pyromancien | Combustion |
    | 10 000 | Omegaris la Fin du Monde | Paladin | Jugement |

    #### Passifs Antiques — détail complet

    | Passif | Classe | Effets |
    |---|---|---|
    | Rage Ancienne | Guerrier | +8% dégâts par tranche de 25% HP perdus (max +32%) + **immunité aux stuns** |
    | Ombre Persistante | Assassin | 15% esquive + ses critiques ignorent 15% de ta Déf. Phy. |
    | Annihilation Partielle | Mage | Ignore 20% ta Déf. Mag. + tous les 5 tours : dégâts purs = 10% de ses HP max |
    | Salve Précise | Tireur | +18% chance de critique + tes défenses physiques -10% |
    | Bastion | Support | Récupère 1,5% HP max/tour + dégâts reçus -10% |
    | Avidité Sanguine | Vampire | Récupère 12% des dégâts infligés + te vole 1% HP max/tour |
    | Distorsion Temporelle | Gardien du Temps | Ta vitesse -15%, sa vitesse +15% |
    | Nuée Venimeuse | Ombre Venin | 20% de chance de poison additionnel + dégâts DoT ×1,2 |
    | Combustion | Pyromancien | 40% de chance d'appliquer 1 stack de brûlure + dégâts brûlure ×1,2 |
    | Jugement | Paladin | Dégâts reçus -12% + tous les 5 tours : dégâts purs = 8% de ses HP max |

    !!! warning "Les Boss Antiques sont des épreuves"
        **Rage Ancienne** (Vrethax) : plus il perd de HP, plus il devient dévastateur — et immune aux stuns. **Avidité Sanguine** (Nexuvor) : il se soigne massivement ET te draine. **Annihilation Partielle / Jugement** : les dégâts purs périodiques ignorent toute défense. Sois préparé avant d'affronter ces colosses.

---

## Conseils et stratégies

!!! tip "Reste dans ta zone confort"
    Si tu perds souvent sur une zone, reviens en arrière et améliore tes équipements ou monte de niveau avant de réessayer. Mourir coûte de l'or et bloque ta régénération.

!!! tip "Priorise les boss selon tes ressources"
    - **Boss Classiques** (2 ⚡) : excellents pour farm régulier, bon ratio coût/récompense
    - **Boss Runiques** (3 ⚡) : meilleur que classique sans dépenser beaucoup — à prioriser sur les zones ×10
    - **Boss Emblématiques** (5 ⚡) : très rentables en XP et or — privilégie-les quand ton énergie est pleine
    - **Boss Antiques** (10 ⚡) : réservés aux joueurs puissants avec suffisamment de stats pour tenir un long combat

!!! tip "Le mode Auto pour les zones déjà maîtrisées"
    Active la boucle automatique uniquement sur des zones où tu es quasi-certain de gagner. Un enchaînement de défaites en auto peut vider ton énergie pour rien et te coûter de l'or.

!!! info "Équipements panoplie Monde"
    Les ennemis du Monde droppent des pièces de la **panoplie Monde** correspondant à leur classe. Ces équipements ont une puissance de base (multiplicateur ×1.0). Pour des équipements plus puissants, explore les **Donjons** et **Raids** — leurs panoplies ont des multiplicateurs bien supérieurs.
    → [Raretés par zone et multiplicateurs de source](../objets/equipements.md)

!!! warning "Gestion de l'énergie face aux boss rares"
    Les Boss Emblématiques (×5 énergie) et Antiques (×10 énergie) apparaissent rarement. Ne les affronte que si tu as l'énergie nécessaire ET les stats suffisantes — une défaite contre eux est particulièrement coûteuse.

---

## 🔍 Simulateur d'ennemi

Sélectionne une zone et un type d'ennemi pour voir ses statistiques exactes.

> Les stats sont calculées avec la même formule que le jeu.

<div id="enemy-calculator">

  <div id="ec-ctrl-monde" class="ec-controls">
    <div class="ec-row">
      <label class="ec-label">Zone <span class="ec-hint">(1 – 10 000)</span></label>
      <input type="number" id="ec-zone" class="ec-input" min="1" max="10000" value="100" />
    </div>
    <div class="ec-row">
      <label class="ec-label">Type d'ennemi</label>
      <select id="ec-stage" class="ec-select">
        <option value="boss_classique">⚔️ Boss Classique (toutes zones)</option>
        <option value="boss_runique">🔮 Boss Runique (zone multiple de 10)</option>
        <option value="boss_emblematique">🌟 Boss Emblématique (zone multiple de 100)</option>
        <option value="boss_antique">⚠️ Boss Antique (zone multiple de 1 000)</option>
        <option value="sep" disabled>─── Ennemis normaux ───</option>
        <option value="1">Stage 1 — Guerrier</option>
        <option value="2">Stage 2 — Assassin</option>
        <option value="3">Stage 3 — Mage</option>
        <option value="4">Stage 4 — Tireur</option>
        <option value="5">Stage 5 — Support</option>
        <option value="6">Stage 6 — Vampire</option>
        <option value="7">Stage 7 — Gardien du Temps</option>
        <option value="8">Stage 8 — Ombre Venin</option>
        <option value="9">Stage 9 — Pyromancien</option>
        <option value="10">Stage 10 — Paladin</option>
      </select>
    </div>
    <div class="ec-row" id="ec-class-row" style="display:none">
      <label class="ec-label">Classe du boss <span class="ec-hint">(rotation par zone, modifiable)</span></label>
      <select id="ec-boss-class" class="ec-select">
        <option value="">Auto-détecté (rotation par zone)</option>
        <option value="Guerrier">⚔️ Guerrier</option>
        <option value="Assassin">🗡️ Assassin</option>
        <option value="Mage">🔮 Mage</option>
        <option value="Tireur">🏹 Tireur</option>
        <option value="Support">💚 Support</option>
        <option value="Vampire">🧛 Vampire</option>
        <option value="Gardien du Temps">⏳ Gardien du Temps</option>
        <option value="Ombre Venin">☠️ Ombre Venin</option>
        <option value="Pyromancien">🔥 Pyromancien</option>
        <option value="Paladin">🛡️ Paladin</option>
      </select>
    </div>
    <div class="ec-hint-box">
      💡 Les options grisées sont activées automatiquement quand la zone le permet. Zone ×10 → Runique (HP ×1,5) · Zone ×100 → Emblématique (HP ×2) · Zone ×1 000 → Antique (HP ×3)
    </div>
  </div>

  <div id="ec-result" style="display:none"></div>

</div>
