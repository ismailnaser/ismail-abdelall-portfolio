(function () {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const canHover = window.matchMedia("(hover: hover)").matches;
  if (canHover) document.body.classList.add("weird-mode");

  function initMagnetic() {
    const strength = 0.35;
    document
      .querySelectorAll(
        ".btn-primary, .btn-secondary, .link-btn:not(.project-back), .btn-ghost, .btn-icon"
      )
      .forEach((el) => {
        el.addEventListener("mousemove", (e) => {
          const rect = el.getBoundingClientRect();
          const x = (e.clientX - rect.left - rect.width / 2) * strength;
          const y = (e.clientY - rect.top - rect.height / 2) * strength;
          el.style.transform = `translate(${x}px, ${y}px)`;
        });
        el.addEventListener("mouseleave", () => {
          el.style.transform = "";
        });
      });
  }

  function initScrollParallax() {
    /* Disabled — conflicts with scroll-fly left/right reveal transforms */
  }

  function initFloatDelays() {
    document.querySelectorAll(".tilt-card.is-visible, .tilt-card").forEach((card, i) => {
      card.style.setProperty("--float-delay", `${(i % 7) * 0.35}s`);
    });
  }

  const revealObserver = new MutationObserver(() => {
    initFloatDelays();
  });
  const main = document.querySelector(".main-content");
  if (main) {
    revealObserver.observe(main, { childList: true, subtree: true, attributes: true, attributeFilter: ["class"] });
  }

  if (canHover) initMagnetic();
  initScrollParallax();
  initFloatDelays();

  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) initFloatDelays();
  });
})();
