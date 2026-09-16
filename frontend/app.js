// CATALYST RISK - Frontend Logic

const API_URL = "http://localhost:8000/api";

const $ = id => document.getElementById(id);
const qa = sel => document.querySelectorAll(sel);
const money = v => '$' + Math.round(v).toLocaleString();

let charts = {};
let simData = null;
let currentConfig = null;

Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = 'Inter, sans-serif';
Chart.defaults.scale.grid.color = 'rgba(255,255,255,0.03)';
Chart.defaults.scale.grid.borderColor = 'transparent';

function initCharts() {
  const ctxLoss = $('chart-loss').getContext('2d');
  charts.loss = new Chart(ctxLoss, {
    type: 'bar',
    data: { labels: [], datasets: [{ label: 'Loss Frequency', data: [], backgroundColor: '#0ea5e9', categoryPercentage: 1.0, barPercentage: 0.95 }] },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { x: { display: false }, y: { beginAtZero: true } }
    }
  });

  const ctxEp = $('chart-ep').getContext('2d');
  charts.ep = new Chart(ctxEp, {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'Loss', data: [], borderColor: '#ef4444', backgroundColor: 'rgba(239, 68, 68, 0.1)', fill: true, tension: 0.2, pointRadius: 0 }] },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { x: { display: false }, y: { beginAtZero: true } }
    }
  });
}

$('inp-sims').addEventListener('input', e => { $('out-sims').textContent = parseInt(e.target.value).toLocaleString(); });

function renderMapMarkers(avgLosses) {
  const mapEl = $('geo-map');
  const detailPanel = $('map-detail-panel');
  qa('.map-marker').forEach(m => m.remove());
  
  // Real geographic regions from Python data generator
  const hubs = [
    { name: "Miami", lat: 25.7617, lon: -80.1918 },
    { name: "Los Angeles", lat: 34.0522, lon: -118.2437 },
    { name: "Houston", lat: 29.7604, lon: -95.3698 }
  ];
  
  // Map drawing bounds (pseudo projection across US)
  const minLon = -125, maxLon = -65;
  const minLat = 24, maxLat = 50;
  
  for(let i=0; i<Math.min(500, avgLosses.length); i++) {
    const hub = hubs[i % 3];
    const lat = hub.lat + (Math.random() - 0.5) * 1.5;
    const lon = hub.lon + (Math.random() - 0.5) * 1.5;
    
    // Normalize to percentage for CSS
    const x = ((lon - minLon) / (maxLon - minLon)) * 100;
    const y = 100 - (((lat - minLat) / (maxLat - minLat)) * 100);
    
    const loss = avgLosses[i];
    
    // Stylistic relative sizing/coloring
    let cls = loss > 15000 ? 'high' : loss > 5000 ? 'med' : 'low';
    
    const marker = document.createElement('div');
    marker.className = `map-marker ${cls}`;
    marker.style.left = x + '%';
    marker.style.top = y + '%';
    
    marker.onmouseover = () => {
      detailPanel.innerHTML = `
        <div style="background: var(--bg-main); border: 1px solid var(--border-strong); padding: 12px; border-radius: var(--radius-sm);">
          <div style="font-size: 10px; color: var(--text-dim); text-transform: uppercase;">Asset ID</div>
          <div style="font-size: 13px; font-weight: 600; margin-top: 4px;">LOC-${String(i+1).padStart(5,'0')}</div>
        </div>
        <div style="background: var(--bg-main); border: 1px solid var(--border-strong); padding: 12px; border-radius: var(--radius-sm);">
          <div style="font-size: 10px; color: var(--text-dim); text-transform: uppercase;">Expected Loss</div>
          <div style="font-size: 13px; font-weight: 600; margin-top: 4px; font-family: var(--font-mono); color: var(--text-main);">${money(loss)}</div>
        </div>
      `;
    };
    
    mapEl.appendChild(marker);
  }
}

async function triggerSimulation() {
  const btn = document.querySelector('.btn-run');
  btn.style.opacity = '0.5';
  btn.textContent = 'Running API...';
  
  $('loaderOverlay').classList.add('active');
  $('loaderProgress').style.width = '30%';
  $('loaderStep').textContent = "Calling Python REST API...";
  
  currentConfig = {
    num_sims: parseInt($('inp-sims').value),
    hazard_type: $('inp-hazard').value,
    severity: $('inp-severity').value,
    seed: parseInt($('inp-seed').value)
  };
  
  try {
    const response = await fetch(`${API_URL}/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(currentConfig)
    });
    
    if(!response.ok) throw new Error("API Execution Failed");
    
    simData = await response.json();
    $('loaderProgress').style.width = '90%';
    $('loaderStep').textContent = "Rendering Metrics...";
    
    updateDashboard(simData);
    
    // Enable download buttons
    $('btn-audit').removeAttribute('disabled');
    $('btn-prop-loss').removeAttribute('disabled');
    
  } catch(e) {
    console.error(e);
    alert("API Error. Ensure FastAPI backend is running.");
  } finally {
    $('loaderProgress').style.width = '100%';
    setTimeout(() => {
      $('loaderOverlay').classList.remove('active');
      btn.style.opacity = '1';
      btn.textContent = '▶ Run Simulation';
    }, 500);
  }
}

function updateDashboard(data) {
  $('kpi-tiv').textContent = money(data.totalTiv);
  $('kpi-aal').textContent = money(data.aal);
  $('kpi-100').textContent = money(data.pml100);
  $('kpi-250').textContent = money(data.pml250);
  
  $('topLastRun').textContent = `LAST RUN: ${new Date().toLocaleTimeString()}`;
  $('dist-meta').textContent = `${data.sims.toLocaleString()} Events`;
  
  $('s-api-time').textContent = `${(data.apiTime * 1000).toFixed(0)} ms`;
  $('s-exec-time').textContent = `${(data.execTime * 1000).toFixed(0)} ms`;
  $('s-aal').textContent = money(data.aal);
  
  if (data.losses && data.losses.length > 0) {
      const buckets = Array(50).fill(0);
      const maxLoss = Math.max(...data.losses);
      data.losses.forEach(l => {
          const idx = Math.min(49, Math.floor((l / maxLoss) * 50));
          buckets[idx]++;
      });
      charts.loss.data.labels = buckets.map((_, i) => money((i/50)*maxLoss));
      charts.loss.data.datasets[0].data = buckets;
      charts.loss.update();
      
      const sorted = [...data.losses].sort((a,b) => b-a);
      const epData = [];
      const epLabels = [];
      for(let i=1; i<=100; i++) {
          const idx = Math.floor(data.sims * (i/1000)) || 1;
          if(sorted[idx]) {
            epData.push(sorted[idx]);
            epLabels.push(1000/i);
          }
      }
      charts.ep.data.labels = epLabels;
      charts.ep.data.datasets[0].data = epData;
      charts.ep.update();
  }
  
  if (data.avgPropLoss) {
      renderMapMarkers(data.avgPropLoss);
  }
}

// Download Handlers
function downloadExposure() {
    window.open(`${API_URL}/download/exposure`, '_blank');
}

function downloadAuditTrail() {
    if(!simData) return;
    const auditData = {
        config: currentConfig,
        run_id: simData.run_id,
        timestamp: new Date().toISOString(),
        metrics: {
            aal: simData.aal,
            pml100: simData.pml100,
            pml250: simData.pml250,
            simulations: simData.sims,
            totalTiv: simData.totalTiv,
            backend_execution_time_sec: simData.execTime
        }
    };
    const blob = new Blob([JSON.stringify(auditData, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `CATALYST_Audit_Run_${simData.run_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

function downloadPropertyLosses() {
    if(!simData || !simData.avgPropLoss) return;
    let csvContent = "location_id,expected_annual_loss_usd\n";
    
    simData.avgPropLoss.forEach((loss, i) => {
        csvContent += `LOC-${String(i+1).padStart(5,'0')},${loss.toFixed(2)}\n`;
    });
    
    const blob = new Blob([csvContent], {type: 'text/csv;charset=utf-8;'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `CATALYST_Expected_Losses_${simData.run_id}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}

qa('.nav-item').forEach(btn => {
  btn.addEventListener('click', () => {
    qa('.nav-item').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    const target = btn.getAttribute('data-target');
    qa('.page-view').forEach(p => p.classList.add('hidden'));
    $(target).classList.remove('hidden');
    
    $('currentCrumb').textContent = btn.querySelector('.nav-label').textContent;
  });
});

window.onload = () => {
  initCharts();
};
