/**
 * Single image preview + cropper for Django admin.
 * User chooses the visible crop area; cropped file is what gets saved.
 */
(function () {
  const CROPPER_JS = "https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.2/cropper.min.js";
  const CROPPER_CSS = "https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.2/cropper.min.css";

  const EMPTY_HINT = "اختر صورة، بعدين حرّك مربع الاقتصاص لتحديد الجزء الظاهر في الموقع";

  function loadAsset(href, type) {
    return new Promise((resolve, reject) => {
      if (type === "css") {
        if ([...document.styleSheets].some((s) => s.href && s.href.includes("cropper"))) {
          resolve();
          return;
        }
        const link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = href;
        link.onload = () => resolve();
        link.onerror = reject;
        document.head.appendChild(link);
        return;
      }
      if (window.Cropper) {
        resolve();
        return;
      }
      const script = document.createElement("script");
      script.src = href;
      script.onload = () => resolve();
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  function ensureAssets() {
    return Promise.all([loadAsset(CROPPER_CSS, "css"), loadAsset(CROPPER_JS, "js")]);
  }

  function fieldKind(input) {
    const name = (input.name || "").toLowerCase();
    if (name.includes("photo")) return "photo";
    if (name.includes("gallery") || name.includes("projectimage")) return "gallery";
    if (name.includes("image")) return "project";
    return "project";
  }

  function cropConfig(kind) {
    if (kind === "photo") {
      return {
        aspectRatio: 1,
        label: "اقتصاص دائري للصورة الشخصية (١:١)",
        width: 800,
        height: 800,
        viewMode: 1,
      };
    }
    return {
      aspectRatio: 4 / 3,
      label: "اقتصاص صورة المشروع (٤:٣)",
      width: 1200,
      height: 900,
      viewMode: 1,
    };
  }

  function findSavedImageNear(input) {
    const row =
      input.closest(".form-group, .form-row, .fieldBox, td, .flex-container") ||
      input.parentElement;
    if (!row) return null;

    const currentLink = row.querySelector('a[href*="/media/"]');
    if (currentLink) return currentLink.href;

    const img = row.querySelector("img.admin-thumb, img.admin-thumb-lg, .file-upload img");
    if (img && img.src) return img.src;

    return null;
  }

  function hideDjangoCurrentPreview(input) {
    const row =
      input.closest(".form-group, .form-row, .fieldBox, td") || input.parentElement;
    if (!row) return;
    row.querySelectorAll("a[href*='/media/']").forEach((a) => {
      if (a.querySelector("img")) return;
      const p = a.closest("p");
      if (p && p.classList.contains("file-upload")) return;
      // Keep the clear checkbox / "Currently" text but hide large duplicate previews
    });
    row.querySelectorAll(".admin-thumb, .admin-thumb-lg").forEach((el) => {
      if (!el.closest(".admin-crop-panel")) el.style.display = "none";
    });
  }

  function createCropPanel(input) {
    const kind = fieldKind(input);
    const cfg = cropConfig(kind);
    const panel = document.createElement("div");
    panel.className = "admin-crop-panel";
    panel.dataset.kind = kind;
    panel.innerHTML = `
      <p class="admin-crop-panel__label">${cfg.label}</p>
      <div class="admin-crop-panel__stage">
        <img class="admin-crop-panel__img" alt="معاينة الاقتصاص" hidden />
        <div class="admin-crop-panel__empty">${EMPTY_HINT}</div>
      </div>
      <div class="admin-crop-panel__result">
        <span class="admin-crop-panel__result-label">شكل الظهور في الموقع</span>
        <div class="admin-crop-panel__result-frame admin-crop-panel__result-frame--${kind}">
          <img class="admin-crop-panel__result-img" alt="نتيجة الاقتصاص" hidden />
        </div>
      </div>
      <div class="admin-crop-panel__actions">
        <button type="button" class="admin-img-btn admin-img-btn--small" data-action="zoom-in">تكبير</button>
        <button type="button" class="admin-img-btn admin-img-btn--small" data-action="zoom-out">تصغير</button>
        <button type="button" class="admin-img-btn admin-img-btn--small admin-img-btn--ghost" data-action="reset">إعادة ضبط</button>
        <button type="button" class="admin-img-btn admin-img-btn--small admin-img-btn--ghost" data-action="clear" hidden>إلغاء الصورة الجديدة</button>
      </div>
      <p class="admin-crop-panel__hint">اسحب مربع الاقتصاص أو حرّك الصورة لتحديد الجزء اللي بدك إياه. عند الحفظ بتنحفظ الصورة بعد الاقتصاص.</p>
    `;

    const stageImg = panel.querySelector(".admin-crop-panel__img");
    const empty = panel.querySelector(".admin-crop-panel__empty");
    const resultImg = panel.querySelector(".admin-crop-panel__result-img");
    const clearBtn = panel.querySelector('[data-action="clear"]');

    let cropper = null;
    let objectUrl = null;
    let dirty = false;
    let ready = false;
    let previewTimer = null;

    function destroyCropper() {
      if (cropper) {
        cropper.destroy();
        cropper = null;
      }
      ready = false;
    }

    function updateResultPreview() {
      if (!cropper) return;
      const canvas = cropper.getCroppedCanvas({
        width: Math.min(cfg.width, 360),
        height: Math.min(cfg.height, 360),
        imageSmoothingEnabled: true,
        imageSmoothingQuality: "high",
      });
      if (!canvas) return;
      resultImg.hidden = false;
      resultImg.src = canvas.toDataURL("image/jpeg", 0.9);
    }

    function schedulePreview() {
      clearTimeout(previewTimer);
      previewTimer = setTimeout(updateResultPreview, 80);
    }

    function markDirty() {
      if (!ready) return;
      dirty = true;
    }

    function startCropper(src, isLocal) {
      destroyCropper();
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
        objectUrl = null;
      }
      if (isLocal) objectUrl = src;

      dirty = !!isLocal;
      clearBtn.hidden = !isLocal;
      empty.hidden = true;
      stageImg.hidden = false;
      stageImg.src = src;

      const onReady = () => {
        cropper = new window.Cropper(stageImg, {
          aspectRatio: cfg.aspectRatio,
          viewMode: cfg.viewMode,
          dragMode: "move",
          autoCropArea: 0.85,
          responsive: true,
          background: false,
          guides: true,
          center: true,
          highlight: false,
          cropBoxMovable: true,
          cropBoxResizable: true,
          toggleDragModeOnDblclick: false,
          ready() {
            ready = true;
            schedulePreview();
          },
          crop() {
            schedulePreview();
          },
          cropend() {
            markDirty();
          },
          zoom() {
            markDirty();
          },
        });
      };

      if (stageImg.complete && stageImg.naturalWidth) onReady();
      else stageImg.onload = onReady;
    }

    function resetPanel() {
      destroyCropper();
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
        objectUrl = null;
      }
      stageImg.removeAttribute("src");
      stageImg.hidden = true;
      resultImg.removeAttribute("src");
      resultImg.hidden = true;
      empty.hidden = false;
      clearBtn.hidden = true;
      dirty = false;
    }

    panel.querySelector('[data-action="zoom-in"]').addEventListener("click", () => {
      if (cropper) cropper.zoom(0.1);
    });
    panel.querySelector('[data-action="zoom-out"]').addEventListener("click", () => {
      if (cropper) cropper.zoom(-0.1);
    });
    panel.querySelector('[data-action="reset"]').addEventListener("click", () => {
      if (cropper) {
        cropper.reset();
        schedulePreview();
      }
    });
    clearBtn.addEventListener("click", () => {
      input.value = "";
      resetPanel();
      const saved = findSavedImageNear(input);
      if (saved) startCropper(saved, false);
    });

    input.addEventListener("change", () => {
      const file = input.files && input.files[0];
      if (!file) {
        resetPanel();
        const saved = findSavedImageNear(input);
        if (saved) startCropper(saved, false);
        return;
      }
      if (!file.type.startsWith("image/")) {
        resetPanel();
        empty.textContent = "الملف المختار مش صورة";
        empty.hidden = false;
        return;
      }
      empty.textContent = EMPTY_HINT;
      startCropper(URL.createObjectURL(file), true);
    });

    const form = input.closest("form");
    if (form && !form.dataset.cropSubmitBound) {
      form.dataset.cropSubmitBound = "1";
      form.addEventListener(
        "submit",
        (e) => {
          if (form.dataset.cropCommitted === "1") {
            delete form.dataset.cropCommitted;
            return;
          }

          const jobs = [...form.querySelectorAll(".admin-crop-panel")]
            .map((p) => p._cropApi)
            .filter((api) => api && api.needsCommit());

          if (!jobs.length) return;

          e.preventDefault();
          e.stopImmediatePropagation();

          Promise.all(jobs.map((api) => api.commit()))
            .then(() => {
              form.dataset.cropCommitted = "1";
              if (typeof form.requestSubmit === "function") {
                const submitter = e.submitter;
                if (submitter) form.requestSubmit(submitter);
                else form.requestSubmit();
              } else {
                HTMLFormElement.prototype.submit.call(form);
              }
            })
            .catch((err) => {
              console.error(err);
              alert("تعذر تجهيز الصورة المقصوصة. حاول مرة ثانية.");
            });
        },
        true
      );
    }

    panel._cropApi = {
      needsCommit() {
        return !!(cropper && dirty);
      },
      commit() {
        return new Promise((resolve, reject) => {
          if (!cropper) {
            resolve();
            return;
          }
          const canvas = cropper.getCroppedCanvas({
            width: cfg.width,
            height: cfg.height,
            imageSmoothingEnabled: true,
            imageSmoothingQuality: "high",
          });
          if (!canvas) {
            reject(new Error("no canvas"));
            return;
          }
          canvas.toBlob(
            (blob) => {
              if (!blob) {
                reject(new Error("no blob"));
                return;
              }
              const base =
                (input.files && input.files[0] && input.files[0].name) ||
                (kind === "photo" ? "profile.jpg" : "image.jpg");
              const name = base.replace(/\.\w+$/, "") + "-cropped.jpg";
              const file = new File([blob], name, { type: "image/jpeg" });
              const dt = new DataTransfer();
              dt.items.add(file);
              input.files = dt.files;
              dirty = false;
              resolve();
            },
            "image/jpeg",
            0.92
          );
        });
      },
    };

    // Initial load of existing image into the same crop UI
    const saved = findSavedImageNear(input);
    if (saved) startCropper(saved, false);

    return panel;
  }

  function bindFileInput(input) {
    if (!input || input.dataset.previewBound) return;
    if (input.disabled) return;

    input.dataset.previewBound = "1";
    input.setAttribute("accept", "image/*");
    hideDjangoCurrentPreview(input);

    const panel = createCropPanel(input);
    input.insertAdjacentElement("afterend", panel);
  }

  function scan(root) {
    const scope = root || document;
    // Hide separate readonly preview fields — one crop panel is enough
    scope
      .querySelectorAll(".field-photo_preview, .field-image_preview, .field-preview")
      .forEach((el) => {
        el.style.display = "none";
      });

    scope.querySelectorAll('input[type="file"]').forEach((input) => {
      const name = (input.name || "").toLowerCase();
      const accept = (input.getAttribute("accept") || "").toLowerCase();
      const looksLikeImage =
        name.includes("image") ||
        name.includes("photo") ||
        !accept ||
        accept.includes("image");
      if (looksLikeImage) bindFileInput(input);
    });
  }

  function init() {
    ensureAssets()
      .then(() => {
        scan(document);
        document.addEventListener("formset:added", (e) => scan(e.target));
        document.addEventListener("click", (e) => {
          if (e.target.closest(".add-row a, a.add-row")) {
            setTimeout(() => scan(document), 80);
          }
        });
      })
      .catch((err) => {
        console.error("Cropper failed to load", err);
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
