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
| Boss Emblématique | 5 ⚡ |
| Boss Antique | 10 ⚡ |
| Boss Final (Zone 10 000) | 10 ⚡ |

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

Chaque combat gagné apporte de l'XP. Monter de niveau augmente toutes tes statistiques de combat. L'objectif ultime est d'atteindre le **niveau 1 000** pour effectuer un **Prestige**.

### Le Prestige

Au niveau 1 000, tu peux **prestiger** : tu recommences au niveau 1, mais chaque niveau de Prestige te donne **+0,1% de toutes tes stats** en permanent. C'est un bonus qui s'accumule indéfiniment à chaque prestige.

!!! warning "Avant de prestiger"
    Mets tes meilleurs équipements et ressources en **Banque** — ils résistent au Prestige. Le reste de ton inventaire est réinitialisé.

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
    Non — les 10 000 zones sont la limite absolue. La zone 10 000 abrite le **Boss Final**, et au-delà il n'y a rien. Atteindre la fin du Monde est un véritable exploit.

---

## Tableau des récompenses

La formule des récompenses est proportionnelle au numéro de zone actuelle.

| Type d'ennemi | XP gagnée | Or gagné |
|---|---|---|
| Ennemi normal | `zone × 1` | `(zone ÷ 5) × 1` |
| Boss Classique | `zone × 3` | `(zone ÷ 5) × 3` |
| Boss Emblématique | `zone × 10` | `(zone ÷ 5) × 10` |
| Boss Antique | `zone × 30` | `(zone ÷ 5) × 30` |
| Boss Final (Zone 10 000) | **5 000 000 XP** | **2 000 000 or** |

!!! tip "Récompenses d'équipement"
    Tous les ennemis (normaux et boss) peuvent droper un équipement de la **panoplie Monde** correspondant à leur classe. Les boss Emblématiques et Antiques ont une meilleure chance de drop et dropent des pièces de meilleure rareté.

---

## Les ennemis

Chaque zone possède un **stage** déterminé par `(zone - 1) % 10 + 1`, qui dicte la **classe** de l'ennemi rencontré. Il existe 10 classes d'ennemis, chacune avec 5 noms possibles tirés aléatoirement.

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
    - **Classe :** identique au stage de la zone (`zone % 10`, puis mapping)
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

    **Récompenses :** XP = `zone × 3` | Or = `(zone ÷ 5) × 3`
    **Drop possible :** équipement panoplie Monde de la classe du boss

=== "Boss Emblématiques"

    ### Boss Emblématiques (zones multiples de 100)

    Aux zones **100, 200, 300, 400...** jusqu'à **9 900**, un **Boss Emblématique** apparaît. Il est bien plus puissant qu'un boss classique (**×3 HP**) et possède un **passif unique**.

    - **Coût :** 5 énergie
    - **Classe :** aléatoire parmi les 10 classes
    - **HP :** ×3 par rapport à un boss classique de même zone

    **Récompenses :** XP = `zone × 10` | Or = `(zone ÷ 5) × 10`

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

    #### Les 10 passifs Emblématiques (cycle par zone ÷ 100)

    | # | Passif | Description |
    |:---:|---|---|
    | 1 | Régénération | Régénère 2% de ses HP max à chaque tour. |
    | 2 | Affaiblissement | Réduit toutes tes stats de 10% au premier tour. |
    | 3 | Dégâts Purs | Inflige des dégâts purs = 5% de ses HP max par tour. |
    | 4 | Furie Initiale | Les 3 premiers tours, dégâts doublés. |
    | 5 | Immunité aux Critiques | Immunité aux critiques pendant les 5 premiers tours. |
    | 6 | Enragé | +10% de dégâts par 20% HP perdus. |
    | 7 | Absorption | 20% des dégâts reçus convertis en bouclier. |
    | 8 | Maudit | Tes soins sont réduits de 50%. |
    | 9 | Riposte | Renvoie 30% des dégâts physiques. |
    | 10 | Aura Glaciale | Réduit ta vitesse de 20%. |

    !!! warning "Prenez garde aux passifs dangereux"
        Le passif **Dégâts Purs** (n°3) ignore toute défense — chaque tour tu perds automatiquement 5% des HP max du boss, peu importe ta résistance. Le passif **Furie Initiale** (n°4) peut éliminer un joueur fragile en quelques tours seulement.

=== "Boss Antiques"

    ### Boss Antiques (zones multiples de 1000)

    Aux zones **1 000, 2 000, 3 000... 9 000**, un **Boss Antique** barre la route. Ce sont les gardiens des grands thèmes, avec **×5 HP** et des passifs dévastateurs.

    - **Coût :** 10 énergie
    - **Classe :** aléatoire parmi les 10 classes
    - **HP :** ×5 par rapport à un boss classique de même zone

    **Récompenses :** XP = `zone × 30` | Or = `(zone ÷ 5) × 30`

    #### Les 10 noms Antiques (1 par zone de 1000)

    | Zone | Nom du Boss Antique |
    |:---:|---|
    | 1 000 | Vrethax le Primordial |
    | 2 000 | Azkoth la Conscience Noire |
    | 3 000 | Solarius le Dévoreur d'Étoiles |
    | 4 000 | Mortifax l'Impérissable |
    | 5 000 | Chronaxis le Maître Absolu |
    | 6 000 | Nexuvor l'Indicible |
    | 7 000 | Erebos la Nuit Éternelle |
    | 8 000 | Pantheos le Dieu-Bête |
    | 9 000 | Ultharak l'Abomination |
    | 10 000 | *(Boss Final — voir section dédiée)* |

    #### Les 10 passifs Antiques (cycle par zone ÷ 1000)

    | # | Passif | Description |
    |:---:|---|---|
    | 1 | Bouclier Ancien | Absorbe 30% des dégâts les 5 premiers tours. |
    | 2 | Fléau Primordial | Applique un debuff -15% sur toutes tes stats. |
    | 3 | Éternité | Ses HP ne peuvent pas tomber sous 50% avant le tour 10. |
    | 4 | Malédiction Antique | Tes critiques ne font pas de dégâts supplémentaires. |
    | 5 | Terreur Abyssale | Réduit ta Défense Physique et ta Défense Magique de 30%. |
    | 6 | Résilience Ancienne | Régénère 5% de ses HP max chaque tour. |
    | 7 | Emprise Temporelle | Saute un de tes tours tous les 5 tours. |
    | 8 | Dévoration | Vole 10% de tes stats offensives à chaque tour. |
    | 9 | Néant | Tes passifs de classe sont désactivés les 3 premiers tours. |
    | 10 | Convergence | Gagne toutes les stats des 5 derniers ennemis vaincus. |

    !!! warning "Les Boss Antiques sont des épreuves"
        Le passif **Éternité** (n°3) rend le boss littéralement invincible sous 50% HP pendant les 10 premiers tours — tu dois tenir le combat long. **Dévoration** (n°8) est cumulatif : à chaque tour, le boss devient plus fort et toi plus faible. Sois préparé avant d'affronter ces colosses.

=== "Boss Final"

    ### Chromastrix, le Convergent des Âges — Zone 10 000

    Le boss ultime du Monde. Une seule rencontre possible, à la zone exacte **10 000**.

    | Propriété | Valeur |
    |---|---|
    | Nom | **Chromastrix, le Convergent des Âges** |
    | Classe | **Chromaste** (unique, n'appartient à aucune des 10 classes) |
    | HP | ×10 (prend le maximum de toutes les classes, puis ×10) |
    | Coût | 10 énergie |
    | XP | **5 000 000** |
    | Or | **2 000 000** |

    #### Passif : Convergence Absolue

    > *Prend le meilleur de TOUTES les classes simultanément.*

    Chromastrix cumule les passifs et capacités de l'ensemble des 10 classes d'ennemis en même temps. Il n'a aucune faiblesse exploitable — chaque aspect de votre build sera mis à l'épreuve.

    !!! warning "L'épreuve ultime"
        Affronter Chromastrix sans une préparation maximale est suicidaire. Assure-toi d'avoir les meilleurs équipements disponibles, des reliques optimisées, et si possible un niveau de Prestige élevé avant de tenter cet affrontement.

    !!! info "Après la zone 10 000"
        Vaincre Chromastrix est l'accomplissement ultime du mode Monde. Il n'existe pas de zone 10 001 — la seule voie de progression au-delà est le **Prestige**.

---

## Conseils et stratégies

!!! tip "Reste dans ta zone confort"
    Si tu perds souvent sur une zone, reviens en arrière et améliore tes équipements ou monte de niveau avant de réessayer. Mourir coûte de l'or et bloque ta régénération.

!!! tip "Priorise les boss selon tes ressources"
    - **Boss Classiques** : excellents pour farm régulier, bon ratio coût/récompense
    - **Boss Emblématiques** : très rentables en XP et or mais coûteux — privilégie-les quand ton énergie est pleine
    - **Boss Antiques** : réservés aux joueurs puissants avec suffisamment de stats pour tenir un long combat

!!! tip "Le mode Auto pour les zones déjà maîtrisées"
    Active la boucle automatique uniquement sur des zones où tu es quasi-certain de gagner. Un enchaînement de défaites en auto peut vider ton énergie pour rien et te coûter de l'or.

!!! info "Équipements panoplie Monde"
    Les ennemis du Monde droppent des pièces de la **panoplie Monde** correspondant à leur classe. Ces équipements ont une puissance de base (multiplicateur ×1.0). Pour des équipements plus puissants, explore les **Donjons** et **Raids** — leurs panoplies ont des multiplicateurs bien supérieurs.

!!! warning "Gestion de l'énergie face aux boss rares"
    Les Boss Emblématiques (×5 énergie) et Antiques (×10 énergie) apparaissent rarement. Ne les affronte que si tu as l'énergie nécessaire ET les stats suffisantes — une défaite contre eux est particulièrement coûteuse.
