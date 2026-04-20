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

  // detect mobile
  const isMobileDevice = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  const isChromium = window.navigator.userAgent.indexOf('Chrome') > -1 || window.navigator.userAgent.indexOf('Edg') > -1;

  // Chỉ vô hiệu hóa cảm ứng Leaflet trên Desktop Chrome/Edge có màn hình cảm ứng để sửa lỗi double-click.
  // Trên thiết bị di động thực sự (Mobile), chúng ta PHẢI giữ L.Browser.touch = true để bản đồ hoạt động đúng.
  if (!isMobileDevice && isChromium && navigator.maxTouchPoints > 0) {
    L.Browser.touch = false;
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
    referrerPolicy: "strict-origin-when-cross-origin",
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

  // Code _onTouch removed because it broke the Finish button.
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
      + "Trang thai: " + (house.status || "Chua cap nhat") + "<br>"
      + '<a href="' + (house.detail_url || "#") + '" class="d-block mt-1">Xem chi tiet</a>'
      + '<button onclick="window.routeToHouse(' + house.lat + ', ' + house.lng + ')" class="btn btn-sm btn-outline-success mt-2 w-100" style="font-weight: 500;">🚩 Chỉ đường đến đây</button>'
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
      map.fitBounds(bounds, { padding: [24, 24], maxZoom: 16 });
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

    // When filtering by manually drawn polygon, do not force zoom
    renderHouses(filtered, false);
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
        enableHighAccuracy: false,
        timeout: 6000,
        maximumAge: 60000,
      }
    );
  }

  function replacePolygonLayer(layer) {
    drawnItems.clearLayers();
    drawnItems.addLayer(layer);
  }

  function showBottomCard(addressText) {
    const bottomCard = document.getElementById("mapBottomCard");
    const addressEl = document.getElementById("bottomCardAddress");
    if (bottomCard && addressEl) {
      addressEl.textContent = addressText;
      bottomCard.classList.remove("d-none");
    }
  }

  function hideBottomCard() {
    const bottomCard = document.getElementById("mapBottomCard");
    if (bottomCard) {
      bottomCard.classList.add("d-none");
    }
  }

  const btnCloseBottomCard = document.getElementById("btnCloseBottomCard");
  if (btnCloseBottomCard) {
    btnCloseBottomCard.addEventListener("click", hideBottomCard);
  }

  function setCustomPinAndSearch(lat, lng, radius, forceFitBounds = false) {
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
    }

    showBottomCard("Đang tìm địa chỉ...");

    const circleLayer = L.circle(position, {
      radius: radius,
      color: "#0d6efd",
      weight: 3,
      fillColor: "#0d6efd",
      fillOpacity: 0.15,
    });
    replacePolygonLayer(circleLayer);

    if (forceFitBounds) {
      map.fitBounds(circleLayer.getBounds(), { padding: [24, 24] });
    } else {
      map.panTo(position);
    }

    fetchHousesByRadius(lat, lng, radius);

    // Call reverse geocoding to update address
    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1&accept-language=vi`)
      .then(res => res.json())
      .then(data => {
        if (data && data.address) {
          const ad = data.address;
          const parts = [];

          if (ad.house_number && ad.road) parts.push(ad.house_number + " " + ad.road);
          else if (ad.road) parts.push(ad.road);

          if (ad.suburb && ad.suburb.toLowerCase().includes("phường")) parts.push(ad.suburb);
          else if (ad.quarter && ad.quarter.toLowerCase().includes("phường")) parts.push(ad.quarter);
          else if (ad.suburb) parts.push(ad.suburb);
          else if (ad.quarter) parts.push(ad.quarter);
          else if (ad.neighbourhood) parts.push(ad.neighbourhood);

          const uniqueParts = [...new Set(parts)];
          let address = uniqueParts.length > 0 ? uniqueParts.join(", ") : data.display_name;

          showBottomCard(address);
          if (inputAddressSearch) {
            inputAddressSearch.value = address;
          }
        } else if (data && data.display_name) {
          showBottomCard(data.display_name);
          if (inputAddressSearch) {
            inputAddressSearch.value = data.display_name;
          }
        } else {
          showBottomCard("Không xác định được địa chỉ.");
        }
      })
      .catch(err => {
        console.error("Reverse geocoding error:", err);
        showBottomCard("Lỗi khi tìm địa chỉ.");
      });
  }

  function fetchHousesByRadius(lat, lng, radius) {
    statusState.filter = "Đang tải dữ liệu...";
    renderStatus();

    fetch(`${apiUrl}?lat=${lat}&lng=${lng}&radius=${radius / 1000}`)
      .then(response => response.json())
      .then(data => {
        houses = data.map(normalizeMapHouse).filter(h => h != null);
        // Do not force fit bounds to houses! The circle/pan logic handles zoom.
        renderHouses(houses, false);
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

  let isDrawingShape = false;
  map.on(L.Draw.Event.DRAWSTART, function () {
    isDrawingShape = true;
  });
  map.on(L.Draw.Event.DRAWSTOP, function () {
    setTimeout(function () {
      isDrawingShape = false;
    }, 200);
  });

  map.on('click', function (e) {
    if (isDrawingShape) return;
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
      hideBottomCard();
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
            // Force fit bounds when searching by text so it scales right to the circle
            setCustomPinAndSearch(lat, lng, radius, true);
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

  let routingControl = null;

  window.routeToHouse = function (lat, lng) {
    let startLat = null;
    let startLng = null;

    if (customPinMarker) {
      startLat = customPinMarker.getLatLng().lat;
      startLng = customPinMarker.getLatLng().lng;
    } else if (userLocationMarker) {
      startLat = userLocationMarker.getLatLng().lat;
      startLng = userLocationMarker.getLatLng().lng;
    }

    if (!startLat || !startLng) {
      alert("Vui lòng ghim một điểm hoặc bật 'Vị trí của tôi' để làm điểm xuất phát trước khi xem đường đi.");
      return;
    }

    if (!routingControl) {
      routingControl = L.Routing.control({
        waypoints: [],
        routeWhileDragging: false,
        addWaypoints: false,
        fitSelectedRoutes: true,
        showAlternatives: false,
        show: false,
        router: L.Routing.osrmv1({
          serviceUrl: 'https://router.project-osrm.org/route/v1'
        }),
        lineOptions: {
          styles: [{ color: '#198754', opacity: 0.8, weight: 6 }]
        },
        createMarker: function () { return null; }
      }).addTo(map);

      routingControl.on('routingerror', function (err) {
        console.error("Routing error:", err);
        statusState.filter = "Máy chủ tìm đường đang quá tải. Hãy thử lại.";
        renderStatus();
      });

      routingControl.on('routesfound', function (e) {
        if (e.routes && e.routes.length > 0) {
          const summary = e.routes[0].summary;
          let distText = "";
          if (summary.totalDistance < 1000) {
            distText = Math.round(summary.totalDistance) + " m";
          } else {
            distText = (summary.totalDistance / 1000).toFixed(1) + " km";
          }
          const timeText = Math.round(summary.totalTime / 60) + " phút";

          statusState.filter = "Đã tìm đường xong: " + distText + " (khoảng " + timeText + ").";
          renderStatus();
        }
      });
    }

    statusState.filter = "Đang tính toán đường đi...";
    renderStatus();

    routingControl.setWaypoints([
      L.latLng(startLat, startLng),
      L.latLng(lat, lng)
    ]);

    const btnClearRoute = document.getElementById("btnClearMapRoute");
    if (btnClearRoute) btnClearRoute.style.display = 'inline-block';

    // Close the popup nicely
    map.closePopup();
  };

  const btnClearMapRoute = document.getElementById("btnClearMapRoute");
  if (btnClearMapRoute) {
    btnClearMapRoute.addEventListener('click', function () {
      if (routingControl) {
        map.removeControl(routingControl);
        routingControl = null;
      }
      this.style.display = 'none';

      // Auto re-center basically by refreshing filter status bounds if we want, but doing nothing is fine too
      statusState.filter = "Đã tắt chỉ đường.";
      renderStatus();
    });
  }

  renderHouses(houses, true);
  statusState.filter = "Nhấn vào bản đồ để ghim vị trí hoặc tìm kiếm địa chỉ. Bán kính mặc định là " + inputSearchRadius.value + "m.";
  renderStatus();
})();
