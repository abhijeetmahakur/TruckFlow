/**
 * TruckFlow Map Animation Engine
 * Interactive Leaflet simulation inspired by Figma trucks-animation.
 */

class HighwayMapAnimation {
  constructor(mapContainerId) {
    this.containerId = mapContainerId;
    this.map = null;
    this.routeLine = null;
    this.truckMarker = null;
    this.destMarker = null;
    this.originMarker = null;
    
    // Animation state
    this.waypoints = [];
    this.currentIndex = 0;
    this.progress = 0;
    this.isPlaying = true;
    this.speedMultiplier = 1.0;
    this.animFrameId = null;

    // Default corridor: Ranchi -> Chennai
    this.originCity = "Ranchi";
    this.destCity = "Chennai";
    this.totalDistanceKm = 1620;

    this.initMap();
  }

  initMap() {
    const el = document.getElementById(this.containerId);
    if (!el) return;

    // Center on Eastern / South-Eastern India freight corridor
    this.map = L.map(this.containerId, {
      zoomControl: false,
      attributionControl: false
    }).setView([18.5, 83.0], 6);

    // Clean, high-definition Esri World Street Map tiles without watermark or 403 blocks
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19,
      attribution: '&copy; Esri, HERE, Garmin, USGS, NGA'
    }).addTo(this.map);

    // Zoom controls at top right
    L.control.zoom({ position: 'topright' }).addTo(this.map);

    this.loadCorridorWaypoints(this.originCity, this.destCity);
    this.bindControls();
  }

  async loadCorridorWaypoints(origin, dest) {
    try {
      const resp = await fetch(`/api/route-coordinates/?origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(dest)}`);
      const data = await resp.json();
      
      this.waypoints = data.waypoints;
      this.totalDistanceKm = data.distance_km;
      this.renderRoute();
    } catch (err) {
      console.warn("Using fallback local waypoints:", err);
      // Hardcoded high-resolution highway points
      this.waypoints = [
        [23.3441, 85.3096], // Ranchi
        [22.8046, 86.2029], // Jamshedpur
        [22.2850, 86.7350], // Baharagora
        [21.5033, 86.9250], // Balasore
        [20.4625, 85.8830], // Cuttack
        [20.2961, 85.8245], // Bhubaneswar
        [19.3150, 84.7940], // Berhampur
        [17.6868, 83.2185], // Visakhapatnam
        [16.5062, 80.6480], // Vijayawada
        [15.5057, 80.0499], // Ongole
        [14.4426, 79.9865], // Nellore
        [13.0827, 80.2707]  // Chennai
      ];
      this.renderRoute();
    }
  }

  renderRoute() {
    if (!this.waypoints || this.waypoints.length < 2) return;

    // Clear old layers
    if (this.routeLine) this.map.removeLayer(this.routeLine);
    if (this.truckMarker) this.map.removeLayer(this.truckMarker);
    if (this.originMarker) this.map.removeLayer(this.originMarker);
    if (this.destMarker) this.map.removeLayer(this.destMarker);

    // Draw active glowing route polyline
    this.routeLine = L.polyline(this.waypoints, {
      color: '#1665d8',
      weight: 5,
      opacity: 0.85,
      dashArray: '8, 8',
      lineCap: 'round'
    }).addTo(this.map);

    // Origin Pin
    const originPt = this.waypoints[0];
    const originIcon = L.divIcon({
      className: 'origin-map-pin',
      html: `<div style="background:#0f172a; color:#fff; font-size:10px; font-weight:800; padding:3px 8px; border-radius:12px; border:2px solid #fff; box-shadow:0 2px 8px rgba(0,0,0,0.3); white-space:nowrap;">${this.originCity}</div>`,
      iconSize: [60, 24],
      iconAnchor: [30, 12]
    });
    this.originMarker = L.marker(originPt, { icon: originIcon }).addTo(this.map);

    // Destination Pulsing Radar Pin (Figma red pin)
    const destPt = this.waypoints[this.waypoints.length - 1];
    const destIcon = L.divIcon({
      className: 'dest-radar-marker',
      iconSize: [20, 20],
      iconAnchor: [10, 10]
    });
    this.destMarker = L.marker(destPt, { icon: destIcon }).addTo(this.map);

    // Animated Custom Truck Marker
    const truckIcon = L.divIcon({
      className: 'truck-map-marker',
      html: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-5l-3-4h-5v10"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/></svg>`,
      iconSize: [38, 38],
      iconAnchor: [19, 19]
    });
    this.truckMarker = L.marker(originPt, { icon: truckIcon }).addTo(this.map);

    // Fit map bounds with padding
    this.map.fitBounds(this.routeLine.getBounds(), { padding: [40, 40] });

    // Reset and start animation
    this.currentIndex = Math.floor(this.waypoints.length * 0.45); // start midway near Vizag for realistic preview
    this.progress = 0;
    this.startAnimation();
  }

  startAnimation() {
    if (this.animFrameId) cancelAnimationFrame(this.animFrameId);
    this.isPlaying = true;
    this.animateLoop();
  }

  pauseAnimation() {
    this.isPlaying = false;
    if (this.animFrameId) cancelAnimationFrame(this.animFrameId);
  }

  resetAnimation() {
    this.currentIndex = 0;
    this.progress = 0;
    this.startAnimation();
  }

  animateLoop() {
    if (!this.isPlaying) return;

    if (this.currentIndex >= this.waypoints.length - 1) {
      // Loop back smoothly
      this.currentIndex = 0;
      this.progress = 0;
    }

    const p1 = this.waypoints[this.currentIndex];
    const p2 = this.waypoints[this.currentIndex + 1];

    // Linear interpolation between waypoints
    this.progress += 0.008 * this.speedMultiplier;
    if (this.progress >= 1.0) {
      this.progress = 0;
      this.currentIndex++;
    }

    if (p1 && p2) {
      const lat = p1[0] + (p2[0] - p1[0]) * this.progress;
      const lng = p1[1] + (p2[1] - p1[1]) * this.progress;

      if (this.truckMarker) {
        this.truckMarker.setLatLng([lat, lng]);
      }

      // Update Telemetry HUD
      const percentDone = (this.currentIndex + this.progress) / (this.waypoints.length - 1);
      const remainingKm = Math.max(0, Math.round(this.totalDistanceKm * (1 - percentDone)));
      
      const speedEl = document.getElementById('hud-speed');
      const remEl = document.getElementById('hud-remaining');
      const wpEl = document.getElementById('hud-waypoint');
      const tollEl = document.getElementById('hud-toll');

      if (speedEl) speedEl.textContent = `${Math.round(56 + Math.sin(Date.now() / 1500) * 6)} km/h`;
      if (remEl) remEl.textContent = `${remainingKm} km`;
      if (wpEl) {
        if (percentDone < 0.25) wpEl.textContent = "Jamshedpur Outer";
        else if (percentDone < 0.50) wpEl.textContent = "Bhubaneswar NH-16";
        else if (percentDone < 0.75) wpEl.textContent = "Visakhapatnam Bypass";
        else if (percentDone < 0.90) wpEl.textContent = "Nellore Tollway";
        else wpEl.textContent = "Approaching Chennai Hub";
      }
      if (tollEl) {
        const estToll = Math.round((this.totalDistanceKm - remainingKm) * 4.20);
        tollEl.textContent = `₹${estToll.toLocaleString('en-IN')} (FASTag)`;
      }
    }

    this.animFrameId = requestAnimationFrame(() => this.animateLoop());
  }

  bindControls() {
    const btnPlay = document.getElementById('btn-play-animation');
    const btnPause = document.getElementById('btn-pause-animation');
    const btnReset = document.getElementById('btn-reset-animation');
    const btnSpeed = document.getElementById('btn-speed-toggle');

    if (btnPlay) {
      btnPlay.addEventListener('click', () => {
        this.startAnimation();
        btnPlay.classList.add('active');
        if (btnPause) btnPause.classList.remove('active');
      });
    }

    if (btnPause) {
      btnPause.addEventListener('click', () => {
        this.pauseAnimation();
        btnPause.classList.add('active');
        if (btnPlay) btnPlay.classList.remove('active');
      });
    }

    if (btnReset) {
      btnReset.addEventListener('click', () => {
        this.resetAnimation();
        if (btnPlay) btnPlay.classList.add('active');
        if (btnPause) btnPause.classList.remove('active');
      });
    }

    if (btnSpeed) {
      btnSpeed.addEventListener('click', () => {
        if (this.speedMultiplier === 1.0) {
          this.speedMultiplier = 2.5;
          btnSpeed.textContent = "4x";
        } else if (this.speedMultiplier === 2.5) {
          this.speedMultiplier = 5.0;
          btnSpeed.textContent = "8x";
        } else {
          this.speedMultiplier = 1.0;
          btnSpeed.textContent = "2x";
        }
      });
    }
  }

  switchRoute(origin, dest) {
    this.originCity = origin;
    this.destCity = dest;
    const titleEl = document.querySelector('.map-title');
    if (titleEl) {
      titleEl.textContent = `Live Telemetry (${origin} ⇄ ${dest} Corridor)`;
    }
    this.pauseAnimation();
    this.loadCorridorWaypoints(origin, dest);
  }
}

// Global instance
window.HighwayMap = null;
document.addEventListener('DOMContentLoaded', () => {
  window.HighwayMap = new HighwayMapAnimation('highway-map');
});
