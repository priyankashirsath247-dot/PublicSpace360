// =============================================================================
// PublicSpace360 - Interactive Panvel Digital Geospatial Discovery System
// Google Maps JS API + Leaflet.js / OpenStreetMap Fallback + Marker Clustering
// =============================================================================

document.addEventListener('DOMContentLoaded', function () {
  const mapElement = document.getElementById('gis-map');
  if (!mapElement) return;

  const config = window.PANVEL_MAP_CONFIG || {
    googleMapsApiKey: '',
    defaultCenter: [18.9950, 73.1180],
    defaultZoom: 13
  };

  let allSpaces = [];
  let activeSelectedSpaceId = null;
  let activeTileLayer = 'streets';

  // UI Elements
  const searchInput = document.getElementById('mapSearchInput');
  const clearSearchBtn = document.getElementById('mapClearSearch');
  const areaFilter = document.getElementById('mapAreaFilter');
  const typeFilter = document.getElementById('mapTypeFilter');
  const facilityFilter = document.getElementById('mapFacilityFilter');
  const resetFiltersBtn = document.getElementById('resetFiltersBtn');
  const cardsListContainer = document.getElementById('sidebarCardsList');
  const activeShowcaseContainer = document.getElementById('activeSpaceShowcase');
  const spacesCountBadge = document.getElementById('spacesCountBadge');
  const recenterBtn = document.getElementById('recenterMapBtn');
  const toggleTileBtn = document.getElementById('toggleTileLayerBtn');
  const engineText = document.getElementById('engineNameText');

  // Leaflet Map Initialization
  const map = L.map('gis-map', {
    zoomControl: false,
    maxZoom: 19
  }).setView(config.defaultCenter, config.defaultZoom);

  // Reposition zoom control to top-right below overlay controls
  L.control.zoom({ position: 'bottomright' }).addTo(map);

  // Tile layers
  const osmStreets = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors | Panvel Smart City CEP'
  });

  const esriSatellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 18,
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
  });

  osmStreets.addTo(map);

  // Marker Cluster Group (Requirement 14)
  const markerClusterGroup = L.markerClusterGroup({
    showCoverageOnHover: false,
    maxClusterRadius: 40,
    spiderfyOnMaxZoom: true,
    zoomToBoundsOnClick: true
  });
  map.addLayer(markerClusterGroup);

  // Store marker references by space ID
  const markersById = {};

  // Custom Div Icons for Gardens (Green) and Playgrounds (Blue) (Requirement 1)
  function createMarkerIcon(type, isHighlighted = false) {
    const isGarden = (type || '').toLowerCase().includes('garden');
    const bgClass = isGarden ? 'panvel-marker-garden' : 'panvel-marker-playground';
    const iconClass = isGarden ? 'fa-seedling' : 'fa-child-reaching';
    const highlightClass = isHighlighted ? 'active-highlight' : '';

    return L.divIcon({
      className: 'custom-panvel-icon',
      html: `<div class="panvel-marker-pin ${bgClass} ${highlightClass}"><i class="fa-solid ${iconClass}"></i></div>`,
      iconSize: [40, 40],
      iconAnchor: [20, 40],
      popupAnchor: [0, -38]
    });
  }

  // Format facilities list with checkmarks (Requirement 7 & 15)
  function formatFacilitiesPills(facilitiesStr, maxCount = 4) {
    if (!facilitiesStr) return '';
    const list = facilitiesStr.split(',').map(f => f.trim()).filter(Boolean);
    return list.slice(0, maxCount).map(fac => 
      `<span class="facility-pill"><i class="fa-solid fa-check"></i> ${fac}</span>`
    ).join(' ');
  }

  // Create Rich Marker Popup HTML (Requirement 7)
  function buildPopupHtml(sp) {
    const isGarden = (sp.type || '').toLowerCase().includes('garden');
    const badgeBg = isGarden ? 'bg-success' : 'bg-primary';
    const imgUrl = sp.primary_image || sp.image || 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=600';
    const facilitiesList = (sp.facilities || '').split(',').map(f => f.trim()).filter(Boolean);

    const checklistHtml = facilitiesList.slice(0, 5).map(f => 
      `<div class="small text-dark mb-1"><i class="fa-solid fa-check text-success me-1"></i> ${f}</div>`
    ).join('');

    return `
      <div class="rich-marker-popup">
        <div class="position-relative">
          <img src="${imgUrl}" class="rich-marker-img" alt="${sp.name}">
          <span class="badge ${badgeBg} position-absolute top-0 start-0 m-2 rounded-pill px-2 py-1 shadow-sm">
            <i class="fa-solid ${isGarden ? 'fa-tree' : 'fa-volleyball'} me-1"></i>${sp.type}
          </span>
          <span class="badge bg-dark bg-opacity-75 text-warning position-absolute top-0 end-0 m-2 rounded-pill px-2 py-1 shadow-sm">
            <i class="fa-solid fa-star text-warning"></i> ${sp.rating || '4.2'} / 5
          </span>
        </div>
        <div class="p-3">
          <h6 class="fw-bold text-dark mb-1">${sp.name}</h6>
          <div class="text-muted small mb-2">
            <i class="fa-solid fa-location-dot text-danger me-1"></i>${sp.address || sp.area}
          </div>

          <div class="p-2 rounded-3 bg-light mb-3">
            <div class="text-uppercase text-secondary fw-bold mb-1" style="font-size: 0.68rem; letter-spacing: 0.5px;">Facilities</div>
            <div class="d-flex flex-column">
              ${checklistHtml}
            </div>
          </div>

          <div class="d-flex gap-2">
            <a href="/public-space/${sp.id}" class="btn btn-sm btn-primary w-100 rounded-pill fw-bold py-1">
              View Full Details <i class="fa-solid fa-arrow-right ms-1"></i>
            </a>
            <a href="${sp.google_maps_url || `https://www.google.com/maps/dir/?api=1&destination=${sp.latitude},${sp.longitude}`}" target="_blank" class="btn btn-sm btn-outline-secondary rounded-circle p-2" title="Google Maps Directions">
              <i class="fa-solid fa-diamond-turn-right text-primary"></i>
            </a>
          </div>
        </div>
      </div>
    `;
  }

  // Render Side Panel Preview Card (Requirement 2, 3, 7)
  function renderActiveShowcase(sp) {
    if (!sp) {
      activeShowcaseContainer.style.display = 'none';
      activeShowcaseContainer.innerHTML = '';
      return;
    }

    const isGarden = (sp.type || '').toLowerCase().includes('garden');
    const typeColor = isGarden ? 'text-success' : 'text-primary';
    const typeBadge = isGarden ? 'bg-success' : 'bg-primary';
    const imgUrl = sp.primary_image || sp.image || 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=600';
    const facilitiesHtml = formatFacilitiesPills(sp.facilities, 6);

    activeShowcaseContainer.innerHTML = `
      <div class="active-preview-card">
        <div class="position-relative">
          <img src="${imgUrl}" class="active-preview-img" alt="${sp.name}">
          <div class="position-absolute top-0 start-0 m-2">
            <span class="badge ${typeBadge} rounded-pill px-3 py-1 shadow-sm">
              <i class="fa-solid ${isGarden ? 'fa-leaf' : 'fa-child-reaching'} me-1"></i> ${sp.type}
            </span>
          </div>
          <div class="position-absolute top-0 end-0 m-2">
            <button class="btn btn-sm btn-light rounded-circle shadow-sm p-1" onclick="closeActiveShowcase()" style="width: 28px; height: 28px;">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
        </div>

        <div class="p-3">
          <div class="d-flex justify-content-between align-items-start mb-1">
            <h6 class="fw-bold text-dark m-0 fs-6">${sp.name}</h6>
            <span class="badge bg-warning text-dark fw-bold">
              <i class="fa-solid fa-star"></i> ${sp.rating || '4.2'}/5
            </span>
          </div>

          <div class="small text-muted mb-2">
            <i class="fa-solid fa-location-dot text-danger me-1"></i> <b>${sp.area}</b> &bull; <span class="text-secondary">${sp.address}</span>
          </div>

          <div class="mb-3 d-flex flex-wrap gap-1">
            ${facilitiesHtml}
          </div>

          <div class="d-flex flex-wrap gap-2">
            <a href="/public-space/${sp.id}" class="btn btn-sm btn-primary rounded-pill px-3 fw-bold flex-grow-1">
              <i class="fa-solid fa-circle-info me-1"></i> View Full Details
            </a>
            <a href="${sp.google_maps_url || `https://www.google.com/maps/dir/?api=1&destination=${sp.latitude},${sp.longitude}`}" target="_blank" class="btn btn-sm btn-outline-success rounded-pill px-3 fw-bold">
              <i class="fa-solid fa-diamond-turn-right me-1"></i> Directions
            </a>
            <a href="/survey?space_id=${sp.id}" class="btn btn-sm btn-outline-primary rounded-pill px-2 fw-semibold" title="Take Survey for this space">
              <i class="fa-solid fa-clipboard-check"></i>
            </a>
          </div>
        </div>
      </div>
    `;

    activeShowcaseContainer.style.display = 'block';
  }

  window.closeActiveShowcase = function() {
    activeShowcaseContainer.style.display = 'none';
    activeShowcaseContainer.innerHTML = '';
    activeSelectedSpaceId = null;
    document.querySelectorAll('.space-result-card').forEach(c => c.classList.remove('selected'));
  };

  // Select space, zoom map, highlight marker, and display preview
  function selectPublicSpace(spaceId, panToMap = true) {
    const sp = allSpaces.find(s => s.id === parseInt(spaceId));
    if (!sp) return;

    activeSelectedSpaceId = sp.id;
    renderActiveShowcase(sp);

    // Highlight card in side panel
    document.querySelectorAll('.space-result-card').forEach(card => {
      if (parseInt(card.getAttribute('data-id')) === sp.id) {
        card.classList.add('selected');
        card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      } else {
        card.classList.remove('selected');
      }
    });

    // Move map and open popup
    const marker = markersById[sp.id];
    if (marker && panToMap) {
      // If clustered, uncluster or zoom into marker
      markerClusterGroup.zoomToShowLayer(marker, () => {
        map.flyTo([sp.latitude, sp.longitude], 16, {
          duration: 1.2
        });
        marker.openPopup();
      });

      // Highlight marker icon
      Object.keys(markersById).forEach(id => {
        const m = markersById[id];
        const s = allSpaces.find(x => x.id === parseInt(id));
        if (s) {
          m.setIcon(createMarkerIcon(s.type, parseInt(id) === sp.id));
        }
      });
    }
  }

  // Render cards in sidebar matching Section 15
  function renderSidebarCards(spaces) {
    cardsListContainer.innerHTML = '';

    if (spaces.length === 0) {
      cardsListContainer.innerHTML = `
        <div class="text-center py-5 text-muted">
          <i class="fa-solid fa-filter-circle-xmark fs-2 mb-2 text-secondary"></i>
          <h6 class="fw-bold">No public spaces found</h6>
          <p class="small text-muted mb-3">Try adjusting your area, type, or facility filter.</p>
          <button class="btn btn-sm btn-outline-primary rounded-pill px-3" onclick="document.getElementById('resetFiltersBtn').click()">
            Reset All Filters
          </button>
        </div>
      `;
      return;
    }

    spaces.forEach(sp => {
      const isGarden = (sp.type || '').toLowerCase().includes('garden');
      const typeBadgeClass = isGarden ? 'bg-success' : 'bg-primary';
      const imgUrl = sp.primary_image || sp.image || 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=600';
      const facilitiesHtml = formatFacilitiesPills(sp.facilities, 3);
      const isSelected = activeSelectedSpaceId === sp.id ? 'selected' : '';

      const card = document.createElement('div');
      card.className = `space-result-card ${isSelected}`;
      card.setAttribute('data-id', sp.id);

      card.innerHTML = `
        <div class="position-relative">
          <img src="${imgUrl}" class="space-card-img" alt="${sp.name}" loading="lazy">
          <span class="badge ${typeBadgeClass} position-absolute top-0 start-0 m-2 rounded-pill px-2 py-1 shadow-sm">
            <i class="fa-solid ${isGarden ? 'fa-leaf' : 'fa-child-reaching'} me-1"></i>${sp.type}
          </span>
          <span class="badge bg-dark bg-opacity-75 text-warning position-absolute top-0 end-0 m-2 rounded-pill px-2 py-1 shadow-sm">
            <i class="fa-solid fa-star text-warning"></i> ${sp.rating || '4.2'}
          </span>
        </div>
        
        <div class="p-3">
          <h6 class="fw-bold text-dark mb-1">${sp.name}</h6>
          <div class="small text-muted mb-2">
            <i class="fa-solid fa-location-dot text-danger me-1"></i> <b>${sp.area}</b> &bull; ${sp.address.split(',')[0]}
          </div>

          <div class="d-flex flex-wrap gap-1 mb-3">
            ${facilitiesHtml}
          </div>

          <div class="d-flex justify-content-between align-items-center gap-2 pt-2 border-top">
            <a href="/public-space/${sp.id}" class="btn btn-sm btn-outline-primary rounded-pill px-3 fw-semibold">
              View Details
            </a>
            <button type="button" class="btn btn-sm btn-primary rounded-pill px-3 fw-bold btn-zoom-map">
              <i class="fa-solid fa-map-pin me-1"></i> Map
            </button>
          </div>
        </div>
      `;

      // Card click handlers
      card.addEventListener('click', (e) => {
        if (!e.target.closest('a')) {
          selectPublicSpace(sp.id, true);
        }
      });

      const mapBtn = card.querySelector('.btn-zoom-map');
      if (mapBtn) {
        mapBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          selectPublicSpace(sp.id, true);
        });
      }

      cardsListContainer.appendChild(card);
    });
  }

  // Render Map Markers with Clustering (Requirement 1 & 14)
  function renderMarkers(spaces) {
    markerClusterGroup.clearLayers();
    Object.keys(markersById).forEach(k => delete markersById[k]);

    const bounds = [];

    spaces.forEach(sp => {
      const isHighlighted = activeSelectedSpaceId === sp.id;
      const icon = createMarkerIcon(sp.type, isHighlighted);
      const marker = L.marker([sp.latitude, sp.longitude], { icon: icon });

      // Rich custom popup (Requirement 7)
      marker.bindPopup(buildPopupHtml(sp), {
        maxWidth: 320,
        className: 'panvel-popup-wrapper'
      });

      // Marker click event (Requirement 7)
      marker.on('click', () => {
        selectPublicSpace(sp.id, false);
      });

      markerClusterGroup.addLayer(marker);
      markersById[sp.id] = marker;
      bounds.push([sp.latitude, sp.longitude]);
    });

    // Update count badge
    if (spacesCountBadge) {
      spacesCountBadge.textContent = `${spaces.length} Spaces`;
    }

    // Adjust map bounds if spaces exist and no specific search term zoomed in
    if (bounds.length > 0 && !activeSelectedSpaceId) {
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 });
    }
  }

  // Filter and synchronize Map & Side Panel (Requirement 13)
  function applyFiltersAndSearch() {
    const q = (searchInput ? searchInput.value : '').trim().toLowerCase();
    const selArea = areaFilter ? areaFilter.value : 'All';
    const selType = typeFilter ? typeFilter.value : 'All';
    const selFacility = facilityFilter ? facilityFilter.value : 'All';

    // Show/hide clear search button
    if (clearSearchBtn) {
      clearSearchBtn.style.display = q ? 'block' : 'none';
    }

    const filtered = allSpaces.filter(sp => {
      // Area filter
      if (selArea !== 'All' && sp.area && sp.area.toLowerCase() !== selArea.toLowerCase()) {
        return false;
      }

      // Type filter
      if (selType !== 'All' && sp.type && sp.type.toLowerCase() !== selType.toLowerCase()) {
        return false;
      }

      // Facility filter
      if (selFacility !== 'All') {
        const facs = (sp.facilities || '').toLowerCase();
        if (!facs.includes(selFacility.toLowerCase())) {
          return false;
        }
      }

      // Search input
      if (q) {
        const nameMatch = (sp.name || '').toLowerCase().includes(q);
        const areaMatch = (sp.area || '').toLowerCase().includes(q);
        const addrMatch = (sp.address || '').toLowerCase().includes(q);
        const facMatch = (sp.facilities || '').toLowerCase().includes(q);
        if (!nameMatch && !areaMatch && !addrMatch && !facMatch) {
          return false;
        }
      }

      return true;
    });

    renderMarkers(filtered);
    renderSidebarCards(filtered);

    // If search term matches exact or prominent space, auto zoom to it (Requirement 2)
    if (q && filtered.length > 0) {
      const topMatch = filtered[0];
      selectPublicSpace(topMatch.id, true);
    } else if (filtered.length === 1) {
      selectPublicSpace(filtered[0].id, true);
    } else if (!q && filtered.length > 0 && activeSelectedSpaceId) {
      const stillVisible = filtered.some(s => s.id === activeSelectedSpaceId);
      if (!stillVisible) {
        closeActiveShowcase();
      }
    }
  }

  // Load all public spaces from database API
  fetch('/api/spaces')
    .then(res => res.json())
    .then(data => {
      allSpaces = data;
      applyFiltersAndSearch();

      // Check URL parameters (e.g. ?id=1 or ?q=CIDCO+Garden)
      const urlParams = new URLSearchParams(window.location.search);
      const preId = urlParams.get('id');
      const preQ = urlParams.get('q');
      const preArea = urlParams.get('area');

      if (preQ && searchInput) {
        searchInput.value = preQ;
      }
      if (preArea && areaFilter) {
        areaFilter.value = preArea;
      }

      if (preQ || preArea) {
        applyFiltersAndSearch();
      }

      if (preId) {
        setTimeout(() => selectPublicSpace(parseInt(preId), true), 400);
      }
    })
    .catch(err => {
      console.error("Error fetching Panvel spaces:", err);
      cardsListContainer.innerHTML = `<div class="p-3 text-danger">Failed to load public space data.</div>`;
    });

  // Event Listeners
  if (searchInput) {
    let debounceTimer;
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(applyFiltersAndSearch, 200);
    });
  }

  if (clearSearchBtn) {
    clearSearchBtn.addEventListener('click', () => {
      searchInput.value = '';
      applyFiltersAndSearch();
      searchInput.focus();
    });
  }

  if (areaFilter) {
    areaFilter.addEventListener('change', applyFiltersAndSearch);
  }

  if (typeFilter) {
    typeFilter.addEventListener('change', applyFiltersAndSearch);
  }

  if (facilityFilter) {
    facilityFilter.addEventListener('change', applyFiltersAndSearch);
  }

  if (resetFiltersBtn) {
    resetFiltersBtn.addEventListener('click', () => {
      if (searchInput) searchInput.value = '';
      if (areaFilter) areaFilter.value = 'All';
      if (typeFilter) typeFilter.value = 'All';
      if (facilityFilter) facilityFilter.value = 'All';
      closeActiveShowcase();
      applyFiltersAndSearch();
      map.setView(config.defaultCenter, config.defaultZoom);
    });
  }

  if (recenterBtn) {
    recenterBtn.addEventListener('click', () => {
      map.flyTo(config.defaultCenter, config.defaultZoom, { duration: 1.2 });
    });
  }

  if (toggleTileBtn) {
    toggleTileBtn.addEventListener('click', () => {
      if (activeTileLayer === 'streets') {
        map.removeLayer(osmStreets);
        map.addLayer(esriSatellite);
        activeTileLayer = 'satellite';
        toggleTileBtn.innerHTML = '<i class="fa-solid fa-map me-1 text-success"></i> Streets';
      } else {
        map.removeLayer(esriSatellite);
        map.addLayer(osmStreets);
        activeTileLayer = 'streets';
        toggleTileBtn.innerHTML = '<i class="fa-solid fa-layer-group me-1 text-info"></i> Satellite';
      }
    });
  }
});
