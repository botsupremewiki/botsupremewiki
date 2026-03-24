# 🔍 Simulateur d'Ennemis

Utilise le simulateur interactif ci-dessous pour connaître les statistiques exactes
de n'importe quel ennemi selon la zone, le type de boss, ou le niveau de donjon/raid.

---

<div class="enemy-simulator-tabs" id="simulator-root">
  <p><em>Chargement du simulateur...</em></p>
</div>

<script>
// Le simulateur est chargé depuis javascripts/enemy_calc.js
document.addEventListener('DOMContentLoaded', function() {
  if (typeof initEnemyCalc === 'function') {
    initEnemyCalc('simulator-root');
  }
});
</script>

---

!!! tip "Navigation par mode"
    Chaque page de mode de jeu contient aussi un lien vers le simulateur pré-configuré pour ce mode :

    - [🌍 Simulateur Monde](../modes/monde.md)
    - [🏰 Simulateur Donjons](../modes/donjons.md)
    - [👥 Simulateur Raids](../modes/raids.md)
    - [🐉 Simulateur World Boss](../modes/world_boss.md)
