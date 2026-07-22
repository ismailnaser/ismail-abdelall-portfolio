/**
 * Admin image preview with optional crop.
 * Default: keep the original image. Crop only when the user enables it.
 */
(function () {
  const CROPPER_JS = "https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.2/cropper.min.js";
  const CROPPER_CSS = "https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.2/cropper.min.css";

  const EMPTY_HINT = "اختر صورة — الافتراضي حفظها كاملة بدون اقتصاص";

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
        label: "معاينة الصورة الشخصية",
        width: 800,
        height: 800,
        viewMode: 1,
      };
    }
    if (kind === "gallery") {
      return {
        aspectRatio: 4 / 3,
        label: "معاينة صورة المعرض",
        width: 1200,
        height: 900,
        viewMode: 1,
      };
    }
    return {
      aspectRatio: 4 / 3,
      label: "معاينة صورة المشروع",
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

    const currentLink = row.querySelector('a[href*="/media/"], a[href*="cloudinary"]');
    if (currentLink) return currentLink.href;

    const img = row.querySelector("img.admin-thumb, img.admin-thumb-lg, .file-upload img");
    if (img && img.src) return img.src;

    return null;
  }

  function hideDjangoCurrentPreview(input) {
    const row =
      input.closest(".form-group, .form-row, .fieldBox, td") || input.parentElement;
    if (!row) return;
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
    panel.dataset.cropEnabled = "0";
    panel.innerHTML = `
      <p class="admin-crop-panel__label">${cfg.label}</p>
      <div class="admin-crop-panel__stage">
        <img class="admin-crop-panel__img" alt="معاينة الصورة" hidden />
        <div class="admin-crop-panel__empty">${EMPTY_HINT}</div>
      </div>
      <div class="admin-crop-panel__result" hidden>
        <span class="admin-crop-panel__result-label">شكل الظهور بعد الاقتصاص</span>
        <div class="admin-crop-panel__result-frame admin-crop-panel__result-frame--${kind}">
          <img class="admin-crop-panel__result-img" alt="نتيجة الاقتصاص" hidden />
        </div>
      </div>
      <div class="admin-crop-panel__actions">
        <button type="button" class="admin-img-btn admin-img-btn--small admin-img-btn--ghost" data-action="toggle-crop">تفعيل الاقتصاص</button>
        <button type="button" class="admin-img-btn admin-img-btn--small" data-action="zoom-in" hidden>تكبير</button>
        <button type="button" class="admin-img-btn admin-img-btn--small" data-action="zoom-out" hidden>تصغير</button>
        <button type="button" class="admin-img-btn admin-img-btn--small admin-img-btn--ghost" data-action="reset" hidden>إعادة ضبط</button>
        <button type="button" class="admin-img-btn admin-img-btn--small admin-img-btn--ghost" data-action="clear" hidden>إلغاء الصورة الجديدة</button>
      </div>
      <p class="admin-crop-panel__hint">الصورة بتنحفظ كاملة. إذا حابب تقتص جزء معيّن، اضغط «تفعيل الاقتصاص».</p>
    `;

    const stageImg = panel.querySelector(".admin-crop-panel__img");
    const empty = panel.querySelector(".admin-crop-panel__empty");
    const resultWrap = panel.querySelector(".admin-crop-panel__result");
    const resultImg = panel.querySelector(".admin-crop-panel__result-img");
    const clearBtn = panel.querySelector('[data-action="clear"]');
    const toggleBtn = panel.querySelector('[data-action="toggle-crop"]');
    const zoomInBtn = panel.querySelector('[data-action="zoom-in"]');
    const zoomOutBtn = panel.querySelector('[data-action="zoom-out"]');
    const resetBtn = panel.querySelector('[data-action="reset"]');
    const hint = panel.querySelector(".admin-crop-panel__hint");

    let cropper = null;
    let objectUrl = null;
    let dirty = false;
    let ready = false;
    let cropEnabled = false;
    let previewTimer = null;
    let currentSrc = null;
    let isLocalFile = false;

    function destroyCropper() {
      if (cropper) {
        cropper.destroy();
        cropper = null;
      }
      ready = false;
    }

    function updateResultPreview() {
      if (!cropper || !cropEnabled) return;
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
      if (!ready || !cropEnabled) return;
      dirty = true;
    }

    function setCropControlsVisible(on) {
      zoomInBtn.hidden = !on;
      zoomOutBtn.hidden = !on;
      resetBtn.hidden = !on;
      resultWrap.hidden = !on;
      panel.dataset.cropEnabled = on ? "1" : "0";
      toggleBtn.textContent = on ? "إلغاء الاقتصاص" : "تفعيل الاقتصاص";
      toggleBtn.classList.toggle("admin-img-btn--active", on);
      hint.textContent = on
        ? "اسحب مربع الاقتصاص أو حرّك الصورة. عند الحفظ بتنحفظ النسخة المقصوصة فقط إذا الاقتصاص مفعّل."
        : "الصورة بتنحفظ كاملة. إذا حابب تقتص جزء معيّن، اضغط «تفعيل الاقتصاص».";
    }

    function showPlainPreview(src) {
      destroyCropper();
      empty.hidden = true;
      stageImg.hidden = false;
      stageImg.removeAttribute("hidden");
      stageImg.style.display = "block";
      stageImg.src = src;
      resultImg.hidden = true;
      resultImg.removeAttribute("src");
      setCropControlsVisible(false);
    }

    function startCropper(src) {
      destroyCropper();
      empty.hidden = true;
      stageImg.hidden = false;
      stageImg.removeAttribute("hidden");
      stageImg.style.display = "block";
      stageImg.src = src;

      const onReady = () => {
        if (cropper) return;
        cropper = new window.Cropper(stageImg, {
          aspectRatio: cfg.aspectRatio,
          viewMode: cfg.viewMode,
          dragMode: "move",
          autoCropArea: 0.92,
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

    function setImage(src, local) {
      if (objectUrl && objectUrl !== src) {
        URL.revokeObjectURL(objectUrl);
        objectUrl = null;
      }
      if (local) objectUrl = src;
      currentSrc = src;
      isLocalFile = !!local;
      dirty = false;
      clearBtn.hidden = !local;
      cropEnabled = false;
      showPlainPreview(src);
    }

    function enableCrop() {
      if (!currentSrc) return;
      cropEnabled = true;
      dirty = isLocalFile;
      setCropControlsVisible(true);
      startCropper(currentSrc);
    }

    function disableCrop() {
      cropEnabled = false;
      dirty = false;
      if (!currentSrc) {
        setCropControlsVisible(false);
        return;
      }
      showPlainPreview(currentSrc);
    }

    function resetPanel() {
      destroyCropper();
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
        objectUrl = null;
      }
      currentSrc = null;
      isLocalFile = false;
      cropEnabled = false;
      stageImg.removeAttribute("src");
      stageImg.hidden = true;
      stageImg.style.display = "";
      resultImg.removeAttribute("src");
      resultImg.hidden = true;
      empty.hidden = false;
      empty.textContent = EMPTY_HINT;
      clearBtn.hidden = true;
      dirty = false;
      setCropControlsVisible(false);
    }

    toggleBtn.addEventListener("click", () => {
      if (!currentSrc) return;
      if (cropEnabled) disableCrop();
      else enableCrop();
    });

    zoomInBtn.addEventListener("click", () => {
      if (cropper) cropper.zoom(0.1);
    });
    zoomOutBtn.addEventListener("click", () => {
      if (cropper) cropper.zoom(-0.1);
    });
    resetBtn.addEventListener("click", () => {
      if (cropper) {
        cropper.reset();
        schedulePreview();
        markDirty();
      }
    });
    clearBtn.addEventListener("click", () => {
      input.value = "";
      resetPanel();
      const saved = findSavedImageNear(input);
      if (saved) setImage(saved, false);
    });

    input.addEventListener("change", () => {
      const file = input.files && input.files[0];
      if (!file) {
        resetPanel();
        const saved = findSavedImageNear(input);
        if (saved) setImage(saved, false);
        return;
      }
      if (!file.type.startsWith("image/")) {
        resetPanel();
        empty.textContent = "الملف المختار مش صورة";
        empty.hidden = false;
        return;
      }
      empty.textContent = EMPTY_HINT;
      setImage(URL.createObjectURL(file), true);
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
        return !!(cropper && cropEnabled && dirty && isLocalFile);
      },
      commit() {
        return new Promise((resolve, reject) => {
          if (!cropper || !cropEnabled) {
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

    const saved = findSavedImageNear(input);
    if (saved) setImage(saved, false);

    return panel;
  }

  function stripStalePanel(input) {
    const next = input.nextElementSibling;
    if (next && next.classList.contains("admin-crop-panel") && !next._cropApi) {
      next.remove();
      delete input.dataset.previewBound;
      return true;
    }
    return false;
  }

  function bindFileInput(input) {
    if (!input || input.disabled) return;
    // Never bind Django's empty formset template — clones would break preview
    if (input.closest(".empty-form")) return;

    if (input.dataset.previewBound === "1") {
      // Cloned row may copy the attribute + dead panel HTML without listeners
      if (!stripStalePanel(input)) return;
    }

    input.dataset.previewBound = "1";
    input.setAttribute("accept", "image/*");
    hideDjangoCurrentPreview(input);

    // Remove any leftover panel before attaching a live one
    const next = input.nextElementSibling;
    if (next && next.classList.contains("admin-crop-panel")) next.remove();

    const panel = createCropPanel(input);
    input.insertAdjacentElement("afterend", panel);
  }

  function isImageFileInput(input) {
    const name = (input.name || "").toLowerCase();
    const accept = (input.getAttribute("accept") || "").toLowerCase();
    return (
      name.includes("image") ||
      name.includes("photo") ||
      !accept ||
      accept.includes("image")
    );
  }

  function scan(root) {
    const scope = root || document;
    scope
      .querySelectorAll(".field-photo_preview, .field-image_preview, .field-preview")
      .forEach((el) => {
        el.style.display = "none";
      });

    scope.querySelectorAll('input[type="file"]').forEach((input) => {
      if (isImageFileInput(input)) bindFileInput(input);
    });
  }

  function onFormsetAdded(row) {
    if (!row || !(row instanceof Element)) return;
    // Fresh bind for newly added inline rows
    row.querySelectorAll('input[type="file"]').forEach((input) => {
      delete input.dataset.previewBound;
      const panel = input.nextElementSibling;
      if (panel && panel.classList.contains("admin-crop-panel")) panel.remove();
    });
    scan(row);
  }

  function init() {
    ensureAssets()
      .then(() => {
        scan(document);

        // Django 4.1+ native CustomEvent on the new row
        document.addEventListener("formset:added", (e) => {
          onFormsetAdded(e.target);
        });

        // jQuery fallback (older admin inlines)
        if (window.django && window.django.jQuery) {
          window.django.jQuery(document).on("formset:added", function (_e, $row) {
            const row = $row && $row.get ? $row.get(0) : $row;
            onFormsetAdded(row);
          });
        }

        // Click fallback for "Add another"
        document.addEventListener("click", (e) => {
          if (!e.target.closest(".add-row a, a.add-row, .inline-group .add-row")) return;
          setTimeout(() => {
            document
              .querySelectorAll(".inline-related:not(.empty-form) input[type='file']")
              .forEach((input) => {
                if (!isImageFileInput(input)) return;
                const panel = input.nextElementSibling;
                const deadPanel =
                  panel &&
                  panel.classList.contains("admin-crop-panel") &&
                  !panel._cropApi;
                if (!input.dataset.previewBound || deadPanel) {
                  delete input.dataset.previewBound;
                  if (deadPanel) panel.remove();
                  bindFileInput(input);
                }
              });
          }, 100);
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
