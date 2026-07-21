(function () {
  const STORAGE_THEME = "portfolio-theme";
  const STORAGE_LANG = "portfolio-lang";

  const html = document.documentElement;
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("menu-overlay");
  const menuOpen = document.getElementById("menu-open");
  const navLinks = document.querySelectorAll(".nav-link");
  const sections = document.querySelectorAll(".section, .hero-section");

  function setTheme(dark) {
    html.classList.toggle("dark", dark);
    html.dataset.theme = dark ? "dark" : "light";
    localStorage.setItem(STORAGE_THEME, dark ? "dark" : "light");

    // نهاري → قمر (انتقال لليل) | ليلي → شمس (انتقال للنهار)
    document.querySelectorAll(".theme-icon-moon").forEach((el) => {
      el.classList.toggle("hidden", dark);
    });
    document.querySelectorAll(".theme-icon-sun").forEach((el) => {
      el.classList.toggle("hidden", !dark);
    });

    const mobileTheme = document.getElementById("theme-toggle-mobile");
    if (mobileTheme) {
      mobileTheme.textContent = dark ? "☀" : "☽";
      mobileTheme.setAttribute(
        "aria-label",
        dark ? "Switch to light mode" : "Switch to dark mode"
      );
    }

    const themeToggle = document.getElementById("theme-toggle");
    if (themeToggle) {
      themeToggle.setAttribute(
        "aria-label",
        dark ? "Switch to light mode" : "Switch to dark mode"
      );
    }

    document.querySelectorAll(".theme-label").forEach((el) => {
      const isAr = html.lang === "ar";
      if (dark) {
        el.textContent = isAr ? el.dataset.arDark : el.dataset.enDark;
      } else {
        el.textContent = isAr ? el.dataset.arLight : el.dataset.enLight;
      }
    });
  }

  function toggleTheme() {
    setTheme(!html.classList.contains("dark"));
  }

  function applyLanguage(lang) {
    const isAr = lang === "ar";
    html.lang = lang;
    html.dir = isAr ? "rtl" : "ltr";
    document.body.classList.toggle("is-rtl", isAr);
    localStorage.setItem(STORAGE_LANG, lang);

    document.querySelectorAll("[data-en][data-ar]").forEach((el) => {
      const text = isAr ? el.dataset.ar : el.dataset.en;
      if (text) el.textContent = text;
    });

    document.querySelectorAll(".form-input").forEach((input) => {
      const ph = isAr ? input.dataset.placeholderAr : input.getAttribute("placeholder");
      if (ph) input.placeholder = ph;
    });

    // إنجليزي → ع | عربي → E
    const langIcon = isAr ? "E" : "ع";
    const langAria = isAr ? "Switch to English" : "Switch to Arabic";

    const langBtn = document.getElementById("lang-toggle");
    const langLabel = langBtn?.querySelector(".lang-toggle-label");
    if (langLabel) langLabel.textContent = langIcon;
    if (langBtn) langBtn.setAttribute("aria-label", langAria);

    const langMobile = document.getElementById("lang-toggle-mobile");
    if (langMobile) {
      langMobile.textContent = langIcon;
      langMobile.setAttribute("aria-label", langAria);
    }

    const photoBtn = document.querySelector(".intro-photo-btn");
    if (photoBtn) {
      photoBtn.setAttribute(
        "aria-label",
        isAr ? photoBtn.dataset.arLabel || "عرض الصورة الشخصية" : photoBtn.dataset.enLabel || "View profile photo"
      );
    }

    setTheme(html.classList.contains("dark"));
    closeMenu();
  }

  function toggleLanguage() {
    applyLanguage(html.lang === "ar" ? "en" : "ar");
  }

  function openMenu() {
    sidebar?.classList.add("is-open");
    overlay?.classList.add("is-visible");
    menuOpen?.setAttribute("aria-expanded", "true");
  }

  function closeMenu() {
    sidebar?.classList.remove("is-open");
    overlay?.classList.remove("is-visible");
    menuOpen?.setAttribute("aria-expanded", "false");
  }

  function initNavSpy() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const id = entry.target.id;
          navLinks.forEach((link) => {
            link.classList.toggle("is-active", link.dataset.section === id);
          });
        });
      },
      { rootMargin: "-40% 0px -50% 0px", threshold: 0 }
    );
    sections.forEach((section) => {
      if (section.id) observer.observe(section);
    });
  }

  function initScrollProgress() {
    const bar = document.createElement("div");
    bar.className = "scroll-progress";
    bar.setAttribute("aria-hidden", "true");
    document.body.prepend(bar);

    function updateProgress() {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = docHeight > 0 ? scrollTop / docHeight : 0;
      bar.style.transform = `scaleX(${Math.min(1, Math.max(0, progress))})`;
    }

    window.addEventListener("scroll", updateProgress, { passive: true });
    updateProgress();
  }

  const SECTION_FLY_SELECTORS =
    ".section-title, .section-lead, .project-card, .service-card, .channel-card, " +
    ".gallery-item, .skill-tag, .about-list li, .project-detail-cover, .project-detail-title, " +
    ".project-detail-stack, .project-detail-actions, .project-detail-text, .project-gallery-title, " +
    ".contact-form .form-row, .contact-form .btn-primary, .form-success, .project-back";

  function getSectionFlyItems(section) {
    if (section.classList.contains("hero-section")) {
      return [
        ...section.querySelectorAll(
          ".hero-eyebrow, .hero-subtitle, .hero-actions > *"
        ),
      ];
    }
    return [...section.querySelectorAll(SECTION_FLY_SELECTORS)];
  }

  function flySide(indexInSection, sectionIndex) {
    return (indexInSection + sectionIndex) % 2 === 0 ? "reveal-from-left" : "reveal-from-right";
  }

  function applyScrollFly(el, indexInSection, sectionIndex) {
    el.classList.remove("reveal-scale", "reveal-hero");
    el.classList.add("reveal", "scroll-fly", flySide(indexInSection, sectionIndex));

    let distance = 110;
    if (el.classList.contains("skill-tag")) distance = 64;
    else if (el.classList.contains("section-title")) distance = 128;
    else if (el.classList.contains("section-lead")) distance = 100;
    else if (el.matches(".form-row, .project-back")) distance = 80;

    distance += (indexInSection % 3) * 18;
    el.style.setProperty("--fly-distance", `${distance}px`);
    el.style.setProperty("--reveal-stagger", `${indexInSection * 100}ms`);
  }

  function revealSection(section, sectionIndex, instant = false) {
    const items = getSectionFlyItems(section);
    items.forEach((el, i) => applyScrollFly(el, i, sectionIndex));

    const flyItems = items.filter((el) => el.classList.contains("scroll-fly"));
    if (!flyItems.length) return;

    section.classList.add("scroll-section");

    const show = () => {
      section.classList.add("section-in-view");
      flyItems.forEach((el, i) => {
        const delay = instant ? 70 + i * 110 : i * 115;
        setTimeout(() => el.classList.add("is-visible"), delay);
      });
    };

    if (instant) {
      show();
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          show();
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.14, rootMargin: "0px 0px -8% 0px" }
    );
    observer.observe(section);
  }

  function initScrollReveal() {
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const sections = [
      ...document.querySelectorAll(".hero-section"),
      ...document.querySelectorAll(".section"),
      ...document.querySelectorAll(".project-detail"),
    ];

    if (reducedMotion) {
      sections.forEach((section) => {
        getSectionFlyItems(section).forEach((el) => {
          el.classList.add("reveal", "is-visible");
        });
      });
      return;
    }

    sections.forEach((section, index) => {
      const instant = section.classList.contains("hero-section");
      revealSection(section, index, instant);
    });
  }

  function initTiltCards() {
    /* Replaced by simple CSS hover in styles.css */
  }

  function initPhotoLightbox() {
    const lightbox = document.getElementById("photo-lightbox");
    const img = lightbox?.querySelector(".photo-lightbox-img");
    const trigger = document.querySelector(".intro-photo-btn");
    if (!lightbox || !img || !trigger) return;

    function open() {
      const src = trigger.getAttribute("data-photo-src");
      const alt = trigger.getAttribute("data-photo-alt") || "";
      if (!src) return;
      img.src = src;
      img.alt = alt;
      lightbox.hidden = false;
      document.body.classList.add("lightbox-open");
      lightbox.querySelector(".photo-lightbox-close")?.focus();
    }

    function close() {
      lightbox.hidden = true;
      img.removeAttribute("src");
      document.body.classList.remove("lightbox-open");
      trigger.focus();
    }

    trigger.addEventListener("click", open);
    lightbox.querySelectorAll("[data-lightbox-close]").forEach((el) => {
      el.addEventListener("click", close);
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && !lightbox.hidden) close();
    });
  }

  const savedTheme = localStorage.getItem(STORAGE_THEME);
  setTheme(savedTheme === "dark");

  const savedLang = localStorage.getItem(STORAGE_LANG) || "en";
  applyLanguage(savedLang);

  window.addEventListener("resize", () => {
    if (window.innerWidth >= 1024) closeMenu();
  });

  document.getElementById("theme-toggle")?.addEventListener("click", toggleTheme);
  document.getElementById("theme-toggle-mobile")?.addEventListener("click", toggleTheme);
  document.getElementById("lang-toggle")?.addEventListener("click", toggleLanguage);
  document.getElementById("lang-toggle-mobile")?.addEventListener("click", toggleLanguage);

  menuOpen?.addEventListener("click", openMenu);
  overlay?.addEventListener("click", closeMenu);

  navLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      const hash = link.getAttribute("href")?.split("#")[1];
      if (!hash) return;

      const target = document.getElementById(hash);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
        history.pushState(null, "", `#${hash}`);
      }
      // If target not on this page, allow normal navigation to /#section

      if (window.innerWidth < 1024) closeMenu();
    });
  });

  document.getElementById("sidebar-brand")?.addEventListener("click", (e) => {
    const top = document.getElementById("top");
    if (top && window.location.pathname === "/") {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
      history.pushState(null, "", "#top");
    }
    if (window.innerWidth < 1024) closeMenu();
  });

  initNavSpy();
  initScrollProgress();
  initScrollReveal();
  initTiltCards();
  initPhotoLightbox();
})();
