
/**
 * @param {string} userId  - ID del usuario en sesión (vacío si no autenticado).
 * @param {string} movieId - ID de la película actual.
 */
function initDetailRatings(userId, movieId) {
  if (!userId || !movieId) return;

  const starContainer = document.getElementById('star-selector');
  const submitBtn     = document.getElementById('submit-rating');
  const deleteBtn     = document.getElementById('delete-rating');
  const labelEl       = document.getElementById('rating-label');

  if (!starContainer) return;

  const starBtns    = starContainer.querySelectorAll('.star');
  let selectedScore = parseInt(starContainer.dataset.current, 10) || 0;

  // Interacción con estrellas 
  starBtns.forEach(star => {
    star.addEventListener('mouseenter', () => highlightStars(starBtns, parseInt(star.dataset.value, 10)));
    star.addEventListener('mouseleave', () => highlightStars(starBtns, selectedScore));
    star.addEventListener('click', () => {
      selectedScore = parseInt(star.dataset.value, 10);
      if (labelEl) {
        labelEl.textContent = `Tu puntaje: ${selectedScore}/5 — ${scoreLabel(selectedScore)}`;
      }
      if (submitBtn) submitBtn.disabled = false;
      highlightStars(starBtns, selectedScore);
    });
  });

  // Guardar 
  if (submitBtn) {
    submitBtn.addEventListener('click', async () => {
      if (!selectedScore) return;
      submitBtn.disabled    = true;
      submitBtn.textContent = 'Guardando…';

      const ok = await postRating(userId, movieId, selectedScore);

      submitBtn.textContent = 'Guardar calificación';
      submitBtn.disabled    = false;

      if (ok) {
        showToast(`✓ Puntaje ${selectedScore}/5 guardado`);
        // Añade botón eliminar si no existía (primera calificación)
        if (!document.getElementById('delete-rating')) {
          const btn = document.createElement('button');
          btn.id          = 'delete-rating';
          btn.className   = 'btn-danger';
          btn.textContent = 'Eliminar calificación';
          submitBtn.parentElement.appendChild(btn);
          setupDeleteBtn(btn, userId, movieId, starBtns, labelEl, submitBtn);
        }
      } else {
        showToast('Error al guardar. Inténtalo de nuevo.', true);
      }
    });
  }

  //  Eliminar 
  if (deleteBtn) {
    setupDeleteBtn(deleteBtn, userId, movieId, starBtns, labelEl, submitBtn);
  }
}

function setupDeleteBtn(btn, userId, movieId, starBtns, labelEl, submitBtn) {
  btn.addEventListener('click', async () => {
    btn.disabled    = true;
    btn.textContent = 'Eliminando…';

    const ok = await deleteRating(userId, movieId);

    if (ok) {
      resetStars(starBtns);
      if (labelEl) labelEl.textContent = 'Selecciona una puntuación';
      if (submitBtn) submitBtn.disabled = true;
      btn.remove();
      showToast('Calificación eliminada.');
    } else {
      btn.disabled    = false;
      btn.textContent = 'Eliminar calificación';
      showToast('Error al eliminar.', true);
    }
  });
}




async function postRating(userId, movieId, puntaje) {
  try {
    const res = await fetch('/ratings/', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ user_id: userId, movie_id: movieId, puntaje }),
    });
    return res.ok;
  } catch {
    return false;
  }
}

async function deleteRating(userId, movieId) {
  try {
    const res = await fetch('/ratings/', {
      method:  'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ user_id: userId, movie_id: movieId }),
    });
    return res.ok;
  } catch {
    return false;
  }
}




function highlightStars(stars, upTo) {
  stars.forEach((s, i) => s.classList.toggle('active', i < upTo));
}

function resetStars(stars) {
  stars.forEach(s => s.classList.remove('active'));
}

/**
 * Devuelve la etiqueta textual para un puntaje 1–5.
 * Retorna cadena vacía para valores fuera de rango.
 * @param {number} score - Puntaje (1–5).
 */
function scoreLabel(score) {
  const labels = ['', 'Muy malo', 'Malo', 'Regular', 'Bueno', 'Excelente'];
  return labels[score] || '';
}

/**
 * Muestra un toast de notificación temporal.
 * Usa clases CSS definidas en style.css (toast-success / toast-error).
 * El contenedor #toast-container está en base.html.
 *
 * GLOBAL: disponible para cualquier script cargado después de ratings.js
 * 
 *
 * @param {string}  message - Texto del toast.
 * @param {boolean} isError - Si true, aplica clase toast-error.
 */
function showToast(message, isError = false) {
  const container = document.getElementById('toast-container') || document.body;

  const toast = document.createElement('div');
  toast.className = `toast ${isError ? 'toast-error' : 'toast-success'}`;
  toast.textContent = message;
  toast.setAttribute('role', 'status');
  toast.setAttribute('aria-live', 'polite');

  container.appendChild(toast);

  // Usa evento animationend para el fade-out: más robusto entre navegadores
  // que modificar .style.animation directamente.
  setTimeout(() => {
    toast.classList.add('toast-leaving');
    const onEnd = () => toast.remove();
    toast.addEventListener('animationend', onEnd, { once: true });
    // Fallback por si animationend no se dispara (ej. prefers-reduced-motion)
    setTimeout(onEnd, 400);
  }, 3000);
}
