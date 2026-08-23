// Cuenta regresiva simple para los tiempos de preparación estimados.
// Cada elemento con [data-hora-lista] tiene un timestamp ISO objetivo.
(function () {
  function actualizar() {
    document.querySelectorAll("[data-hora-lista]").forEach(function (el) {
      const objetivo = new Date(el.getAttribute("data-hora-lista")).getTime();
      if (!objetivo) return;
      const ahora = Date.now();
      const diffSeg = Math.round((objetivo - ahora) / 1000);

      el.classList.remove("urgente", "pronto");
      if (diffSeg <= 0) {
        el.textContent = "Listo";
        el.classList.add("urgente");
        return;
      }
      const min = Math.floor(diffSeg / 60);
      const seg = diffSeg % 60;
      el.textContent = min + ":" + String(seg).padStart(2, "0") + " min";
      if (diffSeg <= 120) el.classList.add("urgente");
      else if (diffSeg <= 300) el.classList.add("pronto");
    });
  }
  actualizar();
  setInterval(actualizar, 1000);

  // Auto-recarga suave de los paneles operativos para reflejar nuevos pedidos.
  const intervalo = document.body.getAttribute("data-auto-recarga");
  if (intervalo) {
    setTimeout(function () {
      window.location.reload();
    }, parseInt(intervalo, 10) * 1000);
  }
})();
