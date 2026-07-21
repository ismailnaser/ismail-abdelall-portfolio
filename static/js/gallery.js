(function () {
  const lightbox = document.getElementById("lightbox");
  if (!lightbox) return;

  const imgEl = document.getElementById("lightbox-img");
  const captionEl = document.getElementById("lightbox-caption");
  const buttons = Array.from(document.querySelectorAll(".gallery-thumb-btn"));
  let currentIndex = 0;

  function captionFor(btn) {
    const isAr = document.documentElement.lang === "ar";
    const en = btn.dataset.captionEn || "";
    const ar = btn.dataset.captionAr || "";
    return isAr && ar ? ar : en;
  }

  function showAt(index) {
    if (!buttons.length) return;
    currentIndex = (index + buttons.length) % buttons.length;
    const btn = buttons[currentIndex];
    imgEl.src = btn.dataset.full;
    imgEl.alt = captionFor(btn) || "Gallery image";
    captionEl.textContent = captionFor(btn);
    captionEl.hidden = !captionEl.textContent;
  }

  function openLightbox(index) {
    showAt(index);
    lightbox.hidden = false;
    lightbox.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeLightbox() {
    lightbox.hidden = true;
    lightbox.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    imgEl.src = "";
  }

  buttons.forEach((btn, i) => {
    btn.addEventListener("click", () => openLightbox(i));
  });

  lightbox.querySelector(".lightbox-close")?.addEventListener("click", closeLightbox);
  lightbox.querySelector(".lightbox-prev")?.addEventListener("click", () => showAt(currentIndex - 1));
  lightbox.querySelector(".lightbox-next")?.addEventListener("click", () => showAt(currentIndex + 1));

  lightbox.addEventListener("click", (e) => {
    if (e.target === lightbox) closeLightbox();
  });

  document.addEventListener("keydown", (e) => {
    if (lightbox.hidden) return;
    if (e.key === "Escape") closeLightbox();
    if (e.key === "ArrowLeft") showAt(currentIndex - 1);
    if (e.key === "ArrowRight") showAt(currentIndex + 1);
  });
})();
