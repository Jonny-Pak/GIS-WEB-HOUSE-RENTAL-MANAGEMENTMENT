(function () {
  if (window.__postHouseScriptInitialized) {
    return;
  }
  window.__postHouseScriptInitialized = true;

  window.__postHouseGeocodeBound = true;

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return "";
  }

  function previewMainImage(event) {
    const file = event.target.files && event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function () {
      const output = document.getElementById("main-img-preview");
      const box = document.getElementById("main-image-preview-box");
      if (!output || !box) return;
      output.src = reader.result;
      box.style.display = "block";
    };
    reader.readAsDataURL(file);
  }

  function previewGalleryImages(event) {
    const container = document.getElementById("gallery-preview-container");
    const emptyState = document.getElementById("gallery-empty-state");
    if (!container || !emptyState) return;

    const files = event.target.files || [];
    container.innerHTML = "";

    if (!files.length) {
      emptyState.style.display = "block";
      return;
    }

    emptyState.style.display = "none";
    const seen = new Set();
    const uniqueFiles = Array.from(files).filter(function (file) {
      const key = [file.name, file.size, file.lastModified].join("|");
      if (seen.has(key)) {
        return false;
      }
      seen.add(key);
      return true;
    });

    uniqueFiles.forEach(function (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const div = document.createElement("div");
        div.className = "col-4 col-md-2";
        div.innerHTML =
          '<img src="' +
          e.target.result +
          '" class="img-fluid rounded border shadow-sm" style="height: 100px; width: 100%; object-fit: cover;">';
        container.appendChild(div);
      };
      reader.readAsDataURL(file);
    });
  }

  function bindFurnitureQuantityInputs() {
    const checkboxes = document.querySelectorAll(".furniture-checkbox");
    checkboxes.forEach(function (checkbox) {
      const qtyInputId = checkbox.dataset.qtyInput;
      const qtyInput = document.getElementById(qtyInputId);
      if (!qtyInput) return;

      checkbox.addEventListener("change", function () {
        qtyInput.disabled = !this.checked;
        if (this.checked && (!qtyInput.value || Number(qtyInput.value) < 1)) {
          qtyInput.value = 1;
        }
      });
    });
  }

  function initializeMapFeatures() {
    const mapWrapper = document.querySelector(".map-wrapper");
    if (!mapWrapper) return;

    const mapElement = document.getElementById("post-house-map");
    const addressInput = document.getElementById("id_address");
    const latInput = document.getElementById("id_lat");
    const lngInput = document.getElementById("id_lng");
    const latDisplay = document.getElementById("latDisplay");
    const lngDisplay = document.getElementById("lngDisplay");
    const geocodeStatus = document.getElementById("geocodeStatus");
    const btnLocateMe = document.getElementById("btnLocateMe");
    const btnFindAddress = document.getElementById("btnFindAddress");
    const btnClearPin = document.getElementById("btnClearPin");
    const btnClearPolygon = document.getElementById("btnClearPolygon");
    const areaInput = document.getElementById("id_area");
    const allowAreaManualEdit = document.getElementById("allowAreaManualEdit");
    const estimatedAreaInput = document.getElementById("id_estimated_area_m2");
    const polygonGeoInput = document.getElementById("id_polygon_geojson");
    const postForm = mapElement ? mapElement.closest("form") : null;
    const submitErrorBanner = document.getElementById("submitErrorBanner");
    const geocodeUrl = mapWrapper.dataset.geocodeUrl;
    const reverseGeocodeUrl = mapWrapper.dataset.reverseGeocodeUrl;

    if (!mapElement || !addressInput || !latInput || !lngInput || !geocodeUrl) return;
    if (typeof L === "undefined") {
      geocodeStatus.textContent = "Khong the tai ban do tuong tac. Vui long tai lai trang.";
      return;
    }

    const defaultLat = 10.8231;
    const defaultLng = 106.6297;
    const initialLat = parseFloat(mapWrapper.dataset.initialLat || latInput.value);
    const initialLng = parseFloat(mapWrapper.dataset.initialLng || lngInput.value);
    const hasInitialCoords = Number.isFinite(initialLat) && Number.isFinite(initialLng);

    let latestUserLocation = null;
    const map = L.map(mapElement).setView(
      hasInitialCoords ? [initialLat, initialLng] : [defaultLat, defaultLng],
      hasInitialCoords ? 16 : 12
    );

    let baseLayer = null;
    let switchedToFallbackTiles = false;
    let tileErrorCount = 0;

    function attachFallbackTiles() {
      if (switchedToFallbackTiles) return;
      switchedToFallbackTiles = true;

      if (baseLayer && map.hasLayer(baseLayer)) {
        map.removeLayer(baseLayer);
      }

      baseLayer = L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
        maxZoom: 20,
        subdomains: "abcd",
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
      }).addTo(map);

      geocodeStatus.textContent =
        "May chu OpenStreetMap dang chan tile (403). He thong da tu dong chuyen sang tile du phong de ban tiep tuc ghim vi tri.";
    }

    baseLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors',
      referrerPolicy: "strict-origin-when-cross-origin",
    });

    baseLayer.on("tileerror", function () {
      tileErrorCount += 1;
      if (tileErrorCount >= 2) {
        attachFallbackTiles();
      }
    });

    baseLayer.addTo(map);
    let marker = null;
    let polygonLayer = null;
    let polygonGeoJson = null;
    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    // Code _onTouch removed because it broke the Finish button.

    const drawControl = new L.Control.Draw({
      position: "topright",
      draw: {
        polyline: false,
        circle: false,
        circlemarker: false,
        rectangle: false,
        marker: false,
        polygon: {
          allowIntersection: false,
          showArea: true,
          shapeOptions: {
            color: "#181460",
            weight: 3,
            fillOpacity: 0.18,
          },
        },
      },
      edit: {
        featureGroup: drawnItems,
        edit: true,
        remove: true,
      },
    });

    map.addControl(drawControl);

    function updateAreaFromPolygon(layer) {
      if (typeof turf === "undefined") {
        geocodeStatus.textContent = "Khong tai duoc cong cu tinh dien tich. Vui long tai lai trang.";
        return;
      }

      const geoJson = layer.toGeoJSON();
      const area = turf.area(geoJson);
      if (!Number.isFinite(area) || area <= 0) {
        return;
      }

      polygonGeoJson = geoJson;
      if (allowAreaManualEdit) {
        allowAreaManualEdit.disabled = false;
      }

      const manualOverride = Boolean(allowAreaManualEdit && allowAreaManualEdit.checked);
      if (areaInput) {
        areaInput.value = Math.round(area);
        areaInput.readOnly = !manualOverride;
      }
      if (estimatedAreaInput) {
        estimatedAreaInput.value = area.toFixed(2);
      }
      if (polygonGeoInput) {
        polygonGeoInput.value = JSON.stringify(geoJson);
      }

      geocodeStatus.textContent =
        "Da tinh dien tich tu polygon: " + Math.round(area) + " m². Ban co the chinh sua hinh neu can.";
    }

    function clearPolygon() {
      if (polygonLayer) {
        drawnItems.removeLayer(polygonLayer);
        polygonLayer = null;
      }
      polygonGeoJson = null;
      if (areaInput) {
        areaInput.readOnly = false;
      }
      if (allowAreaManualEdit) {
        allowAreaManualEdit.checked = false;
        allowAreaManualEdit.disabled = true;
      }
      if (estimatedAreaInput) {
        estimatedAreaInput.value = "";
      }
      if (polygonGeoInput) {
        polygonGeoInput.value = "";
      }
      geocodeStatus.textContent = "Da xoa polygon.";
    }

    function clearSubmitError() {
      if (!submitErrorBanner) return;
      submitErrorBanner.textContent = "";
      submitErrorBanner.classList.add("d-none");
    }

    function showSubmitError(message) {
      if (submitErrorBanner) {
        submitErrorBanner.textContent = message;
        submitErrorBanner.classList.remove("d-none");
        submitErrorBanner.scrollIntoView({ behavior: "smooth", block: "center" });
      }
      geocodeStatus.textContent = message;
    }

    function persistPolygonFromLayerIfNeeded() {
      if (!polygonLayer || typeof turf === "undefined") {
        return false;
      }

      const geoJson = polygonLayer.toGeoJSON();
      const area = turf.area(geoJson);
      if (!Number.isFinite(area) || area <= 0) {
        return false;
      }

      polygonGeoJson = geoJson;
      if (polygonGeoInput) {
        polygonGeoInput.value = JSON.stringify(geoJson);
      }
      if (estimatedAreaInput) {
        estimatedAreaInput.value = area.toFixed(2);
      }
      if (areaInput && (!areaInput.value || Number(areaInput.value) <= 0)) {
        areaInput.value = Math.round(area);
      }
      return true;
    }

    function updateCoordinateUI(lat, lng, message, doNotPanMap) {
      latInput.value = lat.toFixed(6);
      lngInput.value = lng.toFixed(6);
      latDisplay.textContent = lat.toFixed(6);
      lngDisplay.textContent = lng.toFixed(6);

      if (marker) {
        marker.setLatLng([lat, lng]);
      } else {
        marker = L.marker([lat, lng]).addTo(map);
      }

      if (!doNotPanMap) {
        map.setView([lat, lng], Math.max(map.getZoom(), 16));
      }
      if (message) {
        geocodeStatus.textContent = message;
      }
    }

    function setCoordinate(lat, lng, message, doNotPanMap) {
      updateCoordinateUI(lat, lng, message, doNotPanMap);
    }

    function reverseGeocode(lat, lng) {
      if (!reverseGeocodeUrl) return;
      geocodeStatus.textContent = "Đang lấy địa chỉ từ tọa độ...";
      
      const formData = new FormData();
      formData.append("lat", lat);
      formData.append("lng", lng);

      fetch(reverseGeocodeUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "X-Requested-With": "XMLHttpRequest",
        },
        body: formData,
      })
      .then(response => response.json())
      .then(data => {
        if (data.success && data.address) {
          addressInput.value = data.address;
          geocodeStatus.textContent = "Đã tự động điền địa chỉ vào ô bên trên từ vị trí bạn vừa ghim.";
        } else {
          geocodeStatus.textContent = "Đã ghim vị trí, nhưng không thể tìm thấy tên đường chính xác tự động.";
        }
      })
      .catch(() => {
        geocodeStatus.textContent = "Đã ghim vị trí thành công (có lỗi khi tìm tên đường).";
      });
    }

    if (hasInitialCoords) {
      setCoordinate(initialLat, initialLng, "Da nap toa do hien co cua tin dang.");
    }

    let isDrawingShape = false;
    map.on(L.Draw.Event.DRAWSTART, function () {
      isDrawingShape = true;
    });
    map.on(L.Draw.Event.DRAWSTOP, function () {
      setTimeout(function() {
        isDrawingShape = false;
      }, 200);
    });

    map.on("click", function (event) {
      if (isDrawingShape) return;
      const lat = Number(event.latlng.lat);
      const lng = Number(event.latlng.lng);
      setCoordinate(lat, lng, "Đã ghim vị trí. Hệ thống đang dò tìm địa chỉ...", true);
      reverseGeocode(lat, lng);
    });

    map.on(L.Draw.Event.CREATED, function (event) {
      if (event.layerType !== "polygon") {
        return;
      }

      if (polygonLayer) {
        drawnItems.removeLayer(polygonLayer);
      }

      polygonLayer = event.layer;
      drawnItems.addLayer(polygonLayer);
      updateAreaFromPolygon(polygonLayer);

      // Tự động ghim pin tại trung tâm polygon
      var center = polygonLayer.getBounds().getCenter();
      setCoordinate(center.lat, center.lng, "Đã tính diện tích và ghim vị trí tại trung tâm vùng đất.", true);
      reverseGeocode(center.lat, center.lng);
    });

    map.on(L.Draw.Event.EDITED, function (event) {
      event.layers.eachLayer(function (layer) {
        if (layer === polygonLayer) {
          updateAreaFromPolygon(layer);
          // Cập nhật lại pin khi chỉnh polygon
          var center = layer.getBounds().getCenter();
          setCoordinate(center.lat, center.lng, "Đã cập nhật diện tích và vị trí ghim theo polygon mới.", true);
        }
      });
    });

    map.on(L.Draw.Event.DELETED, function () {
      polygonLayer = null;
      polygonGeoJson = null;
      if (areaInput) {
        areaInput.readOnly = false;
      }
      if (allowAreaManualEdit) {
        allowAreaManualEdit.checked = false;
        allowAreaManualEdit.disabled = true;
      }
      if (estimatedAreaInput) {
        estimatedAreaInput.value = "";
      }
      if (polygonGeoInput) {
        polygonGeoInput.value = "";
      }
      geocodeStatus.textContent = "Da xoa polygon va xoa gia tri dien tich.";
    });

    function requestUserLocation() {
      if (!navigator.geolocation) {
        geocodeStatus.textContent = "Trinh duyet khong ho tro dinh vi.";
        return;
      }

      geocodeStatus.textContent = "Dang lay vi tri hien tai...";
      navigator.geolocation.getCurrentPosition(
        function (position) {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          latestUserLocation = { lat: lat, lng: lng };
          setCoordinate(lat, lng, "Đã lấy vị trí hiện tại. Đang dò tìm địa chỉ...");
          reverseGeocode(lat, lng);
        },
        function (error) {
          if (error && error.code === 1) {
            geocodeStatus.textContent = "Ban da tu choi quyen vi tri. Hay bam vao bieu tuong khoa/cai dat tren trinh duyet de cho phep vi tri cho 127.0.0.1.";
          } else if (error && error.code === 2) {
            geocodeStatus.textContent = "Khong the xac dinh vi tri hien tai. Hay thu lai khi ket noi mang on dinh hon.";
          } else {
            geocodeStatus.textContent = "Lay vi tri hien tai bi het thoi gian. Hay thu lai hoac chon tim theo dia chi.";
          }
        },
        { enableHighAccuracy: true, timeout: 10000 }
      );
    }

    function geocodeAddress() {
      const address = (addressInput.value || "").trim();

      if (!address) {
        geocodeStatus.textContent = "Vui lòng nhập địa chỉ để tìm tọa độ.";
        geocodeStatus.className = "text-danger mt-1 small d-inline-block fw-bold";
        return;
      }

      geocodeStatus.textContent = "Đang tìm tọa độ...";
      geocodeStatus.className = "text-primary mt-1 small d-inline-block fw-bold";
      
      const formData = new FormData();
      formData.append("address", address);
      if (latestUserLocation) {
        formData.append("user_lat", String(latestUserLocation.lat));
        formData.append("user_lng", String(latestUserLocation.lng));
      }

      fetch(geocodeUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "X-Requested-With": "XMLHttpRequest",
        },
        body: formData,
      })
        .then(function (response) {
          return response.json();
        })
        .then(function (data) {
          if (!data.success || !Number.isFinite(data.lat) || !Number.isFinite(data.lng)) {
            if (
              Number.isFinite(data.approximate_lat) &&
              Number.isFinite(data.approximate_lng)
            ) {
              map.setView([Number(data.approximate_lat), Number(data.approximate_lng)], 14);
            }
            geocodeStatus.textContent = data.message || "Khong the tim toa do tu dia chi.";
            return;
          }

          let sourceMessage = "Da lay toa do tu dia chi thanh cong.";
          if (data.source === "user_location_fallback") {
            sourceMessage = "Khong tim thay dia chi chinh xac, da dung vi tri hien tai cua ban.";
          } else if (data.source === "district_center_fallback" || data.source === "district_center_fallback_rate_limited") {
            sourceMessage = "Khong tim thay dia chi chinh xac, da tam thoi dung tam quan/huyen da chon.";
          } else if (data.source === "parsed_from_input") {
            sourceMessage = "Da doc truc tiep toa do tu noi dung ban vua nhap.";
          } else if (data.source === "cached") {
            sourceMessage = "Da su dung toa do da luu tru cho dia chi nay.";
          }
          setCoordinate(data.lat, data.lng, sourceMessage);
        })
        .catch(function () {
          geocodeStatus.textContent = "Co loi khi tim toa do. Vui long thu lai.";
        });
    }

    if (btnLocateMe) {
      btnLocateMe.addEventListener("click", requestUserLocation);
    }

    if (btnFindAddress) {
      btnFindAddress.addEventListener("click", geocodeAddress);
    }

    if (btnClearPin) {
      btnClearPin.addEventListener("click", function () {
        latInput.value = "";
        lngInput.value = "";
        latDisplay.textContent = "--";
        lngDisplay.textContent = "--";
        if (marker) {
          map.removeLayer(marker);
          marker = null;
        }
        geocodeStatus.textContent = "Da bo ghim thu cong.";
      });
    }

    if (btnClearPolygon) {
      btnClearPolygon.addEventListener("click", function () {
        clearPolygon();
      });
    }

    // Avoid aggressive geocoding while user is typing, as OSM/Nominatim may rate-limit.
    addressInput.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        geocodeAddress();
      }
    });

    if (areaInput) {
      areaInput.readOnly = false;
    }

    if (allowAreaManualEdit && areaInput) {
      allowAreaManualEdit.addEventListener("change", function () {
        const canEdit = Boolean(this.checked && polygonGeoJson);
        areaInput.readOnly = !canEdit;

        if (!canEdit && estimatedAreaInput && Number.isFinite(Number(estimatedAreaInput.value))) {
          areaInput.value = Math.round(Number(estimatedAreaInput.value));
        }
      });
    }

    if (postForm) {
      postForm.addEventListener("submit", function (event) {
        clearSubmitError();
        persistPolygonFromLayerIfNeeded();

        if (!estimatedAreaInput || !polygonGeoInput) {
          return;
        }

        const estimated = Number(estimatedAreaInput.value || "");
        const enteredArea = Number(areaInput && areaInput.value ? areaInput.value : "");
        const hasPolygon = Boolean((polygonGeoInput.value || "").trim());

        if (!Number.isFinite(enteredArea) || enteredArea <= 0) {
          event.preventDefault();
          showSubmitError("Dien tich khong hop le. Vui long kiem tra lai.");
          return;
        }

        if (hasPolygon) {
          if (!Number.isFinite(estimated) || estimated <= 0) {
            event.preventDefault();
            showSubmitError("Khong doc duoc dien tich tu polygon. Vui long ve lai polygon.");
            return;
          }

          const tolerance = Math.max(5, estimated * 0.1);
          if (Math.abs(enteredArea - estimated) > tolerance) {
            event.preventDefault();
            showSubmitError(
              "Dien tich nhap tay vuot nguong cho phep so voi polygon (toi da ±" +
              tolerance.toFixed(1) +
              " m²)."
            );
          }
        }
      });
    }

    const existingArea = parseFloat(areaInput && areaInput.value ? areaInput.value : '');
    if (Number.isFinite(existingArea) && existingArea > 0) {
      geocodeStatus.textContent = "Gia tri dien tich hien co: " + Math.round(existingArea) + " m². Ban co the ve polygon de cap nhat.";
    }
  }

  function previewMainImage(event) {
    const input = event.target;
    const previewBox = document.getElementById("main-image-preview-box");
    const previewImg = document.getElementById("main-img-preview");
    
    if (input.files && input.files[0]) {
      const reader = new FileReader();
      reader.onload = function(e) {
        previewImg.src = e.target.result;
        previewBox.classList.remove("d-none");
      };
      reader.readAsDataURL(input.files[0]);
    } else {
      previewImg.src = "#";
      previewBox.classList.add("d-none");
    }
  }

  function previewGalleryImages(event) {
    const input = event.target;
    const container = document.getElementById("gallery-preview-container");
    const emptyState = document.getElementById("gallery-empty-state");
    
    // Create the container if it doesn't exist
    let gridContainer = container;
    if (!gridContainer) {
      gridContainer = document.createElement("div");
      gridContainer.id = "gallery-preview-container";
      gridContainer.className = "row g-2 mt-0";
      emptyState.parentNode.appendChild(gridContainer);
    }
    
    gridContainer.innerHTML = "";
    
    if (input.files && input.files.length > 0) {
      emptyState.classList.add("d-none");
      gridContainer.classList.remove("d-none");
      
      Array.from(input.files).forEach(file => {
        if (!file.type.startsWith('image/')) return;
        
        const reader = new FileReader();
        reader.onload = function(e) {
          const col = document.createElement("div");
          col.className = "col-4 col-md-3";
          col.innerHTML = `
            <div class="position-relative ratio ratio-1x1 border rounded overflow-hidden shadow-sm">
              <img src="${e.target.result}" class="object-fit-cover w-100 h-100" alt="Detail preview">
            </div>
          `;
          gridContainer.appendChild(col);
        };
        reader.readAsDataURL(file);
      });
    } else {
      emptyState.classList.remove("d-none");
      gridContainer.classList.add("d-none");
    }
  }

  const mainImageInput = document.getElementById("mainImageInput");
  if (mainImageInput) {
    mainImageInput.onchange = previewMainImage;
  }

  const detailImagesInput = document.getElementById("detailImagesInput");
  if (detailImagesInput) {
    detailImagesInput.onchange = previewGalleryImages;
  }

  bindFurnitureQuantityInputs();
  initializeMapFeatures();
})();
