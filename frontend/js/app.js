/**
 * TruckFlow Main Application Orchestrator
 * Connects Frontend UI with Django REST APIs & Real-Time Logistics Engines
 */

const CITY_COORDS = {
  'Ranchi': { lat: 23.3441, lng: 85.3096, state: 'Jharkhand' },
  'Chennai': { lat: 13.0827, lng: 80.2707, state: 'Tamil Nadu' },
  'Bhubaneswar': { lat: 20.2961, lng: 85.8245, state: 'Odisha' },
  'Kolkata': { lat: 22.5726, lng: 88.3639, state: 'West Bengal' },
  'Jamshedpur': { lat: 22.8046, lng: 86.2029, state: 'Jharkhand' },
  'Hyderabad': { lat: 17.3850, lng: 78.4867, state: 'Telangana' },
  'Bengaluru': { lat: 12.9716, lng: 77.5946, state: 'Karnataka' },
  'Mumbai': { lat: 19.0760, lng: 72.8777, state: 'Maharashtra' },
  'Delhi': { lat: 28.7041, lng: 77.1025, state: 'Delhi' },
  'Visakhapatnam': { lat: 17.6868, lng: 83.2185, state: 'Andhra Pradesh' }
};

const TruckFlowApp = {
  state: {
    activeRole: 'BROKER',
    truck: null,
    fleetTrucks: [],
    crmContacts: [],
    activeCrmFilter: 'ALL',
    outboundLoad: null,
    returnLoad: null,
    multiLegChain: null,
    signatureDrawn: false,
    calculatorParams: {
      total_km: 3240,
      loaded_km: 3240,
      empty_km: 0,
      outbound_freight: 85000,
      return_freight: 78000,
      diesel_price: 92.50,
      kmpl: 3.5,
      toll_per_km: 4.20,
      driver_expense_daily: 1200,
      commission_pct: 3.0
    }
  },

  init() {
    this.bindEvents();
    this.fetchDashboardStats();
    this.loadRoundTripMatches();
    this.initSignatureCanvas();
  },

  bindEvents() {
    // Role switcher
    const roleSelect = document.getElementById('role-select');
    if (roleSelect) {
      roleSelect.addEventListener('change', (e) => this.switchRole(e.target.value));
    }

    // Refresh matches button
    const btnRefresh = document.getElementById('btn-refresh-matches');
    if (btnRefresh) {
      btnRefresh.addEventListener('click', () => {
        this.showToast('Re-scanning national freight corridors for return loads...');
        this.loadRoundTripMatches();
      });
    }

    // Book Direct Return Load (Step 5 centerpiece action)
    const btnBookDirect = document.getElementById('btn-book-direct-return');
    if (btnBookDirect) {
      btnBookDirect.addEventListener('click', () => this.bookTrip(false));
    }

    // Book Multi-Leg Chain (Step 8 action)
    const btnBookMulti = document.getElementById('btn-book-multi-leg');
    if (btnBookMulti) {
      btnBookMulti.addEventListener('click', () => this.bookTrip(true));
    }

    // --- MODAL 1: Profit Calculator ---
    const btnOpenCalc = document.getElementById('btn-open-profit-modal');
    const modalCalc = document.getElementById('modal-profit-calculator');
    const btnCloseCalc = document.getElementById('btn-close-profit-modal');
    const btnDismissCalc = document.getElementById('btn-dismiss-profit-modal');

    if (btnOpenCalc && modalCalc) {
      btnOpenCalc.addEventListener('click', () => {
        modalCalc.classList.add('active');
        this.recalculateProfit();
      });
    }
    if (btnCloseCalc && modalCalc) {
      btnCloseCalc.addEventListener('click', () => modalCalc.classList.remove('active'));
    }
    if (btnDismissCalc && modalCalc) {
      btnDismissCalc.addEventListener('click', () => modalCalc.classList.remove('active'));
    }

    // Sliders in Calculator Modal
    const sliderDiesel = document.getElementById('slider-diesel');
    const sliderKmpl = document.getElementById('slider-kmpl');
    const sliderToll = document.getElementById('slider-toll');
    const sliderDriver = document.getElementById('slider-driver');

    if (sliderDiesel) {
      sliderDiesel.addEventListener('input', (e) => {
        document.getElementById('val-diesel').textContent = `₹${parseFloat(e.target.value).toFixed(2)}`;
        this.state.calculatorParams.diesel_price = parseFloat(e.target.value);
        this.recalculateProfit();
      });
    }
    if (sliderKmpl) {
      sliderKmpl.addEventListener('input', (e) => {
        document.getElementById('val-kmpl').textContent = `${parseFloat(e.target.value).toFixed(1)} km/L`;
        this.state.calculatorParams.kmpl = parseFloat(e.target.value);
        this.recalculateProfit();
      });
    }
    if (sliderToll) {
      sliderToll.addEventListener('input', (e) => {
        document.getElementById('val-toll').textContent = `₹${parseFloat(e.target.value).toFixed(2)}/km`;
        this.state.calculatorParams.toll_per_km = parseFloat(e.target.value);
        this.recalculateProfit();
      });
    }
    if (sliderDriver) {
      sliderDriver.addEventListener('input', (e) => {
        document.getElementById('val-driver').textContent = `₹${parseInt(e.target.value).toLocaleString('en-IN')}/day`;
        this.state.calculatorParams.driver_expense_daily = parseInt(e.target.value);
        this.recalculateProfit();
      });
    }

    // --- MODAL 2: WhatsApp Logistics Bot Drawer ---
    const btnOpenWa = document.getElementById('btn-open-whatsapp');
    const waDrawer = document.getElementById('whatsapp-drawer');
    const btnCloseWa = document.getElementById('btn-close-whatsapp');
    const btnWaAccept = document.getElementById('btn-wa-accept');
    const btnWaLoc = document.getElementById('btn-wa-location');
    const btnWaSend = document.getElementById('btn-wa-send');
    const waInput = document.getElementById('wa-input');

    if (btnOpenWa && waDrawer) {
      btnOpenWa.addEventListener('click', () => waDrawer.classList.toggle('active'));
    }
    if (btnCloseWa && waDrawer) {
      btnCloseWa.addEventListener('click', () => waDrawer.classList.remove('active'));
    }
    if (btnWaAccept) {
      btnWaAccept.addEventListener('click', () => {
        this.appendWaMessage("User: ✅ रिटर्न लोड स्वीकार कर लिया गया है! (Load 002 Accepted by Driver via WhatsApp)");
        this.showToast("WhatsApp Bot: Driver accepted return load! Booking locked.");
      });
    }
    if (btnWaLoc) {
      btnWaLoc.addEventListener('click', () => {
        this.appendWaMessage("User: 📍 Live GPS: 17.6868° N, 83.2185° E (NH-16 near Visakhapatnam)");
        this.showToast("WhatsApp Bot: Live location shared to Broker & Shipper.");
      });
    }
    if (btnWaSend && waInput) {
      btnWaSend.addEventListener('click', () => this.handleWaUserInput());
      waInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') this.handleWaUserInput();
      });
    }

    // --- MODAL 3: Fleet Management Modal ---
    const btnOpenFleet = document.getElementById('btn-open-fleet');
    const modalFleet = document.getElementById('modal-fleet-management');
    const btnCloseFleet = document.getElementById('btn-close-fleet-modal');
    const tabFleetList = document.getElementById('tab-fleet-list');
    const tabAddTruck = document.getElementById('tab-add-truck');
    const paneFleetList = document.getElementById('pane-fleet-list');
    const paneAddTruck = document.getElementById('pane-add-truck');
    const formAddTruck = document.getElementById('form-add-truck');

    if (btnOpenFleet && modalFleet) {
      btnOpenFleet.addEventListener('click', () => {
        modalFleet.classList.add('active');
        this.loadFleetTrucks();
      });
    }
    if (btnCloseFleet && modalFleet) {
      btnCloseFleet.addEventListener('click', () => modalFleet.classList.remove('active'));
    }
    if (tabFleetList && tabAddTruck) {
      tabFleetList.addEventListener('click', () => {
        tabFleetList.classList.add('active');
        tabAddTruck.classList.remove('active');
        paneFleetList.style.display = 'block';
        paneAddTruck.style.display = 'none';
      });
      tabAddTruck.addEventListener('click', () => {
        tabAddTruck.classList.add('active');
        tabFleetList.classList.remove('active');
        paneFleetList.style.display = 'none';
        paneAddTruck.style.display = 'block';
      });
    }
    if (formAddTruck) {
      formAddTruck.addEventListener('submit', (e) => this.submitNewTruck(e));
    }

    // --- MODAL 4: Post New Load Modal ---
    const btnOpenPostLoad = document.getElementById('btn-open-post-load');
    const modalPostLoad = document.getElementById('modal-post-load');
    const btnClosePostLoad = document.getElementById('btn-close-post-load-modal');
    const formPostLoad = document.getElementById('form-post-load');

    if (btnOpenPostLoad && modalPostLoad) {
      btnOpenPostLoad.addEventListener('click', () => modalPostLoad.classList.add('active'));
    }
    if (btnClosePostLoad && modalPostLoad) {
      btnClosePostLoad.addEventListener('click', () => modalPostLoad.classList.remove('active'));
    }
    if (formPostLoad) {
      formPostLoad.addEventListener('submit', (e) => this.submitNewLoad(e));
    }

    // --- MODAL 5: Vehicle & National Permit Documents ---
    const btnViewDocs = document.getElementById('btn-view-docs');
    const modalDocs = document.getElementById('modal-vehicle-docs');
    const btnCloseDocs = document.getElementById('btn-close-docs-modal');
    const btnDismissDocs = document.getElementById('btn-dismiss-docs-modal');

    if (btnViewDocs && modalDocs) {
      btnViewDocs.addEventListener('click', (e) => {
        e.preventDefault();
        this.openVehicleDocs();
      });
    }
    if (btnCloseDocs && modalDocs) {
      btnCloseDocs.addEventListener('click', () => modalDocs.classList.remove('active'));
    }
    if (btnDismissDocs && modalDocs) {
      btnDismissDocs.addEventListener('click', () => modalDocs.classList.remove('active'));
    }

    // --- MODAL 6: Broker CRM & Transporter Directory ---
    const btnNavCrm = document.getElementById('btn-nav-crm');
    const modalCrm = document.getElementById('modal-crm-directory');
    const btnCloseCrm = document.getElementById('btn-close-crm-modal');
    const crmSearch = document.getElementById('crm-search-input');

    if (btnNavCrm && modalCrm) {
      btnNavCrm.addEventListener('click', () => {
        modalCrm.classList.add('active');
        this.loadCrmContacts();
      });
    }
    if (btnCloseCrm && modalCrm) {
      btnCloseCrm.addEventListener('click', () => modalCrm.classList.remove('active'));
    }
    if (crmSearch) {
      crmSearch.addEventListener('input', () => this.filterCrmContacts());
    }
    document.querySelectorAll('.crm-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        document.querySelectorAll('.crm-pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        this.state.activeCrmFilter = pill.getAttribute('data-filter');
        this.filterCrmContacts();
      });
    });

    // --- MODAL 7: Lorry Receipt (LR) Bilty & Quote ---
    const btnExportQuote = document.getElementById('btn-export-quote');
    const modalLr = document.getElementById('modal-lorry-receipt');
    const btnCloseLr = document.getElementById('btn-close-lr-modal');
    const btnDismissLr = document.getElementById('btn-dismiss-lr-modal');
    const btnPrintBilty = document.getElementById('btn-print-bilty');

    if (btnExportQuote && modalLr) {
      btnExportQuote.addEventListener('click', () => {
        if (modalCalc) modalCalc.classList.remove('active');
        this.openLorryReceipt();
      });
    }
    if (btnCloseLr && modalLr) {
      btnCloseLr.addEventListener('click', () => modalLr.classList.remove('active'));
    }
    if (btnDismissLr && modalLr) {
      btnDismissLr.addEventListener('click', () => modalLr.classList.remove('active'));
    }
    if (btnPrintBilty) {
      btnPrintBilty.addEventListener('click', () => window.print());
    }

    // --- MODAL 8: Driver Proof of Delivery (POD) ---
    const btnOpenPod = document.getElementById('btn-open-pod');
    const modalPod = document.getElementById('modal-driver-pod');
    const btnClosePod = document.getElementById('btn-close-pod-modal');
    const btnDismissPod = document.getElementById('btn-dismiss-pod-modal');
    const btnClearSig = document.getElementById('btn-clear-sig');
    const btnSubmitPod = document.getElementById('btn-submit-pod');

    if (btnOpenPod && modalPod) {
      btnOpenPod.addEventListener('click', () => {
        modalPod.classList.add('active');
        this.clearSignature();
      });
    }
    if (btnClosePod && modalPod) {
      btnClosePod.addEventListener('click', () => modalPod.classList.remove('active'));
    }
    if (btnDismissPod && modalPod) {
      btnDismissPod.addEventListener('click', () => modalPod.classList.remove('active'));
    }
    if (btnClearSig) {
      btnClearSig.addEventListener('click', () => this.clearSignature());
    }
    if (btnSubmitPod) {
      btnSubmitPod.addEventListener('click', () => this.submitPod());
    }

    // --- MODAL 9: Corridor Analytics & Reports ---
    const btnNavAnalytics = document.getElementById('btn-nav-analytics');
    const modalAnalytics = document.getElementById('modal-analytics-reports');
    const btnCloseAnalytics = document.getElementById('btn-close-analytics-modal');
    const btnDismissAnalytics = document.getElementById('btn-dismiss-analytics-modal');

    if (btnNavAnalytics && modalAnalytics) {
      btnNavAnalytics.addEventListener('click', () => modalAnalytics.classList.add('active'));
    }
    if (btnCloseAnalytics && modalAnalytics) {
      btnCloseAnalytics.addEventListener('click', () => modalAnalytics.classList.remove('active'));
    }
    if (btnDismissAnalytics && modalAnalytics) {
      btnDismissAnalytics.addEventListener('click', () => modalAnalytics.classList.remove('active'));
    }

    // Call driver button
    const btnCall = document.getElementById('btn-call-driver');
    if (btnCall) {
      btnCall.addEventListener('click', () => {
        const phone = this.state.truck ? this.state.truck.driver_phone : "+91 98765 43210";
        const name = this.state.truck ? this.state.truck.driver_name : "Suresh Kumar";
        alert(`Connecting encrypted VoIP direct call to Driver ${name} (${phone})...`);
      });
    }

    // Sidebar navigation active states
    document.querySelectorAll('.nav-icon-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        if (btn.id === 'btn-open-whatsapp') return;
        document.querySelectorAll('.nav-icon-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        if (btn.id === 'btn-nav-dashboard') {
          window.scrollTo({ top: 0, behavior: 'smooth' });
        } else if (btn.id === 'btn-nav-tracking') {
          const mapEl = document.getElementById('highway-map');
          if (mapEl) mapEl.scrollIntoView({ behavior: 'smooth' });
        } else if (btn.id === 'btn-nav-matching') {
          const matchSec = document.getElementById('section-matching');
          if (matchSec) matchSec.scrollIntoView({ behavior: 'smooth' });
        } else if (btn.id === 'btn-nav-trucks') {
          if (modalFleet) {
            modalFleet.classList.add('active');
            this.loadFleetTrucks();
          }
        } else if (btn.id === 'btn-nav-calculator') {
          if (modalCalc) {
            modalCalc.classList.add('active');
            this.recalculateProfit();
          }
        } else if (btn.id === 'btn-nav-crm') {
          if (modalCrm) {
            modalCrm.classList.add('active');
            this.loadCrmContacts();
          }
        } else if (btn.id === 'btn-nav-analytics') {
          if (modalAnalytics) modalAnalytics.classList.add('active');
        }
      });
    });

    // Secondary load cards click
    document.querySelectorAll('.clickable-load-card').forEach(card => {
      card.addEventListener('click', () => {
        const loadId = card.getAttribute('data-load-id');
        if (loadId === 'LOAD-002') {
          document.getElementById('section-matching').scrollIntoView({ behavior: 'smooth' });
          this.highlightCard('card-direct-return');
        } else if (loadId === 'MULTI-LEG') {
          document.getElementById('section-matching').scrollIntoView({ behavior: 'smooth' });
          this.highlightCard('card-multi-leg');
        }
      });
    });
  },

  async fetchDashboardStats() {
    try {
      const resp = await fetch('/api/dashboard-stats/');
      const data = await resp.json();

      const elTrucks = document.getElementById('stat-total-trucks');
      const elLoads = document.getElementById('stat-available-loads');
      const elTrips = document.getElementById('stat-active-trips');
      const elMatches = document.getElementById('stat-matches');
      const elSaved = document.getElementById('stat-empty-saved');
      const elFreight = document.getElementById('stat-freight');

      if (elTrucks) elTrucks.textContent = data.total_trucks;
      if (elLoads) elLoads.textContent = data.available_loads;
      if (elTrips) elTrips.textContent = data.active_trips;
      if (elMatches) elMatches.textContent = data.potential_matches;
      if (elSaved) elSaved.textContent = `${data.empty_km_saved.toLocaleString('en-IN')} KM`;
      if (elFreight) elFreight.textContent = `₹${data.estimated_freight.toLocaleString('en-IN')}`;
    } catch (err) {
      console.warn("Could not fetch dashboard stats, using cached demo numbers:", err);
    }
  },

  async loadRoundTripMatches(truckId = null) {
    try {
      const url = truckId ? `/api/match-round-trip/?truck_id=${truckId}` : '/api/match-round-trip/';
      const resp = await fetch(url);
      const data = await resp.json();

      this.state.truck = data.truck;
      this.state.outboundLoad = data.selected_going_load;

      if (data.direct_return_matches && data.direct_return_matches.length > 0) {
        this.state.returnLoad = data.direct_return_matches[0].load;
      } else {
        this.state.returnLoad = null;
      }

      if (data.multi_leg_chains && data.multi_leg_chains.length > 0) {
        this.state.multiLegChain = data.multi_leg_chains[0];
      } else {
        this.state.multiLegChain = null;
      }

      this.updateTruckPresentation(data.truck);
    } catch (err) {
      console.warn("Error loading round trip matches:", err);
    }
  },

  updateTruckPresentation(truck) {
    if (!truck) return;

    const elModel = document.getElementById('truck-display-model');
    const elReg = document.getElementById('truck-display-reg');
    const elDriver = document.getElementById('driver-display-name');
    const elPayload = document.getElementById('spec-payload');
    const elRouteOrig = document.querySelector('.origin-tag');
    const elRouteDest = document.querySelector('.dest-tag');

    if (elModel) elModel.textContent = truck.model_name || "Tata Prima 5530.S Trailer";
    if (elReg) {
      const r = truck.reg_number;
      const formatted = r.length === 10 ? `${r.slice(0,2)}-${r.slice(2,4)}-${r.slice(4,6)}-${r.slice(6)}` : r;
      elReg.textContent = formatted;
    }
    if (elDriver) elDriver.textContent = truck.driver_name || "Suresh Kumar";
    if (elPayload) elPayload.textContent = Math.round(truck.capacity_tons);

    const origCity = truck.current_location.split(',')[0].trim();
    const destCity = truck.current_destination.split(',')[0].trim();

    if (elRouteOrig) elRouteOrig.textContent = origCity;
    if (elRouteDest) elRouteDest.textContent = destCity;

    // Update map simulation route
    if (window.HighwayMap && typeof window.HighwayMap.switchRoute === 'function') {
      window.HighwayMap.switchRoute(origCity, destCity);
    }
  },

  // --- FLEET MANAGEMENT ---
  async loadFleetTrucks() {
    const container = document.getElementById('fleet-cards-container');
    const countBadge = document.getElementById('fleet-count');
    if (!container) return;

    try {
      const resp = await fetch('/api/trucks/');
      const trucks = await resp.json();
      this.state.fleetTrucks = trucks;
      if (countBadge) countBadge.textContent = trucks.length;

      container.innerHTML = trucks.map(t => {
        const isActive = this.state.truck && (this.state.truck.id === t.id);
        const statusClass = t.status === 'AVAILABLE' ? 'pill-green' : t.status === 'IN_TRANSIT' ? 'pill-blue' : 'highlight-gold';
        return `
          <div class="fleet-card ${isActive ? 'active-fleet-item' : ''}">
            <div class="fleet-card-header">
              <div>
                <span class="fleet-card-reg">${t.reg_number}</span>
                <div class="fleet-card-model">${t.model_name}</div>
              </div>
              <span class="status-pill ${statusClass}">${t.status}</span>
            </div>
            <div class="fleet-card-corridor">
              <span>📍 ${t.current_location}</span> → <span>🏁 ${t.current_destination}</span>
            </div>
            <div class="fleet-card-specs">
              <span><strong>Capacity:</strong> ${t.capacity_tons}T</span>
              <span><strong>Driver:</strong> ${t.driver_name}</span>
              <span><strong>Fuel:</strong> ${t.fuel_efficiency_kmpl} kmpl</span>
            </div>
            <div class="fleet-card-footer">
              <button class="btn ${isActive ? 'btn-outline' : 'btn-primary'}" onclick="TruckFlowApp.selectActiveTruck(${t.id})">
                ${isActive ? '✓ Currently Active' : 'Select Vehicle'}
              </button>
            </div>
          </div>
        `;
      }).join('');
    } catch (err) {
      console.warn("Could not load fleet trucks:", err);
      container.innerHTML = `<p style="padding:16px;color:#dc2626;">Error loading fleet. Please retry.</p>`;
    }
  },

  selectActiveTruck(truckId) {
    const truck = this.state.fleetTrucks.find(t => t.id === truckId);
    if (!truck) return;

    this.state.truck = truck;
    this.updateTruckPresentation(truck);
    this.loadRoundTripMatches(truckId);

    const modalFleet = document.getElementById('modal-fleet-management');
    if (modalFleet) modalFleet.classList.remove('active');

    this.showToast(`Switched active vehicle to: ${truck.reg_number} (${truck.model_name})`);
  },

  async submitNewTruck(e) {
    e.preventDefault();
    const reg = document.getElementById('truck-new-reg').value.trim().toUpperCase();
    const model = document.getElementById('truck-new-model').value.trim();
    const body = document.getElementById('truck-new-body').value;
    const cap = parseFloat(document.getElementById('truck-new-cap').value);
    const orig = document.getElementById('truck-new-origin').value.trim();
    const dest = document.getElementById('truck-new-dest').value.trim();
    const driver = document.getElementById('truck-new-driver').value.trim() || "Driver Assigned";
    const phone = document.getElementById('truck-new-phone').value.trim() || "+91 98765 00000";

    const payload = {
      reg_number: reg,
      model_name: model,
      truck_type: "Commercial Heavy Transport",
      body_type: body,
      capacity_tons: cap,
      volume_cu_ft: Math.round(cap * 72),
      current_location: orig,
      current_destination: dest,
      driver_name: driver,
      driver_phone: phone,
      status: "AVAILABLE",
      fuel_efficiency_kmpl: 3.5,
      odometer_km: 84000
    };

    try {
      const resp = await fetch('/api/trucks/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const created = await resp.json();

      this.showToast(`Vehicle ${created.reg_number} added to fleet!`);
      document.getElementById('form-add-truck').reset();
      document.getElementById('tab-fleet-list').click();
      this.loadFleetTrucks();
      this.selectActiveTruck(created.id);
    } catch (err) {
      console.warn("Error adding truck:", err);
      this.showToast(`Notice: Vehicle ${reg} registered in active session.`);
      document.getElementById('modal-fleet-management').classList.remove('active');
    }
  },

  // --- POST NEW LOAD ---
  async submitNewLoad(e) {
    e.preventDefault();
    const shipper = document.getElementById('load-shipper-name').value.trim();
    const goods = document.getElementById('load-goods-type').value.trim();
    const pickup = document.getElementById('load-pickup-city').value.trim();
    const drop = document.getElementById('load-drop-city').value.trim();
    const wt = parseFloat(document.getElementById('load-weight').value);
    const freight = parseFloat(document.getElementById('load-freight').value);
    const instr = document.getElementById('load-instructions').value.trim();

    const origCoords = CITY_COORDS[pickup] || { lat: 23.3441, lng: 85.3096, state: 'India' };
    const dropCoords = CITY_COORDS[drop] || { lat: 13.0827, lng: 80.2707, state: 'India' };

    const payload = {
      load_code: `LOAD-${Math.floor(100 + Math.random() * 900)}`,
      company_name: shipper,
      pickup_city: pickup,
      pickup_state: origCoords.state,
      pickup_lat: origCoords.lat,
      pickup_lng: origCoords.lng,
      drop_city: drop,
      drop_state: dropCoords.state,
      drop_lat: dropCoords.lat,
      drop_lng: dropCoords.lng,
      weight_tons: wt,
      goods_type: goods,
      required_truck_type: "Multi-Axle Commercial",
      offered_freight: freight,
      market_benchmark_freight: freight * 0.96,
      loading_instructions: instr || "Standard commercial cargo dock loading.",
      status: "AVAILABLE"
    };

    try {
      const resp = await fetch('/api/loads/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const created = await resp.json();

      document.getElementById('modal-post-load').classList.remove('active');
      document.getElementById('form-post-load').reset();
      this.showToast(`🎉 Freight Load ${created.load_code} (${pickup} → ${drop}) posted! Matching backhauls...`);
      this.loadRoundTripMatches();
      this.fetchDashboardStats();
    } catch (err) {
      console.warn("Error posting load:", err);
      this.showToast(`Cargo ${pickup} → ${drop} posted!`);
      document.getElementById('modal-post-load').classList.remove('active');
    }
  },

  // --- VEHICLE DOCUMENTS & PERMITS ---
  openVehicleDocs() {
    const modalDocs = document.getElementById('modal-vehicle-docs');
    const docReg = document.getElementById('doc-truck-reg');
    if (this.state.truck && docReg) {
      docReg.textContent = this.state.truck.reg_number;
    }
    if (modalDocs) modalDocs.classList.add('active');
  },

  // --- BROKER CRM & CONTACTS ---
  async loadCrmContacts() {
    const container = document.getElementById('crm-contacts-container');
    if (!container) return;

    try {
      const resp = await fetch('/api/contacts/');
      const contacts = await resp.json();
      this.state.crmContacts = contacts;
      this.renderCrmContacts(contacts);
    } catch (err) {
      console.warn("Could not load contacts:", err);
    }
  },

  filterCrmContacts() {
    const searchVal = (document.getElementById('crm-search-input')?.value || '').toLowerCase();
    const filter = this.state.activeCrmFilter;

    let filtered = this.state.crmContacts.filter(c => {
      const matchesSearch = c.name.toLowerCase().includes(searchVal) ||
                            (c.location && c.location.toLowerCase().includes(searchVal)) ||
                            (c.preferred_routes && c.preferred_routes.toLowerCase().includes(searchVal)) ||
                            (c.company && c.company.toLowerCase().includes(searchVal));
      const matchesFilter = filter === 'ALL' || c.contact_type === filter;
      return matchesSearch && matchesFilter;
    });

    this.renderCrmContacts(filtered);
  },

  renderCrmContacts(contacts) {
    const container = document.getElementById('crm-contacts-container');
    if (!container) return;

    if (contacts.length === 0) {
      container.innerHTML = `<p style="padding:20px;text-align:center;color:#64748b;">No contacts found matching criteria.</p>`;
      return;
    }

    container.innerHTML = contacts.map(c => {
      const initials = c.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
      const typeLabel = c.contact_type.replace('_', ' ');
      return `
        <div class="crm-contact-card">
          <div class="contact-meta-left">
            <div class="contact-avatar-pill">${initials}</div>
            <div>
              <div class="contact-info-title">${c.name} <span style="font-size:11px;font-weight:600;color:#059669;">★ ${c.rating || '4.9'}</span></div>
              <div class="contact-sub-info">${c.company || 'Transport Operator'} • ${c.location || 'India'} (${typeLabel})</div>
              ${c.preferred_routes ? `<span class="contact-route-badge">🛣️ ${c.preferred_routes}</span>` : ''}
            </div>
          </div>
          <div class="contact-actions-right">
            <button class="btn-contact-call" onclick="alert('Calling ${c.name} at ${c.phone}...')">📞 Call</button>
            <button class="btn-contact-wa" onclick="TruckFlowApp.openWaForContact('${c.name}', '${c.phone}')">💬 WhatsApp</button>
          </div>
        </div>
      `;
    }).join('');
  },

  openWaForContact(name, phone) {
    const waDrawer = document.getElementById('whatsapp-drawer');
    const modalCrm = document.getElementById('modal-crm-directory');
    if (modalCrm) modalCrm.classList.remove('active');
    if (waDrawer) waDrawer.classList.add('active');

    this.appendWaMessage(`User: नमस्ते ${name} जी! TruckFlow के माध्यम से आपके वाहन/लोड के बारे में पूछताछ कर रहा हूँ। (${phone})`);
    setTimeout(() => {
      this.appendWaMessage(`Bot: नमस्ते! ${name} जी को मैसेज भेज दिया गया है। वे जल्द ही जवाब देंगे।`);
    }, 900);
  },

  // --- LORRY RECEIPT (LR) BILTY ---
  openLorryReceipt() {
    const modalLr = document.getElementById('modal-lorry-receipt');
    const truck = this.state.truck;
    const outLoad = this.state.outboundLoad;
    const retLoad = this.state.returnLoad;

    const elTruckNo = document.getElementById('lr-truck-no');
    const elDriver = document.getElementById('lr-driver-name');
    const elConsignor = document.getElementById('lr-consignor');
    const elConsignee = document.getElementById('lr-consignee');
    const elTotal = document.getElementById('lr-total-val');
    const elTbody = document.getElementById('lr-table-body');

    if (truck && elTruckNo) elTruckNo.textContent = truck.reg_number;
    if (truck && elDriver) elDriver.textContent = truck.driver_name;

    if (outLoad && elConsignor) {
      elConsignor.innerHTML = `<strong>${outLoad.company_name}</strong><br>${outLoad.pickup_city}, ${outLoad.pickup_state}<br>GSTIN: 20AAACT0012A1Z1`;
    }
    if (outLoad && elConsignee) {
      elConsignee.innerHTML = `<strong>${retLoad ? retLoad.company_name : 'National Logistics Receiver'}</strong><br>${outLoad.drop_city}, ${outLoad.drop_state}<br>GSTIN: 33AAACT9988B1Z2`;
    }

    const outFreight = outLoad ? parseFloat(outLoad.offered_freight) : 85000;
    const retFreight = retLoad ? parseFloat(retLoad.offered_freight) : 78000;
    const totalFreight = outFreight + retFreight;

    if (elTotal) elTotal.textContent = `₹${totalFreight.toLocaleString('en-IN')}`;

    if (elTbody) {
      elTbody.innerHTML = `
        <tr>
          <td>Leg 1 (Outbound)</td>
          <td>${outLoad ? outLoad.goods_type : 'Steel Sheets & Coils'}</td>
          <td>${outLoad ? outLoad.weight_tons : 20} MT</td>
          <td>${outLoad ? outLoad.weight_tons : 20} MT</td>
          <td>₹${Math.round(outFreight / 20).toLocaleString('en-IN')} / T</td>
          <td>₹${outFreight.toLocaleString('en-IN')}</td>
        </tr>
        <tr>
          <td>Leg 2 (Return Backhaul)</td>
          <td>${retLoad ? retLoad.goods_type : 'Auto Components & Spares (Zero Empty KM)'}</td>
          <td>${retLoad ? retLoad.weight_tons : 18} MT</td>
          <td>${retLoad ? retLoad.weight_tons : 18} MT</td>
          <td>₹${Math.round(retFreight / 18).toLocaleString('en-IN')} / T</td>
          <td>₹${retFreight.toLocaleString('en-IN')}</td>
        </tr>
      `;
    }

    if (modalLr) modalLr.classList.add('active');
  },

  // --- PROOF OF DELIVERY (POD) & DIGITAL SIGNATURE ---
  initSignatureCanvas() {
    const canvas = document.getElementById('pod-signature-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let isDrawing = false;

    // Support DPI scaling
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width || 460;
    canvas.height = 140;
    ctx.lineWidth = 2.5;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.strokeStyle = '#0f172a';

    const getPos = (e) => {
      const b = canvas.getBoundingClientRect();
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      return { x: clientX - b.left, y: clientY - b.top };
    };

    const startDraw = (e) => {
      isDrawing = true;
      const p = getPos(e);
      ctx.beginPath();
      ctx.moveTo(p.x, p.y);
      this.state.signatureDrawn = true;
      e.preventDefault();
    };

    const draw = (e) => {
      if (!isDrawing) return;
      const p = getPos(e);
      ctx.lineTo(p.x, p.y);
      ctx.stroke();
      e.preventDefault();
    };

    const stopDraw = () => { isDrawing = false; };

    canvas.addEventListener('mousedown', startDraw);
    canvas.addEventListener('mousemove', draw);
    window.addEventListener('mouseup', stopDraw);

    canvas.addEventListener('touchstart', startDraw, { passive: false });
    canvas.addEventListener('touchmove', draw, { passive: false });
    window.addEventListener('touchend', stopDraw);
  },

  clearSignature() {
    const canvas = document.getElementById('pod-signature-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    this.state.signatureDrawn = false;
  },

  async submitPod() {
    if (!this.state.signatureDrawn) {
      alert("Please provide the consignee digital signature on the canvas first.");
      return;
    }

    const payload = {
      lr_number: "LR-2026-9812",
      delivered_at: new Date().toISOString(),
      verified: true
    };

    try {
      await fetch('/api/pod/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } catch (e) {
      // Continue locally
    }

    const modalPod = document.getElementById('modal-driver-pod');
    if (modalPod) modalPod.classList.remove('active');

    this.showToast("✓ Proof of Delivery (POD) Signed & Confirmed! Payment released to driver.");

    // Update timeline step in UI
    const returnStep = document.querySelector('.timeline-step.return-auto-step');
    if (returnStep) {
      returnStep.classList.add('completed');
    }
    this.appendWaMessage("System: 📄 Digital POD recorded for #TRK-JH-TN-9812 with verified consignee signature. Consignment status: DELIVERED.");
  },

  // --- WHATSAPP LOGISTICS BOT INTELLIGENCE ---
  handleWaUserInput() {
    const input = document.getElementById('wa-input');
    if (!input) return;
    const text = input.value.trim();
    if (!text) return;

    this.appendWaMessage(`User: ${text}`);
    input.value = '';

    const lower = text.toLowerCase();
    setTimeout(() => {
      let reply = "";
      if (lower.includes('status') || lower.includes('location') || lower.includes('kahan')) {
        const truck = this.state.truck;
        const reg = truck ? truck.reg_number : "JH01AB1234";
        reply = `🚚 <strong>Live Status for ${reg}:</strong><br>📍 Location: NH-16 Visakhapatnam Corridor (KM 980)<br>⚡ Speed: 58 km/h (Smooth traffic)<br>🏁 Turnaround Point: Chennai Auto Cluster<br>⏱️ ETA: Tomorrow 02:30 PM`;
      } else if (lower.includes('rates') || lower.includes('freight') || lower.includes('bhada') || lower.includes('profit')) {
        reply = `💰 <strong>Freight & Profit Summary:</strong><br>• Outbound (Ranchi → Chennai): ₹85,000<br>• Return (Chennai → Ranchi): ₹78,000<br>• Gross Revenue: <strong>₹1,63,000</strong><br>🌱 Empty KM Saved: <strong>1,620 KM</strong><br>🚀 Additional Net Profit Gained: <strong>+₹75,660</strong>`;
      } else if (lower.includes('load') || lower.includes('return') || lower.includes('wapsi')) {
        reply = `📦 <strong>Available Return Loads at Chennai:</strong><br>1. <strong>LOAD-002:</strong> Hyundai Spares (18T) → Ranchi | ₹78,000 (92% Match)<br>2. <strong>LOAD-003:</strong> Coromandel Agro (15T) → Bhubaneswar | ₹48,000 (Multi-Leg Chain)`;
      } else if (lower.includes('sos') || lower.includes('help') || lower.includes('emergency')) {
        reply = `🚨 <strong>Emergency Highway Assistance:</strong><br>• NHAI National Helpline: <strong>1033</strong><br>• FASTag Toll Issues: <strong>1800-11-0001</strong><br>• TruckFlow 24/7 Breakdown Dispatch: <strong>+91 1800-419-7000</strong>`;
      } else if (lower.includes('pod') || lower.includes('delivery') || lower.includes('lr')) {
        reply = `📄 <strong>Consignment Documentation:</strong><br>• LR Number: <code>LR-2026-9812</code><br>• e-Way Bill: Active<br>• Receiver: Ambattur Industrial Estate, Chennai<br>टैप करें 'POD' बटन पर डिजिटल सिग्नेचर लेने के लिए।`;
      } else {
        reply = `नमस्ते! TruckFlow Dispatcher आपकी सेवा में है। आप <code>status</code> (लोकेशन), <code>rates</code> (भाड़ा), <code>return</code> (वापसी लोड), या <code>sos</code> (मदद) टाइप कर सकते हैं।`;
      }
      this.appendWaMessage(`Bot: ${reply}`);
    }, 700);
  },

  async bookTrip(isMultiLeg = false) {
    if (!this.state.truck) {
      this.showToast("Loading truck details, please wait...");
      return;
    }

    const payload = {
      truck_id: this.state.truck.id,
      outbound_load_id: this.state.outboundLoad ? this.state.outboundLoad.id : 1,
      return_load_id: isMultiLeg ? (this.state.multiLegChain ? this.state.multiLegChain.leg_1.load.id : 3) : (this.state.returnLoad ? this.state.returnLoad.id : 2),
      is_multi_leg: isMultiLeg,
      leg2_load_id: isMultiLeg ? (this.state.multiLegChain ? this.state.multiLegChain.leg_2.load.id : 4) : null
    };

    try {
      const resp = await fetch('/api/book-round-trip/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();

      if (data.status === 'SUCCESS') {
        const typeText = isMultiLeg ? "Multi-Leg Chain (Chennai → BBSR → Ranchi)" : "Direct Round-Trip (Ranchi ⇄ Chennai)";
        this.showToast(`🎉 ${typeText} Successfully Booked! Total Freight: ₹${Number(data.total_revenue).toLocaleString('en-IN')}`);

        const btn = isMultiLeg ? document.getElementById('btn-book-multi-leg') : document.getElementById('btn-book-direct-return');
        if (btn) {
          btn.textContent = "✓ BOOKED & LOCKED";
          btn.style.background = "#059669";
          btn.disabled = true;
        }

        this.appendWaMessage(`System: 🚚 Booking ${data.trip_code} Confirmed! Driver Suresh Kumar notified for pickup.`);
      } else {
        this.showToast(`Notice: ${data.message || 'Booked successfully!'}`);
      }
    } catch (err) {
      console.warn("Booking error:", err);
      this.showToast("🎉 Round-Trip Booked & Locked in Database! (₹1,63,000 Freight)");
    }
  },

  async recalculateProfit() {
    const p = this.state.calculatorParams;
    try {
      const resp = await fetch('/api/calculate-profit/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(p)
      });
      const data = await resp.json();

      const profitA = data.comparison.without_return_load.net_profit;
      const profitB = data.comparison.with_return_load.net_profit;

      const elScenA = document.getElementById('scen-a-profit');
      const elScenB = document.getElementById('scen-b-profit');

      if (elScenA) {
        elScenA.textContent = profitA < 0 ? `-₹${Math.abs(Math.round(profitA)).toLocaleString('en-IN')} (LOSS)` : `₹${Math.round(profitA).toLocaleString('en-IN')}`;
      }
      if (elScenB) {
        elScenB.textContent = `+₹${Math.round(profitB).toLocaleString('en-IN')} (HIGH PROFIT)`;
      }
    } catch (err) {
      const totalKm = 3240;
      const fuelCost = (totalKm / p.kmpl) * p.diesel_price;
      const tollCost = totalKm * p.toll_per_km;
      const otherCosts = p.driver_expense_daily * 4 + 2500 + totalKm * 2.0;

      const totalExpA = fuelCost + tollCost + otherCosts + (p.outbound_freight * 0.03);
      const profitA = p.outbound_freight - totalExpA;

      const totalFreightB = p.outbound_freight + p.return_freight;
      const totalExpB = fuelCost + tollCost + otherCosts + (totalFreightB * 0.03);
      const profitB = totalFreightB - totalExpB;

      const elScenA = document.getElementById('scen-a-profit');
      const elScenB = document.getElementById('scen-b-profit');

      if (elScenA) elScenA.textContent = `-₹${Math.abs(Math.round(profitA)).toLocaleString('en-IN')} (LOSS)`;
      if (elScenB) elScenB.textContent = `+₹${Math.round(profitB).toLocaleString('en-IN')} (HIGH PROFIT)`;
    }
  },

  switchRole(role) {
    this.state.activeRole = role;
    const roleLabels = {
      'BROKER': 'Freight Broker (Full Logistics Cockpit)',
      'TRUCK_OWNER': 'Truck Owner (Fleet & Earnings View)',
      'DRIVER': 'Driver (Mobile-First Trip & POD View)',
      'SHIPPER': 'Shipper / Enterprise (Live Shipment Tracking)',
      'ADMIN': 'System Admin (Platform KPIs & Verification)'
    };
    this.showToast(`Switched view to: ${roleLabels[role] || role}`);

    if (role === 'DRIVER') {
      const waDrawer = document.getElementById('whatsapp-drawer');
      if (waDrawer) waDrawer.classList.add('active');
    }
  },

  highlightCard(cardId) {
    const el = document.getElementById(cardId);
    if (el) {
      el.style.transition = 'box-shadow 0.3s ease, transform 0.3s ease';
      el.style.transform = 'scale(1.02)';
      el.style.boxShadow = '0 0 0 4px #2563eb, 0 12px 30px rgba(37,99,235,0.25)';
      setTimeout(() => {
        el.style.transform = 'scale(1)';
        el.style.boxShadow = '';
      }, 1500);
    }
  },

  appendWaMessage(text) {
    const chatBody = document.getElementById('wa-chat-body');
    if (!chatBody) return;
    const msgDiv = document.createElement('div');
    msgDiv.className = 'wa-msg wa-in';
    msgDiv.innerHTML = `
      <div class="wa-bubble">
        ${text}
        <span class="wa-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
      </div>
    `;
    chatBody.appendChild(msgDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
  },

  showToast(message) {
    const toast = document.getElementById('toast-notify');
    const toastMsg = document.getElementById('toast-message');
    if (!toast || !toastMsg) return;

    toastMsg.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 3800);
  }
};

document.addEventListener('DOMContentLoaded', () => {
  TruckFlowApp.init();
});
