document.addEventListener('DOMContentLoaded', () => {
  const grid = document.getElementById('movies-grid');
  if (!grid) return;

  // Si catalog.html ya inyectó #live-search, no duplicamos el listener
  const existing = document.getElementById('live-search');
  if (existing) return;

  // ── Crear campo de búsqueda e insertarlo en el formulario ───
  const searchInput = document.createElement('input');
  searchInput.type        = 'text';
  searchInput.placeholder = 'Buscar por título…';
  searchInput.id          = 'live-search';
  searchInput.style.cssText = 'flex:1; min-width:160px;';

  const form = document.querySelector('.filters-form');
  if (form) {
    form.insertBefore(searchInput, form.firstChild);

    // Evitar que Enter envíe el formulario al escribir en live-search
    searchInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') e.preventDefault();
    });
  }

  // ── Filtrado con debounce ────────────────────────────────────
  searchInput.addEventListener('input', debounce(() => {
    const q = searchInput.value.trim().toLowerCase();
    filterCards(grid, q);
  }, 220));
});

/**
 * Muestra u oculta tarjetas según si el título contiene la query.
 * @param {HTMLElement} grid  - Contenedor de tarjetas.
 * @param {string}      query - Texto a buscar (ya en minúsculas).
 */
function filterCards(grid, query) {
  let visible = 0;

  grid.querySelectorAll('.movie-card').forEach(card => {
    const title = card.querySelector('h3')?.textContent.toLowerCase() || '';
    const match = !query || title.includes(query);
    card.style.display = match ? '' : 'none';
    if (match) visible++;
  });

  // Mostrar o esconder mensaje "sin resultados"
  let noResults = document.getElementById('no-results-msg');
  if (visible === 0) {
    if (noResults) noResults.style.display = 'block';
  } else {
    if (noResults) noResults.style.display = 'none';
  }
}

/**
 * Limita la frecuencia de ejecución de una función.
 * @param {Function} fn    - Función a ejecutar.
 * @param {number}   delay - Milisegundos de espera.
 */
function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}
