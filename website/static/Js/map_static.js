(function () {
  function normalizeMapHouse(house) {
    if (!house) {
      return null;
    }

    if (house.lat != null && house.lng != null) {
      return house;
    }

    if (house.coords && house.coords.lat != null && house.coords.lng != null) {
      return {
        id: house.id,
        name: house.name,
        price: house.price,
        district: house.district,
        status: house.status,
        lat: house.coords.lat,
        lng: house.coords.lng,
        detail_url: house.detail_url,
      };
    }

    return null;
  }

  function getPolygonOuterRing(latLngs) {
    if (!Array.isArray(latLngs) || latLngs.length === 0) {
      return [];
    }

    if (Array.isArray(latLngs[0])) {
      return getPolygonOuterRing(latLngs[0]);
    }

    return latLngs;
  }

  function isPointInsidePolygon(point, polygonRing) {
    if (!Array.isArray(polygonRing) || polygonRing.length < 3) {
      return true;
    }

    const x = Number(point.lng);
    const y = Number(point.lat);
    let inside = false;

    for (let i = 0, j = polygonRing.length - 1; i < polygonRing.length; j = i, i += 1) {
      const xi = Number(polygonRing[i].lng);
      const yi = Number(polygonRing[i].lat);
      const xj = Number(polygonRing[j].lng);
      const yj = Number(polygonRing[j].lat);

      const intersects = ((yi > y) !== (yj > y))
        && (x < ((xj - xi) * (y - yi)) / ((yj - yi) || Number.EPSILON) + xi);

      if (intersects) {
        inside = !inside;
      }
    }

    return inside;
  }

  function updateStatusText(element, text) {
    if (element) {
      element.textContent = text;
    }
  }

  const map = L.map("static-map", {
    zoomControl: true,
    scrollWheelZoom: true,
  }).setView([10.7769, 106.7009], 12);

  let baseLayer = null;
  let switchedToFallbackTiles = false;
  let tileErrorCount = 0;

  function attachFallbackTiles() {
    if (switchedToFallbackTiles) return;
    switchedToFallbackTiles = true;
    if (baseLayer && map.hasLayer(baseLayer)) {
      map.removeLayer(baseLayer);
    }
    baseLayer = L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
      maxZoom: 20,
      subdomains: "abcd",
      attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    }).addTo(map);
  }

  baseLayer = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors',
  });

  baseLayer.on("tileerror", function () {
    tileErrorCount += 1;
    if (tileErrorCount >= 2) {
      attachFallbackTiles();
    }
  });

  baseLayer.addTo(map);

  const mapElement = document.getElementById("static-map");
  const apiUrl = mapElement ? mapElement.dataset.apiUrl : '/api/v1/houses/';

  const housesDataNode = document.getElementById("houses-data");
  const rawHouses = JSON.parse((housesDataNode && housesDataNode.textContent) || "[]");
  let houses = rawHouses
    .map(normalizeMapHouse)
    .filter(function (house) {
      return house && house.lat != null && house.lng != null;
    });

  const markerGroup = L.featureGroup().addTo(map);
  const drawnItems = new L.FeatureGroup().addTo(map);
  const btnClearPolygon = document.getElementById("btnClearMapPolygon");
  const btnLocateMeOnMap = document.getElementById("btnLocateMeOnMap");
  const inputSearchRadius = document.getElementById("inputSearchRadius");
  const btnSearchAddress = document.getElementById("btnSearchAddress");
  const inputAddressSearch = document.getElementById("inputAddressSearch");
  const mapFilterStatus = document.getElementById("mapFilterStatus");
  let userLocationMarker = null;
  let userAccuracyCircle = null;
  let customPinMarker = null;

  const statusState = {
    filter: "",
    location: "",
  };

  function renderStatus() {
    const pieces = [];
    if (statusState.filter) {
      pieces.push(statusState.filter);
    }
    if (statusState.location) {
      pieces.push(statusState.location);
    }
    updateStatusText(mapFilterStatus, pieces.join(" | "));
  }

  const drawControl = new L.Control.Draw({
    position: "topleft",
    draw: {
      polygon: {
        allowIntersection: false,
        showArea: true,
        shapeOptions: {
          color: "#1f7a5a",
          weight: 3,
          fillColor: "#39a57f",
          fillOpacity: 0.18,
        },
      },
      polyline: false,
      rectangle: false,
      circle: {
        shapeOptions: {
          color: "#0d6efd",
          weight: 3,
          fillColor: "#0d6efd",
          fillOpacity: 0.15,
        }
      },
      marker: false,
      circlemarker: false,
    },
    edit: {
      featureGroup: drawnItems,
      edit: true,
      remove: true,
    },
  });
  map.addControl(drawControl);

  function buildPopupHtml(house) {
    return (
      '<div class="map-popup-content">'
      + "<strong>" + (house.name || "Nha cho thue") + "</strong><br>"
      + "Gia: " + (house.price || "Lien he") + "<br>"
      + "Khu vuc: " + (house.district || "Khong ro khu vuc") + "<br>"
      + "Trang thai: " + (house.status || "Chua cap nhat") + "<br>"
      + '<a href="' + (house.detail_url || "#") + '">Xem chi tiet</a>'
      + "</div>"
    );
  }

  function renderHouses(houseList, shouldFitBounds) {
    markerGroup.clearLayers();

    houseList.forEach(function (house) {
      const marker = L.marker([house.lat, house.lng]);
      marker.bindPopup(buildPopupHtml(house));
      marker.addTo(markerGroup);
    });

    const bounds = markerGroup.getBounds();
    if (shouldFitBounds && bounds.isValid()) {
      map.fitBounds(bounds, { padding: [24, 24] });
    }
  }

  function getCurrentPolygonLayer() {
    let polygonLayer = null;
    drawnItems.eachLayer(function (layer) {
      if (!polygonLayer) {
        polygonLayer = layer;
      }
    });
    return polygonLayer;
  }

  function applyPolygonFilter() {
    const polygonLayer = getCurrentPolygonLayer();
    if (!polygonLayer) {
      renderHouses(houses, false);
      statusState.filter =
        "Ve polygon tren ban do de loc nha theo vung. Hien dang hien thi tat ca " + houses.length + " nha.";
      renderStatus();
      return;
    }

    const ring = getPolygonOuterRing(polygonLayer.getLatLngs());
    const filtered = houses.filter(function (house) {
      return isPointInsidePolygon(house, ring);
    });

    renderHouses(filtered, true);
    statusState.filter = "Da loc theo vung: " + filtered.length + "/" + houses.length + " nha nam trong polygon.";
    renderStatus();
  }

  function updateUserLocationLayer(lat, lng, accuracyMeters) {
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
      return;
    }

    const position = [lat, lng];

    if (userLocationMarker) {
      userLocationMarker.setLatLng(position);
    } else {
      userLocationMarker = L.circleMarker(position, {
        radius: 8,
        color: "#0d6efd",
        weight: 2,
        fillColor: "#5aa3ff",
        fillOpacity: 0.9,
      }).addTo(map);
    }

    if (userAccuracyCircle) {
      map.removeLayer(userAccuracyCircle);
    }

    if (Number.isFinite(accuracyMeters) && accuracyMeters > 0) {
      userAccuracyCircle = L.circle(position, {
        radius: accuracyMeters,
        color: "#5aa3ff",
        weight: 1,
        fillColor: "#5aa3ff",
        fillOpacity: 0.12,
      }).addTo(map);
    }

    map.setView(position, Math.max(map.getZoom(), 15));
  }

  function locateCurrentUser() {
    if (!navigator.geolocation) {
      statusState.location = "Trinh duyet khong ho tro dinh vi vi tri hien tai.";
      renderStatus();
      return;
    }

    statusState.location = "Dang lay vi tri hien tai...";
    renderStatus();

    navigator.geolocation.getCurrentPosition(
      function (position) {
        const lat = Number(position.coords.latitude);
        const lng = Number(position.coords.longitude);
        const accuracy = Number(position.coords.accuracy);

        updateUserLocationLayer(lat, lng, accuracy);
        statusState.location =
          "Da lay vi tri cua ban" + (Number.isFinite(accuracy) ? " (sai so ~" + Math.round(accuracy) + "m)." : ".");
        renderStatus();
      },
      function (error) {
        if (error && error.code === 1) {
          statusState.location = "Ban da tu choi quyen vi tri. Hay cap quyen tren trinh duyet va thu lai.";
        } else if (error && error.code === 2) {
          statusState.location = "Khong the xac dinh vi tri hien tai. Vui long thu lai sau.";
        } else {
          statusState.location = "Het thoi gian lay vi tri hien tai. Vui long thu lai.";
        }
        renderStatus();
      },
      {
        enableHighAccuracy: true,
        timeout: 12000,
      }
    );
  }

  function replacePolygonLayer(layer) {
    drawnItems.clearLayers();
    drawnItems.addLayer(layer);
  }

  function setCustomPinAndSearch(lat, lng, radius) {
    const position = [lat, lng];

    // Clear user location when custom pin is dropped
    if (userLocationMarker) map.removeLayer(userLocationMarker);
    if (userAccuracyCircle) map.removeLayer(userAccuracyCircle);
    userLocationMarker = null;
    userAccuracyCircle = null;

    if (customPinMarker) {
      customPinMarker.setLatLng(position);
    } else {
      customPinMarker = L.marker(position).addTo(map);
      customPinMarker.bindPopup("<strong>Vị trí đã ghim</strong>").openPopup();
    }
    map.setView(position, 14);

    const circleLayer = L.circle(position, {
      radius: radius,
      color: "#0d6efd",
      weight: 3,
      fillColor: "#0d6efd",
      fillOpacity: 0.15,
    });
    replacePolygonLayer(circleLayer);
    fetchHousesByRadius(lat, lng, radius);
  }

  function fetchHousesByRadius(lat, lng, radius) {
    statusState.filter = "Đang tải dữ liệu...";
    renderStatus();

    fetch(`${apiUrl}?lat=${lat}&lng=${lng}&radius=${radius / 1000}`)
      .then(response => response.json())
      .then(data => {
        houses = data.map(normalizeMapHouse).filter(h => h != null);
        renderHouses(houses, true);
        statusState.filter = `Tìm thấy ${houses.length} nhà trong bán kính ${Math.round(radius)}m`;
        renderStatus();
      })
      .catch(error => {
        statusState.filter = "Lỗi khi tải dữ liệu từ máy chủ.";
        renderStatus();
        console.error("API error:", error);
      });
  }

  map.on(L.Draw.Event.CREATED, function (event) {
    replacePolygonLayer(event.layer);

    if (event.layerType === "polygon") {
      applyPolygonFilter();
    } else if (event.layerType === "circle") {
      const center = event.layer.getLatLng();
      const radius = event.layer.getRadius();
      fetchHousesByRadius(center.lat, center.lng, radius);
    }
  });

  map.on(L.Draw.Event.EDITED, function () {
    applyPolygonFilter();
  });

  map.on(L.Draw.Event.DELETED, function () {
    applyPolygonFilter();
  });

  map.on('click', function (e) {
    if (!inputSearchRadius) return;
    const radius = parseFloat(inputSearchRadius.value) || 2000;
    setCustomPinAndSearch(e.latlng.lat, e.latlng.lng, radius);
  });

  if (btnClearPolygon) {
    btnClearPolygon.addEventListener("click", function () {
      drawnItems.clearLayers();
      if (customPinMarker) {
        map.removeLayer(customPinMarker);
        customPinMarker = null;
      }
      if (userLocationMarker) {
        map.removeLayer(userLocationMarker);
        map.removeLayer(userAccuracyCircle);
        userLocationMarker = null;
        userAccuracyCircle = null;
      }
      applyPolygonFilter();
    });
  }

  if (btnLocateMeOnMap) {
    btnLocateMeOnMap.addEventListener("click", function () {
      if (customPinMarker) {
        map.removeLayer(customPinMarker);
        customPinMarker = null;
      }
      locateCurrentUser();

      // Attempt search immediately assuming successful locate after a small delay
      setTimeout(() => {
        if (userLocationMarker) {
          const radius = parseFloat(inputSearchRadius.value) || 2000;
          const lat = userLocationMarker.getLatLng().lat;
          const lng = userLocationMarker.getLatLng().lng;

          const circleLayer = L.circle([lat, lng], {
            radius: radius, color: "#0d6efd", weight: 3, fillColor: "#0d6efd", fillOpacity: 0.15
          });
          replacePolygonLayer(circleLayer);
          fetchHousesByRadius(lat, lng, radius);
        }
      }, 3000); // 3 sec is generally enough but it's a rough fallback
    });
  }

  if (inputSearchRadius) {
    inputSearchRadius.addEventListener("change", function () {
      const radius = parseFloat(this.value);
      if (!radius || radius <= 0) return;

      if (customPinMarker) {
        setCustomPinAndSearch(customPinMarker.getLatLng().lat, customPinMarker.getLatLng().lng, radius);
      } else if (userLocationMarker) {
        setCustomPinAndSearch(userLocationMarker.getLatLng().lat, userLocationMarker.getLatLng().lng, radius);
      }
    });
  }

  if (btnSearchAddress && inputAddressSearch) {
    btnSearchAddress.addEventListener('click', function () {
      const q = inputAddressSearch.value.trim();
      if (!q) return;

      statusState.filter = "Đang tìm địa chỉ...";
      renderStatus();

      fetch("https://nominatim.openstreetmap.org/search?format=json&limit=1&q=" + encodeURIComponent(q))
        .then(res => res.json())
        .then(data => {
          if (data && data.length > 0) {
            const lat = parseFloat(data[0].lat);
            const lng = parseFloat(data[0].lon);
            const radius = parseFloat(inputSearchRadius.value) || 2000;
            setCustomPinAndSearch(lat, lng, radius);
            statusState.filter = "Đã tìm thấy địa chỉ.";
          } else {
            alert("Không tìm thấy địa chỉ này.");
            statusState.filter = "Không tìm thấy địa chỉ.";
          }
          renderStatus();
        })
        .catch(err => {
          console.error(err);
          alert("Lỗi khi tìm địa chỉ.");
        });
    });

    inputAddressSearch.addEventListener('keypress', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        btnSearchAddress.click();
      }
    });
  }


  renderHouses(houses, true);
  statusState.filter = "Nhấn vào bản đồ để ghim vị trí hoặc tìm kiếm địa chỉ. Bán kính mặc định là " + inputSearchRadius.value + "m.";
  renderStatus();
})();
