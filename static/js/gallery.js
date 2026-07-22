(function () {
  const lightbox = document.getElementById("lightbox");
  if (!lightbox) return;

  // Keep lightbox above sidebar / main stacking contexts
  if (lightbox.parentElement !== document.body) {
    document.body.appendChild(lightbox);
  }

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
    document.body.classList.add("lightbox-open");
    document.body.style.overflow = "hidden";
    lightbox.querySelector(".lightbox-close")?.focus();
  }

  function closeLightbox() {
    lightbox.hidden = true;
    lightbox.setAttribute("aria-hidden", "true");
    document.body.classList.remove("lightbox-open");
    document.body.style.overflow = "";
    imgEl.src = "";
  }

  buttons.forEach((btn, i) => {
    btn.addEventListener("click", () => openLightbox(i));
  });

  lightbox.querySelectorAll(".lightbox-close").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      closeLightbox();
    });
  });

  lightbox.querySelector(".lightbox-prev")?.addEventListener("click", (e) => {
    e.stopPropagation();
    showAt(currentIndex - 1);
  });
  lightbox.querySelector(".lightbox-next")?.addEventListener("click", (e) => {
    e.stopPropagation();
    showAt(currentIndex + 1);
  });

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
