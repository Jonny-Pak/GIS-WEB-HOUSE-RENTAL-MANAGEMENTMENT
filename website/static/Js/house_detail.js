(function () {
  const mainImage = document.getElementById("houseMainImage");
  const mainPrev = document.getElementById("houseMainPrev");
  const mainNext = document.getElementById("houseMainNext");
  const galleryStrip = document.getElementById("houseGalleryStrip");
  const galleryPrev = document.getElementById("houseGalleryPrev");
  const galleryNext = document.getElementById("houseGalleryNext");
  const copyOwnerPhoneBtn = document.getElementById("copyOwnerPhoneBtn");
  const galleryItems = Array.from(document.querySelectorAll(".house-gallery-item"));

  function escapeHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  if (copyOwnerPhoneBtn) {
    const originalBtnHtml = copyOwnerPhoneBtn.innerHTML;

    const setCopiedState = function () {
      copyOwnerPhoneBtn.innerHTML = '<span class="icon-check me-2"></span> Da sao chep';
      copyOwnerPhoneBtn.disabled = true;
      window.setTimeout(function () {
        copyOwnerPhoneBtn.innerHTML = originalBtnHtml;
        copyOwnerPhoneBtn.disabled = false;
      }, 1400);
    };

    const copyPhoneFallback = function (value) {
      const helper = document.createElement("textarea");
      helper.value = value;
      helper.setAttribute("readonly", "");
      helper.style.position = "absolute";
      helper.style.left = "-9999px";
      document.body.appendChild(helper);
      helper.select();
      const copied = document.execCommand("copy");
      document.body.removeChild(helper);
      return copied;
    };

    copyOwnerPhoneBtn.addEventListener("click", function () {
      const phoneNumber = (copyOwnerPhoneBtn.dataset.phone || "").trim();
      if (!phoneNumber) return;

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard
          .writeText(phoneNumber)
          .then(setCopiedState)
          .catch(function () {
            if (copyPhoneFallback(phoneNumber)) {
              setCopiedState();
            }
          });
        return;
      }

      if (copyPhoneFallback(phoneNumber)) {
        setCopiedState();
      }
    });
  }

  if (mainImage && galleryItems.length > 0) {
    let currentIndex = 0;

    const setMainImage = function (index) {
      if (!galleryItems[index]) return;

      const item = galleryItems[index];
      mainImage.src = item.dataset.src;
      mainImage.alt = item.dataset.alt || "Gallery image";

      galleryItems.forEach(function (thumb) {
        thumb.classList.remove("active");
      });
      item.classList.add("active");
      item.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });

      currentIndex = index;
    };

    const matchedIndex = galleryItems.findIndex(function (item) {
      return item.dataset.src === mainImage.getAttribute("src");
    });

    setMainImage(matchedIndex >= 0 ? matchedIndex : 0);

    galleryItems.forEach(function (item, index) {
      item.addEventListener("click", function () {
        setMainImage(index);
      });
    });

    if (mainPrev && mainNext && galleryItems.length > 1) {
      mainPrev.addEventListener("click", function () {
        const nextIndex = currentIndex === 0 ? galleryItems.length - 1 : currentIndex - 1;
        setMainImage(nextIndex);
      });

      mainNext.addEventListener("click", function () {
        const nextIndex = currentIndex === galleryItems.length - 1 ? 0 : currentIndex + 1;
        setMainImage(nextIndex);
      });
    } else {
      if (mainPrev) mainPrev.classList.add("is-disabled");
      if (mainNext) mainNext.classList.add("is-disabled");
    }
  } else {
    if (mainPrev) mainPrev.classList.add("is-disabled");
    if (mainNext) mainNext.classList.add("is-disabled");
  }

  if (galleryStrip && galleryPrev && galleryNext) {
    const scrollStep = 320;

    galleryPrev.addEventListener("click", function () {
      galleryStrip.scrollBy({ left: -scrollStep, behavior: "smooth" });
    });

    galleryNext.addEventListener("click", function () {
      galleryStrip.scrollBy({ left: scrollStep, behavior: "smooth" });
    });
  }

  const mapElement = document.getElementById("house-location-map");
  const fallbackElement = document.getElementById("house-location-fallback");
  if (!mapElement) return;

  const lat = Number(mapElement.dataset.lat || "");
  const lng = Number(mapElement.dataset.lng || "");

  if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
    mapElement.classList.add("d-none");
    if (fallbackElement) fallbackElement.classList.remove("d-none");
    return;
  }

  const map = L.map("house-location-map", {
    zoomControl: true,
    scrollWheelZoom: true,
  }).setView([lat, lng], 15);

  L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors &copy; CARTO",
  }).addTo(map);

  const houseName = escapeHtml(mapElement.dataset.name || "Nha cho thue");
  const houseAddress = escapeHtml(mapElement.dataset.address || "");
  const houseDistrict = escapeHtml(mapElement.dataset.district || "");

  const marker = L.marker([lat, lng]).addTo(map);
  marker
    .bindPopup(
      '<div class="map-popup-content"><strong>' +
        houseName +
        "</strong><br>" +
        houseAddress +
        (houseDistrict ? ", " + houseDistrict : "") +
        "</div>"
    )
    .openPopup();
})();
