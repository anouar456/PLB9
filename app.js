/* ============================================================
   DURASIA — moteur de supervision (front-end)
   Auteur : équipe DURASIA · École Centrale Casablanca
   Données réelles embarquées dans DATA (voir index.html / dataset.json)
   ============================================================ */
'use strict';

const $ = (s) => document.querySelector(s);
const fmt = (n, d = 0) => Number(n).toLocaleString('fr-FR', { minimumFractionDigits: d, maximumFractionDigits: d });

let MODE = 'demo';
let idx = 0;
let timer = null;
let prodChart, predChart;
let liveBuf = [];                 // points affichés sur le graphe live
const PROFILE = DATA.day_profile; // journée mesurée
const settings = {
  api: localStorage.getItem('durasia_api') || '',
  key: localStorage.getItem('durasia_key') || ''
};

/* ---------- LOGIN ---------- */
function doLogin() {
  $('#login').classList.remove('open');
  setTimeout(() => { $('#login').style.display = 'none'; }, 350);
  $('#app').style.display = 'block';
  boot();
}

/* ---------- BOOT ---------- */
function boot() {
  buildArcSvg();
  buildKpis();
  buildSensors();
  buildEnv();
  buildArch();
  buildAlerts();
  buildQuickChips();
  initChat();
  initProdChart();
  initPredChart();
  buildFeatImp();
  $('#rfr2').textContent = DATA.ml.rf_r2;
  $('#plr2').textContent = DATA.ml.poly_r2;
  $('#apiUrl').value = settings.api;
  $('#anthKey').value = settings.key;
  revealOnScroll();
  // démarre la boucle démo
  liveBuf = PROFILE.slice(0, 12).map(p => ({ ...p }));
  idx = 12;
  refreshAll(PROFILE[idx - 1]);
  startLoop();
}

/* ---------- MODE démo / live ---------- */
function setMode(m) {
  MODE = m;
  [...$('#modeSeg').children].forEach((b, i) => b.classList.toggle('active', (i === 0) === (m === 'demo')));
  if (m === 'live' && !settings.api) {
    toast('Renseignez l’URL de l’API Raspberry Pi dans les réglages', 'warn');
    openSettings();
  }
  $('#statusPill').innerHTML = m === 'live'
    ? '<span class="live-dot"></span> Connexion Live'
    : '<span class="live-dot"></span> Système actif (démo)';
  startLoop();
}

function startLoop() {
  clearInterval(timer);
  timer = setInterval(tick, MODE === 'live' ? 2500 : 1600);
}

async function tick() {
  if (MODE === 'live') return tickLive();
  // démo : avance dans la journée mesurée, en boucle
  const p = PROFILE[idx % PROFILE.length];
  idx++;
  liveBuf.push({ ...p });
  if (liveBuf.length > 60) liveBuf.shift();
  refreshAll(p);
}

async function tickLive() {
  try {
    const r = await fetch(settings.api, { cache: 'no-store' });
    if (!r.ok) throw new Error(r.status);
    const d = await r.json();
    // mapping souple des champs renvoyés par l'API Raspberry Pi
    const p = {
      time: (d.time || new Date().toTimeString().slice(0, 5)),
      p: +(d.puissance_W ?? d.p ?? (d.tension_V * d.courant_A) ?? 0),
      v: +(d.tension_V ?? d.v ?? 0),
      i: +(d.courant_A ?? d.i ?? 0),
      temp: +(d.temp_C ?? d.temp ?? 0),
      lux: +(d.lux ?? 0),
      ghi: +(d.ciel_clair_ghi_Wm2 ?? d.ghi ?? 0),
      elev: +(d.solar_elevation_deg ?? d.elev ?? 0),
      airmass: +(d.airmass_abs ?? 1.2)
    };
    liveBuf.push(p); if (liveBuf.length > 60) liveBuf.shift();
    $('#statusPill').innerHTML = '<span class="live-dot"></span> Live connecté';
    refreshAll(p);
  } catch (e) {
    $('#statusPill').innerHTML = '<span class="live-dot" style="background:var(--red)"></span> Live indisponible';
    $('#statusPill').style.background = '#fdeceb'; $('#statusPill').style.color = 'var(--red)';
  }
}

/* ---------- REFRESH global ---------- */
function refreshAll(p) {
  $('#clock').textContent = p.time;
  animateKpis(p);
  updateSensors(p);
  updateSun(p);
  updateEnv(p);
  updateProdChart();
  updateAiReco(p);
}

/* ============================================================
   KPI
   ============================================================ */
const KPIS = [
  { id: 'k_power', label: 'Puissance instantanée', unit: 'W', icon: 'fa-bolt', color: 'var(--green)', bg: 'var(--mint)', get: p => p.p },
  { id: 'k_energy', label: 'Énergie cumulée', unit: 'Wh', icon: 'fa-battery-three-quarters', color: 'var(--amber-d)', bg: 'var(--amber-soft)', get: () => DATA.kpis.energy_total_Wh },
  { id: 'k_temp', label: 'Température panneau', unit: '°C', icon: 'fa-temperature-half', color: 'var(--red)', bg: '#fdeceb', get: p => p.temp },
  { id: 'k_health', label: 'Santé système', unit: '%', icon: 'fa-heart-pulse', color: 'var(--blue)', bg: '#e9f3fb', get: p => healthScore(p) }
];
function buildKpis() {
  $('#kpiRow').innerHTML = KPIS.map(k => `
    <div class="reveal card lift" style="padding:18px 18px 16px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
        <div style="width:38px;height:38px;border-radius:12px;background:${k.bg};color:${k.color};display:grid;place-items:center"><i class="fas ${k.icon}"></i></div>
        <span class="live-dot"></span>
      </div>
      <div class="kbig" style="font-size:30px;color:var(--green-deep)"><span id="${k.id}">0</span><span style="font-size:15px;color:var(--ink-faint);font-weight:600;margin-left:4px">${k.unit}</span></div>
      <div class="muted" style="font-size:12.5px;margin-top:5px">${k.label}</div>
    </div>`).join('');
}
function animateKpis(p) {
  KPIS.forEach(k => animateNum($('#' + k.id), k.get(p), k.id === 'k_energy' || k.id === 'k_health' ? 0 : 1));
}
function healthScore(p) {
  let s = 100;
  if (p.temp > 45) s -= (p.temp - 45) * 2.2;          // surchauffe
  if (p.lux > 1200 && p.p < 8) s -= 14;                // forte lumière, faible prod => encrassement probable
  return Math.max(60, Math.round(s));
}
function animateNum(el, to, dec) {
  if (!el) return;
  const from = parseFloat(el.dataset.v || '0'); const t0 = performance.now(); const dur = 600;
  function step(t) {
    const k = Math.min(1, (t - t0) / dur); const e = 1 - Math.pow(1 - k, 3);
    el.textContent = fmt(from + (to - from) * e, dec); if (k < 1) requestAnimationFrame(step); else el.dataset.v = to;
  }
  requestAnimationFrame(step);
}

/* ============================================================
   CAPTEURS (jauges SVG)
   ============================================================ */
const SENSORS = [
  { id: 's_lux', label: 'Irradiance / Lux', sub: 'Capteur lumière', unit: 'lx', max: 2200, color: '#f3a833', get: p => p.lux },
  { id: 's_temp', label: 'Temp. panneau', sub: 'DS18B20', unit: '°C', max: 70, color: '#e2554b', get: p => p.temp },
  { id: 's_v', label: 'Tension bus', sub: 'ADS1115 · A0', unit: 'V', max: 21, color: '#15a05a', get: p => p.v },
  { id: 's_i', label: 'Courant', sub: 'ADS1115 · A1', unit: 'A', max: 3.5, color: '#2f8fd6', get: p => p.i }
];
function gauge(id, color) {
  const r = 46, c = 2 * Math.PI * r;
  return `<svg viewBox="0 0 120 120" style="width:118px;height:118px">
    <circle cx="60" cy="60" r="${r}" fill="none" class="gauge-track" stroke-width="9"/>
    <circle id="${id}_arc" cx="60" cy="60" r="${r}" fill="none" stroke="${color}" stroke-width="9" stroke-linecap="round"
      stroke-dasharray="${c}" stroke-dashoffset="${c}" transform="rotate(-90 60 60)" style="transition:stroke-dashoffset .8s cubic-bezier(.2,.7,.2,1)"/>
    <text id="${id}_txt" x="60" y="58" text-anchor="middle" font-family="Manrope" font-weight="800" font-size="22" fill="var(--green-deep)">0</text>
    <text id="${id}_unit" x="60" y="76" text-anchor="middle" font-size="11" fill="var(--ink-faint)"></text>
  </svg>`;
}
function buildSensors() {
  $('#sensorRow').innerHTML = SENSORS.map(s => `
    <div class="reveal card lift" style="padding:18px;text-align:center">
      <div style="display:flex;align-items:center;gap:10px;text-align:left;margin-bottom:6px">
        <div style="width:34px;height:34px;border-radius:11px;background:${s.color}1a;color:${s.color};display:grid;place-items:center"><i class="fas fa-circle-dot" style="font-size:12px"></i></div>
        <div><div style="font-weight:600;font-size:13.5px;color:var(--green-deep)">${s.label}</div><div class="muted" style="font-size:11px">${s.sub}</div></div>
      </div>
      ${gauge(s.id, s.color)}
    </div>`).join('');
}
function updateSensors(p) {
  const r = 46, c = 2 * Math.PI * r;
  SENSORS.forEach(s => {
    const v = s.get(p); const pct = Math.max(0, Math.min(1, v / s.max));
    const arc = document.getElementById(s.id + '_arc');
    if (arc) arc.style.strokeDashoffset = c * (1 - pct);
    const txt = document.getElementById(s.id + '_txt');
    if (txt) txt.textContent = fmt(v, s.unit === 'A' ? 2 : (s.unit === 'V' ? 1 : 0));
    const u = document.getElementById(s.id + '_unit'); if (u) u.textContent = s.unit;
  });
}

/* ============================================================
   COURSE DU SOLEIL (arc SVG)
   ============================================================ */
function buildArcSvg() {
  $('#sunArc').innerHTML = `<svg viewBox="0 0 320 150" style="width:100%;height:auto">
    <defs><linearGradient id="skyg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fdf3e1"/><stop offset="1" stop-color="#eef5ef"/></linearGradient></defs>
    <path d="M10 140 A150 150 0 0 1 310 140" fill="none" stroke="rgba(17,36,27,.10)" stroke-width="2" stroke-dasharray="3 4"/>
    <line x1="10" y1="140" x2="310" y2="140" stroke="rgba(17,36,27,.12)" stroke-width="1.5"/>
    <circle id="sunDot" cx="160" cy="20" r="11" fill="#f3a833"/>
    <circle id="sunGlow" cx="160" cy="20" r="20" fill="#f3a833" opacity=".25"/>
  </svg>`;
}
function updateSun(p) {
  const elev = Math.max(0, p.elev); // 0..90
  // abscisse = progression dans la journée mesurée ; ordonnée = élévation solaire
  const dot = document.getElementById('sunDot'), glow = document.getElementById('sunGlow');
  const px = 30 + ((idx % PROFILE.length) / PROFILE.length) * 260;
  const py = 140 - (elev / 90) * 120;
  if (dot) { dot.setAttribute('cx', px); dot.setAttribute('cy', py); }
  if (glow) { glow.setAttribute('cx', px); glow.setAttribute('cy', py); }
  $('#elevVal').textContent = fmt(p.elev, 0) + '°';
  $('#ghiVal').textContent = fmt(p.ghi, 0);
  $('#luxVal').textContent = fmt(p.lux, 0);
}

/* ============================================================
   ENVIRONNEMENT (modèle météo)
   ============================================================ */
const ENV = [
  { k: 'temp_air', icon: 'fa-temperature-low', color: 'var(--amber-d)', label: 'Air ambiant', unit: '°C', v: 23.5 },
  { k: 'hum', icon: 'fa-droplet', color: 'var(--blue)', label: 'Humidité', unit: '%', v: 67 },
  { k: 'wind', icon: 'fa-wind', color: '#2bb3a3', label: 'Vent', unit: 'm/s', v: 5.0 },
  { k: 'dew', icon: 'fa-snowflake', color: '#7c8cff', label: 'Point de rosée', unit: '°C', v: 17 }
];
function buildEnv() {
  $('#envGrid').innerHTML = ENV.map(e => `
    <div style="background:var(--surface-2);border:1px solid var(--line);border-radius:14px;padding:14px">
      <div style="display:flex;align-items:center;gap:9px;margin-bottom:8px">
        <div style="width:30px;height:30px;border-radius:9px;background:${e.color}1a;color:${e.color};display:grid;place-items:center"><i class="fas ${e.icon}" style="font-size:12px"></i></div>
        <span class="muted" style="font-size:12px">${e.label}</span>
      </div>
      <div class="kbig" style="font-size:23px;color:var(--green-deep)">${fmt(e.v, e.unit === 'm/s' ? 1 : 0)}<span style="font-size:12px;color:var(--ink-faint);margin-left:3px">${e.unit}</span></div>
    </div>`).join('');
}
function updateEnv() {/* données météo modèle ~ stables sur la fenêtre */ }

/* ============================================================
   ARCHITECTURE : refroidissement + stockage
   ============================================================ */
function buildArch() {
  $('#coolBox').innerHTML = `
    <p class="muted" style="font-size:13px;margin-bottom:14px">Couche d'hydrogel + brumisation pilotée par IA. Déclenchement uniquement si la température dépasse le seuil — minimise la consommation d'eau.</p>
    <div id="coolState"></div>
    <div style="display:flex;gap:10px;margin-top:14px">
      <div style="flex:1;background:var(--surface-2);border:1px solid var(--line);border-radius:12px;padding:12px;text-align:center">
        <div class="kbig" style="font-size:20px;color:var(--blue)" id="coolDrop">−6 °C</div><div class="muted" style="font-size:11px">Gain refroid.</div></div>
      <div style="flex:1;background:var(--surface-2);border:1px solid var(--line);border-radius:12px;padding:12px;text-align:center">
        <div class="kbig" style="font-size:20px;color:var(--green)" id="coolWater">0.4 L/h</div><div class="muted" style="font-size:11px">Eau utilisée</div></div>
    </div>`;
  $('#storeBox').innerHTML = `
    <p class="muted" style="font-size:13px;margin-bottom:14px">Batterie (autonomie) + supercondensateur série-parallèle (tampon de puissance) : lisse les pics et prolonge la durée de vie.</p>
    ${bar('Batterie Li-ion', 78, 'var(--green)', 'fa-battery-three-quarters')}
    ${bar('Supercondensateur', 54, 'var(--amber)', 'fa-bolt')}
    <div style="display:flex;gap:10px;margin-top:6px">
      <div style="flex:1;background:var(--surface-2);border:1px solid var(--line);border-radius:12px;padding:12px;text-align:center">
        <div class="kbig" style="font-size:20px;color:var(--green-deep)">+38%</div><div class="muted" style="font-size:11px">Durée de vie batt.</div></div>
      <div style="flex:1;background:var(--surface-2);border:1px solid var(--line);border-radius:12px;padding:12px;text-align:center">
        <div class="kbig" style="font-size:20px;color:var(--green-deep)" id="busV">18.4 V</div><div class="muted" style="font-size:11px">Tension bus</div></div>
    </div>`;
}
function bar(label, pct, color, icon) {
  return `<div style="margin-bottom:13px">
    <div style="display:flex;justify-content:space-between;font-size:12.5px;margin-bottom:6px"><span style="color:var(--green-deep);font-weight:600"><i class="fas ${icon}" style="color:${color};margin-right:6px"></i>${label}</span><span class="muted">${pct}%</span></div>
    <div style="height:9px;background:rgba(17,36,27,.07);border-radius:9px;overflow:hidden"><div style="height:100%;width:${pct}%;background:linear-gradient(90deg,${color},${color});border-radius:9px"></div></div>
  </div>`;
}

/* ============================================================
   ALERTES
   ============================================================ */
function buildAlerts() {
  const A = [
    { sev: 'mineur', icon: 'fa-broom', t: 'Nettoyage recommandé', d: 'Forte luminosité mais production réduite en milieu d’après-midi : encrassement / poussière probable sur le panneau.', c: '#ca8a04', bg: '#fefce8' },
    { sev: 'modéré', icon: 'fa-temperature-arrow-up', t: 'Pic de température détecté', d: 'Le panneau a atteint 50 °C. La brumisation a été déclenchée pour préserver le rendement.', c: '#ea580c', bg: '#fff7ed' },
    { sev: 'bon', icon: 'fa-circle-check', t: 'Stockage hybride nominal', d: 'Batterie et supercondensateur fonctionnent dans les plages attendues. Aucune action requise.', c: '#16a34a', bg: '#f0fdf4' }
  ];
  $('#alertsBox').innerHTML = A.map(a => `
    <div style="display:flex;gap:13px;align-items:flex-start;background:${a.bg};border:1px solid ${a.c}33;border-radius:14px;padding:14px 16px">
      <div style="width:36px;height:36px;border-radius:11px;background:#fff;color:${a.c};display:grid;place-items:center;flex-shrink:0"><i class="fas ${a.icon}"></i></div>
      <div><div style="font-weight:700;color:var(--green-deep);font-size:14px;display:flex;align-items:center;gap:8px">${a.t}<span class="pill" style="background:${a.c}1a;color:${a.c};padding:2px 9px;font-size:10.5px;text-transform:uppercase">${a.sev}</span></div>
      <div class="muted" style="font-size:13px;margin-top:3px;line-height:1.5">${a.d}</div></div>
    </div>`).join('');
}

/* ============================================================
   AI reco (banner)
   ============================================================ */
function updateAiReco(p) {
  let msg;
  if (p.temp > 45) msg = `Température panneau élevée (${fmt(p.temp,0)} °C) : la brumisation intelligente est activée pour limiter la perte de rendement. Surveillance accrue.`;
  else if (p.lux > 1200 && p.p < 8) msg = `Luminosité forte (${fmt(p.lux,0)} lx) mais production faible (${fmt(p.p,1)} W) — un nettoyage du panneau est conseillé pour récupérer la production perdue.`;
  else if (p.p > 30) msg = `Excellente production (${fmt(p.p,1)} W) et conditions favorables. Surplus dirigé vers le stockage hybride — bon moment pour les charges différables.`;
  else msg = `Conditions stables. Production ${fmt(p.p,1)} W à ${fmt(p.v,1)} V. Le système fonctionne normalement, aucune maintenance immédiate requise.`;
  $('#aiReco').textContent = msg;
}

/* ============================================================
   GRAPHIQUE PRODUCTION
   ============================================================ */
function gradFill(ctx, color) {
  const g = ctx.createLinearGradient(0, 0, 0, 240);
  g.addColorStop(0, color + '55'); g.addColorStop(1, color + '03'); return g;
}
function initProdChart() {
  const ctx = $('#prodChart').getContext('2d');
  prodChart = new Chart(ctx, {
    type: 'line',
    data: { labels: [], datasets: [
      { label: 'Puissance (W)', data: [], borderColor: '#15a05a', backgroundColor: gradFill(ctx, '#15a05a'), borderWidth: 2.4, fill: true, tension: .4, pointRadius: 0, yAxisID: 'y' },
      { label: 'Température (°C)', data: [], borderColor: '#e2554b', borderWidth: 1.6, borderDash: [5, 4], fill: false, tension: .4, pointRadius: 0, yAxisID: 'y1' }
    ]},
    options: baseOpts({ y: { title: { display: true, text: 'W' } }, y1: { position: 'right', grid: { drawOnChartArea: false }, title: { display: true, text: '°C' } } })
  });
}
function updateProdChart() {
  if (!prodChart) return;
  prodChart.data.labels = liveBuf.map(p => p.time);
  prodChart.data.datasets[0].data = liveBuf.map(p => p.p);
  prodChart.data.datasets[1].data = liveBuf.map(p => p.temp);
  prodChart.update('none');
}

/* ============================================================
   PRÉDICTION ML (modèle polynomial embarqué)
   ============================================================ */
function predictPower(feat) { // feat aligné sur DATA.ml.embed.keyf
  const e = DATA.ml.embed; let y = e.intercept;
  for (let t = 0; t < e.coef.length; t++) {
    let term = e.coef[t];
    for (let j = 0; j < e.keyf.length; j++) term *= Math.pow(feat[j], e.powers[t][j]);
    y += term;
  }
  return Math.max(0, y);
}
function initPredChart() {
  // construit mesuré vs prédit sur la journée mesurée
  const labels = PROFILE.map(p => p.time);
  const measured = PROFILE.map(p => p.p);
  const predicted = PROFILE.map(p => {
    const am = p.elev > 1 ? Math.min(6, 1 / Math.sin(p.elev * Math.PI / 180)) : 6;
    return predictPower([p.elev, p.ghi, p.lux, p.temp, am]);
  });
  const ctx = $('#predChart').getContext('2d');
  predChart = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets: [
      { label: 'Mesuré (W)', data: measured, borderColor: '#15a05a', backgroundColor: gradFill(ctx, '#15a05a'), borderWidth: 2.2, fill: true, tension: .4, pointRadius: 0 },
      { label: 'Prédit IA (W)', data: predicted, borderColor: '#7c5cd6', borderWidth: 2, borderDash: [6, 4], fill: false, tension: .4, pointRadius: 0 }
    ]},
    options: baseOpts({ y: { title: { display: true, text: 'Puissance (W)' } } })
  });
}
function buildFeatImp() {
  const imp = DATA.ml.importances;
  const entries = Object.entries(imp).sort((a, b) => b[1] - a[1]).slice(0, 5);
  const names = { solar_elevation_deg: 'Élévation solaire', ciel_clair_ghi_Wm2: 'Irradiance (GHI)', lux: 'Luminosité', temp_C: 'Temp. panneau', airmass_abs: 'Masse d’air', temp_air_C_model: 'Temp. air', humidite_rel_pct_model: 'Humidité', vent_ms_model: 'Vent' };
  const max = entries[0][1];
  $('#featImp').innerHTML = `<div class="muted" style="font-size:12.5px;margin-bottom:10px;font-weight:600"><i class="fas fa-list-ol"></i> Variables les plus influentes (Random Forest)</div>` +
    entries.map(([k, v]) => `<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
      <span style="width:130px;font-size:12.5px;color:var(--green-deep)">${names[k] || k}</span>
      <div style="flex:1;height:8px;background:rgba(17,36,27,.07);border-radius:8px;overflow:hidden"><div style="height:100%;width:${(v / max * 100).toFixed(0)}%;background:linear-gradient(90deg,#7c5cd6,#a78bfa);border-radius:8px"></div></div>
      <span class="muted" style="font-size:11.5px;width:38px;text-align:right">${(v * 100).toFixed(0)}%</span></div>`).join('');
}

function baseOpts(scales) {
  return {
    responsive: true, maintainAspectRatio: true, animation: { duration: 500 },
    interaction: { mode: 'index', intersect: false },
    plugins: { legend: { labels: { font: { family: 'Inter', size: 12 }, usePointStyle: true, boxWidth: 7, color: '#52635a' } },
      tooltip: { backgroundColor: '#0f2e22', padding: 11, cornerRadius: 10, titleFont: { family: 'Manrope' } } },
    scales: Object.assign({ x: { grid: { display: false }, ticks: { maxTicksLimit: 8, font: { size: 11 }, color: '#8a988f' } } },
      Object.fromEntries(Object.entries(scales).map(([k, v]) => [k, Object.assign({ grid: { color: 'rgba(17,36,27,.05)' }, ticks: { font: { size: 11 }, color: '#8a988f' } }, v)])))
  };
}

/* ============================================================
   CHATBOT
   ============================================================ */
const CHIPS = ['État du système', 'Production', 'Maintenance', 'Prévisions', 'Stockage'];
function buildQuickChips() {
  $('#quickChips').innerHTML = CHIPS.map(c => `<button onclick="quick('${c}')" style="font-size:11.5px;padding:6px 11px;border-radius:999px;border:1px solid var(--line);background:var(--mint);color:var(--green-d);cursor:pointer">${c}</button>`).join('');
}
function initChat() {
  pushMsg('bot', 'Bonjour 👋 Je suis l’assistant DURASIA. Posez-moi une question sur votre système photovoltaïque, sa production, sa maintenance ou ses prévisions.');
}
function quick(t) { $('#chatInput').value = t; sendChat(); }
function pushMsg(who, html) {
  const box = $('#chatMsgs');
  const wrap = document.createElement('div');
  wrap.style.cssText = 'display:flex;gap:9px;' + (who === 'me' ? 'flex-direction:row-reverse' : '');
  wrap.innerHTML = `
    <div style="width:30px;height:30px;border-radius:9px;flex-shrink:0;display:grid;place-items:center;background:${who === 'me' ? 'var(--amber-soft)' : 'var(--mint)'};color:${who === 'me' ? 'var(--amber-d)' : 'var(--green)'}"><i class="fas ${who === 'me' ? 'fa-user' : 'fa-robot'}" style="font-size:12px"></i></div>
    <div style="max-width:78%;background:${who === 'me' ? 'var(--green)' : '#fff'};color:${who === 'me' ? '#fff' : 'var(--ink)'};border:1px solid var(--line);padding:10px 13px;border-radius:14px;font-size:13.5px;line-height:1.5">${html}</div>`;
  box.appendChild(wrap); box.scrollTop = box.scrollHeight;
  return wrap;
}
async function sendChat() {
  const inp = $('#chatInput'); const q = inp.value.trim(); if (!q) return;
  pushMsg('me', q); inp.value = '';
  const typing = pushMsg('bot', '<div class="typing" style="display:flex;gap:4px;padding:3px 0"><span></span><span></span><span></span></div>');
  let answer;
  if (settings.key) { try { answer = await askAnthropic(q); } catch (e) { answer = offlineAnswer(q) + '<br><span style="color:var(--ink-faint);font-size:11px">(réponse hors-ligne — clé API invalide)</span>'; } }
  else answer = offlineAnswer(q);
  typing.remove(); pushMsg('bot', answer);
}
function offlineAnswer(q) {
  const s = q.toLowerCase(); const k = DATA.kpis;
  if (/état|etat|statut|santé|sante/.test(s)) return `Le système est <b>actif et nominal</b>. Production de pointe mesurée : <b>${k.peak_power_W} W</b>, tension nominale du bus : <b>${k.nominal_voltage_V} V</b>, température max relevée : <b>${k.max_temp_C} °C</b>. Aucune anomalie critique.`;
  if (/production|énergie|energie|puissance/.test(s)) return `Sur la fenêtre suivie, l’énergie cumulée est de <b>${k.energy_total_Wh} Wh</b> avec un pic de <b>${k.peak_power_W} W</b> et un courant max de <b>${k.max_current_A} A</b>. La production suit l’irradiance et chute quand le panneau surchauffe.`;
  if (/maintenance|nettoy|poussi|encrass/.test(s)) return `Recommandation : <b>nettoyer le panneau</b>. Une forte luminosité associée à une production réduite indique un encrassement (poussière). Un nettoyage manuel permettrait de récupérer plusieurs watts.`;
  if (/prévis|previs|demain|futur|prédi|predi/.test(s)) return `Le modèle IA (Random Forest, R²=<b>${DATA.ml.rf_r2}</b>) prédit la production à partir de l’irradiance, de l’élévation solaire et de la température. Consultez la section « Prédiction de production » pour la courbe mesuré vs prédit.`;
  if (/stock|batt|condensa|super/.test(s)) return `Le <b>stockage hybride</b> associe une batterie Li-ion (autonomie) et un supercondensateur série-parallèle (tampon de puissance). Il absorbe les pics, réduit le stress de la batterie et prolonge sa durée de vie (~+38%).`;
  if (/refroid|brumis|température|temperature|chaud/.test(s)) return `Le <b>refroidissement hygroscopique</b> (hydrogel + brumisation) se déclenche au-delà du seuil de température pour limiter la perte de rendement, tout en minimisant la consommation d’eau.`;
  return `Je peux vous renseigner sur l’<b>état du système</b>, la <b>production</b>, la <b>maintenance</b>, le <b>stockage hybride</b>, le <b>refroidissement</b> et les <b>prévisions IA</b>. Que souhaitez-vous savoir ?`;
}
async function askAnthropic(q) {
  const ctx = `Données système DURASIA : pic ${DATA.kpis.peak_power_W} W, énergie ${DATA.kpis.energy_total_Wh} Wh, temp max ${DATA.kpis.max_temp_C}°C, tension nominale ${DATA.kpis.nominal_voltage_V} V, courant max ${DATA.kpis.max_current_A} A. Modèle IA R²=${DATA.ml.rf_r2}.`;
  const r = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-api-key': settings.key, 'anthropic-version': '2023-06-01', 'anthropic-dangerous-direct-browser-access': 'true' },
    body: JSON.stringify({ model: 'claude-3-5-haiku-20241022', max_tokens: 400, system: 'Tu es l’assistant du système photovoltaïque DURASIA. Réponds en français, de façon concise et utile, en t’appuyant sur les données fournies. ' + ctx, messages: [{ role: 'user', content: q }] })
  });
  const d = await r.json();
  if (d.content && d.content[0]) return d.content[0].text.replace(/\n/g, '<br>');
  throw new Error('api');
}

/* ============================================================
   INSPECTION IA (photo panneau)
   ============================================================ */
function onInspFile(e) {
  const f = e.target.files[0]; if (!f) return;
  const reader = new FileReader();
  reader.onload = () => runInspection(reader.result, f.type);
  reader.readAsDataURL(f);
}
async function runInspection(dataUrl, mime) {
  $('#inspDrop').style.display = 'none';
  $('#inspResult').innerHTML = `
    <div style="position:relative;border-radius:14px;overflow:hidden;border:1px solid var(--line)">
      <img src="${dataUrl}" style="width:100%;display:block">
      <div id="scanline" style="position:absolute;left:0;right:0;height:2px;background:var(--amber);box-shadow:0 0 12px var(--amber)"></div>
    </div>
    <p class="muted" style="text-align:center;font-size:12.5px;margin:12px 0"><i class="fas fa-spinner fa-spin"></i> Analyse IA en cours…</p>`;
  animateScan();
  let result;
  if (settings.key) { try { result = await inspectAnthropic(dataUrl, mime); } catch (e) { result = demoInspection(); } }
  else { await new Promise(r => setTimeout(r, 1700)); result = demoInspection(); }
  renderInspection(dataUrl, result);
}
function animateScan() {
  const l = $('#scanline'); if (!l) return; let y = 0, dir = 1;
  const it = setInterval(() => { if (!document.getElementById('scanline')) return clearInterval(it); y += dir * 3; if (y > 160 || y < 0) dir *= -1; l.style.top = y + 'px'; }, 24);
}
function demoInspection() {
  return { score: 82, etat: 'Bon état général', zones: [
    { sev: 'mineur', t: 'Dépôt de poussière', d: 'Encrassement léger en partie basse — nettoyage conseillé.' },
    { sev: 'bon', t: 'Cellules intègres', d: 'Aucune micro-fissure ni point chaud visible.' },
    { sev: 'bon', t: 'Cadre & connectique', d: 'Cadre droit, boîte de jonction intacte.' }
  ], reco: ['Nettoyage doux à l’eau claire en partie basse', 'Réinspection sous 2 semaines', 'Vérifier l’absence d’ombrage au lever du soleil'] };
}
async function inspectAnthropic(dataUrl, mime) {
  const b64 = dataUrl.split(',')[1];
  const r = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-api-key': settings.key, 'anthropic-version': '2023-06-01', 'anthropic-dangerous-direct-browser-access': 'true' },
    body: JSON.stringify({ model: 'claude-3-5-sonnet-20241022', max_tokens: 700,
      messages: [{ role: 'user', content: [
        { type: 'image', source: { type: 'base64', media_type: mime, data: b64 } },
        { type: 'text', text: 'Tu es un expert en maintenance de panneaux photovoltaïques. Analyse ce panneau et renvoie UNIQUEMENT un JSON: {"score":0-100,"etat":"...","zones":[{"sev":"critique|modéré|mineur|bon","t":"titre","d":"description"}],"reco":["..."]}' }
      ] }] })
  });
  const d = await r.json();
  const txt = d.content[0].text; const m = txt.match(/\{[\s\S]*\}/);
  return JSON.parse(m[0]);
}
function renderInspection(dataUrl, res) {
  const sevColor = { critique: '#dc2626', 'modéré': '#ea580c', modere: '#ea580c', mineur: '#ca8a04', bon: '#16a34a' };
  const scoreColor = res.score >= 80 ? '#16a34a' : res.score >= 60 ? '#ca8a04' : '#dc2626';
  $('#inspResult').innerHTML = `
    <div style="border-radius:14px;overflow:hidden;border:1px solid var(--line);margin-bottom:14px"><img src="${dataUrl}" style="width:100%;display:block"></div>
    <div style="display:flex;align-items:center;gap:14px;background:var(--surface-2);border:1px solid var(--line);border-radius:14px;padding:14px;margin-bottom:12px">
      <div style="width:58px;height:58px;border-radius:50%;display:grid;place-items:center;background:conic-gradient(${scoreColor} ${res.score * 3.6}deg,rgba(17,36,27,.08) 0)">
        <div style="width:46px;height:46px;border-radius:50%;background:#fff;display:grid;place-items:center;font-family:Manrope;font-weight:800;color:${scoreColor}">${res.score}</div></div>
      <div><div style="font-weight:700;color:var(--green-deep)">${res.etat}</div><div class="muted" style="font-size:12px">Score de santé du panneau</div></div>
    </div>
    ${res.zones.map(z => `<div style="display:flex;gap:11px;align-items:flex-start;padding:11px;border:1px solid ${(sevColor[z.sev] || '#16a34a')}33;background:${(sevColor[z.sev] || '#16a34a')}0d;border-radius:12px;margin-bottom:9px">
      <i class="fas fa-circle" style="color:${sevColor[z.sev] || '#16a34a'};font-size:9px;margin-top:5px"></i>
      <div><div style="font-weight:600;font-size:13px;color:var(--green-deep)">${z.t} <span style="font-size:10.5px;color:${sevColor[z.sev] || '#16a34a'};text-transform:uppercase">· ${z.sev}</span></div><div class="muted" style="font-size:12px;margin-top:2px">${z.d}</div></div></div>`).join('')}
    <div style="background:var(--mint-2);border:1px solid var(--line);border-radius:12px;padding:13px;margin-top:6px">
      <div style="font-weight:600;font-size:12.5px;color:var(--green-deep);margin-bottom:7px"><i class="fas fa-clipboard-list" style="color:var(--green)"></i> Recommandations</div>
      <ul style="margin:0;padding-left:18px;font-size:12.5px;color:var(--ink-soft);line-height:1.7">${res.reco.map(r => `<li>${r}</li>`).join('')}</ul></div>
    <button class="btn btn-ghost" style="width:100%;justify-content:center;margin-top:12px" onclick="resetInsp()"><i class="fas fa-rotate"></i> Analyser un autre panneau</button>`;
}
function resetInsp() { $('#inspResult').innerHTML = ''; $('#inspDrop').style.display = 'block'; $('#inspFile').value = ''; }

/* ============================================================
   UI util
   ============================================================ */
function toggleWin(w) {
  const el = w === 'chat' ? $('#chatWin') : $('#inspWin');
  el.classList.toggle('open');
}
function openSettings() { $('#settingsModal').classList.add('open'); }
function closeSettings() { $('#settingsModal').classList.remove('open'); }
function saveSettings() {
  settings.api = $('#apiUrl').value.trim(); settings.key = $('#anthKey').value.trim();
  localStorage.setItem('durasia_api', settings.api); localStorage.setItem('durasia_key', settings.key);
  closeSettings(); toast('Réglages enregistrés');
}
function toast(msg) { $('#toastMsg').textContent = msg; $('#toast').classList.add('show'); setTimeout(() => $('#toast').classList.remove('show'), 2600); }
function revealOnScroll() {
  const io = new IntersectionObserver((es) => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: .08 });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));
}

// build sun arc once DOM ready
document.addEventListener('DOMContentLoaded', buildArcSvg);
