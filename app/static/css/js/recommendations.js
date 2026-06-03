document.addEventListener('DOMContentLoaded', () => {
  const grid    = document.getElementById('recs-grid');
  const buttons = document.querySelectorAll('.sort-btn');

  if (!grid || !buttons.length) return;

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      // Actualiza estado visual del botón activo
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const field = btn.dataset.sort; // 'relevancia' | 'rating' | 'anio'
      sortGrid(grid, field);
    });
  });
});

/**
 * Ordena los hijos de `grid` por el atributo data-{field} de forma descendente.
 * Usa un DocumentFragment para minimizar los reflows del DOM (1 solo reflow).
 *
 * @param {HTMLElement} grid  - Contenedor de tarjetas (#recs-grid).
 * @param {string}      field - Campo a ordenar: 'relevancia' | 'rating' | 'anio'.
 */
function sortGrid(grid, field) {
  const cards = Array.from(grid.querySelectorAll('.rec-card'));

  cards.sort((a, b) => {
    const va = parseFloat(a.dataset[field]) || 0;
    const vb = parseFloat(b.dataset[field]) || 0;
    return vb - va; // descendente
  });

  const fragment = document.createDocumentFragment();
  cards.forEach(card => fragment.appendChild(card));
  grid.appendChild(fragment);
}
