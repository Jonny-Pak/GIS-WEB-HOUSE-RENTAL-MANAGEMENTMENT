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

  L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors &copy; CARTO",
  }).addTo(map);

  const housesDataNode = document.getElementById("houses-data");
  const rawHouses = JSON.parse((housesDataNode && housesDataNode.textContent) || "[]");
  const houses = rawHouses
    .map(normalizeMapHouse)
    .filter(function (house) {
      return house && house.lat != null && house.lng != null;
    });

  const markerGroup = L.featureGroup().addTo(map);
  const drawnItems = new L.FeatureGroup().addTo(map);
  const btnClearPolygon = document.getElementById("btnClearMapPolygon");
  const btnLocateMeOnMap = document.getElementById("btnLocateMeOnMap");
  const btnPinLocation = document.getElementById("btnPinLocation");
  const mapFilterStatus = document.getElementById("mapFilterStatus");
  let userLocationMarker = null;
  let userAccuracyCircle = null;
  let pinMarker = null;
  let pinCircle = null;
  function clearPinMarker() {
    if (pinMarker) {
      map.removeLayer(pinMarker);
      pinMarker = null;
    }
    if (pinCircle) {
      map.removeLayer(pinCircle);
      pinCircle = null;
    }
  }

  function filterHousesByRadius(center, radiusKm) {
    if (!center) return houses;
    const radiusMeters = radiusKm * 1000;
    return houses.filter(function (house) {
      const d = map.distance([house.lat, house.lng], center);
      return d <= radiusMeters;
    });
  }

  function handlePinLocation() {
    map.once('click', function (e) {
      clearPinMarker();
      const latlng = e.latlng;
      // Hiện input bán kính
      const radiusInputWrapper = document.getElementById('radiusInputWrapper');
      const pinRadiusInput = document.getElementById('pinRadiusInput');
      if (radiusInputWrapper) radiusInputWrapper.style.display = 'flex';
      let radiusKm = parseFloat(pinRadiusInput ? pinRadiusInput.value : 20) || 20;
      let lastLatLng = latlng;
      pinMarker = L.marker(latlng, { draggable: true }).addTo(map);
      pinCircle = L.circle(latlng, { radius: radiusKm * 1000, color: '#e74c3c', fillColor: '#e74c3c', fillOpacity: 0.08 }).addTo(map);
      // Lọc nhà trong bán kính
      const filtered = filterHousesByRadius([latlng.lat, latlng.lng], radiusKm);
      renderHouses(filtered, true);
      statusState.filter = `Đã ghim vị trí, lọc ${filtered.length}/${houses.length} nhà trong bán kính ${radiusKm}km.`;
      renderStatus();

      // Khi kéo marker
      pinMarker.on('drag', function (ev) {
        const newLatLng = ev.target.getLatLng();
        lastLatLng = newLatLng;
        pinCircle.setLatLng(newLatLng);
        const filtered2 = filterHousesByRadius([newLatLng.lat, newLatLng.lng], radiusKm);
        renderHouses(filtered2, true);
        statusState.filter = `Đã ghim vị trí, lọc ${filtered2.length}/${houses.length} nhà trong bán kính ${radiusKm}km.`;
        renderStatus();
      });

      // Khi đổi bán kính
      if (pinRadiusInput) {
        pinRadiusInput.oninput = function () {
          radiusKm = parseFloat(pinRadiusInput.value) || 1;
          pinCircle.setRadius(radiusKm * 1000);
          const filtered3 = filterHousesByRadius([lastLatLng.lat, lastLatLng.lng], radiusKm);
          renderHouses(filtered3, true);
          statusState.filter = `Đã ghim vị trí, lọc ${filtered3.length}/${houses.length} nhà trong bán kính ${radiusKm}km.`;
          renderStatus();
        };
      }
    });
    statusState.filter = 'Click lên bản đồ để ghim vị trí, sẽ hiện bán kính tuỳ chỉnh.';
    renderStatus();
  }

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
      circle: false,
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

  map.on(L.Draw.Event.CREATED, function (event) {
    if (event.layerType !== "polygon") {
      return;
    }

    replacePolygonLayer(event.layer);
    applyPolygonFilter();
  });

  map.on(L.Draw.Event.EDITED, function () {
    applyPolygonFilter();
  });

  map.on(L.Draw.Event.DELETED, function () {
    applyPolygonFilter();
  });


  if (btnClearPolygon) {
    btnClearPolygon.addEventListener("click", function () {
      drawnItems.clearLayers();
      clearPinMarker();
      applyPolygonFilter();
    });
  }

  if (btnLocateMeOnMap) {
    btnLocateMeOnMap.addEventListener("click", locateCurrentUser);
  }

  if (btnPinLocation) {
    btnPinLocation.addEventListener("click", function () {
      clearPinMarker();
      handlePinLocation();
    });
  }

  renderHouses(houses, true);
  statusState.filter = "Ve polygon tren ban do de loc nha theo vung. Hien dang hien thi tat ca " + houses.length + " nha.";
  renderStatus();
})();
