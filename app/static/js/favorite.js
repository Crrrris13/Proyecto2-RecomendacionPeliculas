function initFavorites(userId, movieId, isFav) {
  if (!userId || !movieId) return;

  const btn = document.getElementById("favorite-btn");
  if (!btn) return;

  let favorito = isFav;
  updateBtn(btn, favorito);

  btn.addEventListener("click", async () => {
    btn.disabled = true;

    try {
      const res = await fetch("/favorites/", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ movie_id: movieId }),
      });

      if (res.ok) {
        const data = await res.json();
        favorito = data.favorito;
        updateBtn(btn, favorito);
        // showToast está definida en ratings.js
        if (typeof showToast === "function") {
          showToast(data.favorito ? "❤️ Agregado a favoritos" : "💔 Eliminado de favoritos");
        }
      } else {
        if (typeof showToast === "function") {
          showToast("No se pudo actualizar favorito.", true);
        }
      }
    } catch {
      if (typeof showToast === "function") {
        showToast("Error de conexión.", true);
      }
    } finally {
      btn.disabled = false;
    }
  });
}

function updateBtn(btn, isFav) {
  btn.textContent = isFav ? "❤️ En favoritos" : "♡ Agregar a favoritos";
  btn.classList.toggle("btn-primary", isFav);
  btn.classList.toggle("btn-outline", !isFav);
}