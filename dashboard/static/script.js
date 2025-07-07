let heartCtx = document.getElementById("heartChart").getContext("2d");
let spo2Ctx = document.getElementById("spo2Chart").getContext("2d");
let tempCtx = document.getElementById("tempChart").getContext("2d");

// Check if FontAwesome is loaded and provide fallbacks
function checkFontAwesome() {
  const testIcon = document.createElement('i');
  testIcon.className = 'fa-solid fa-heart';
  testIcon.style.position = 'absolute';
  testIcon.style.left = '-9999px';
  document.body.appendChild(testIcon);
  
  const isLoaded = window.getComputedStyle(testIcon, ':before').content !== 'none';
  document.body.removeChild(testIcon);
  
  if (!isLoaded) {
    console.log('FontAwesome not loaded, using fallback icons');
    // Add fallback class to body
    document.body.classList.add('fa-fallback');
  }
}

// Run FontAwesome check when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  checkFontAwesome();
  
  // Also check for chat input
  const chatInput = document.getElementById('chat-input');
  if (chatInput) {
    chatInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        sendChatMessage();
      }
    });
  }
});

let heartChart = new Chart(heartCtx, {
  type: "line",
  data: { labels: [], datasets: [] },
  options: { 
    responsive: true, 
    plugins: { 
      title: { 
        display: true, 
        text: "Heart Rate Trends",
        color: '#ffffff'
      },
      legend: {
        labels: {
          color: '#ffffff'
        }
      }
    },
    scales: {
      y: {
        ticks: { color: '#ffffff' },
        grid: { color: 'rgba(255,255,255,0.1)' }
      },
      x: {
        ticks: { color: '#ffffff' },
        grid: { color: 'rgba(255,255,255,0.1)' }
      }
    }
  }
});

let spo2Chart = new Chart(spo2Ctx, {
  type: "line",
  data: { labels: [], datasets: [] },
  options: { 
    responsive: true, 
    plugins: { 
      title: { 
        display: true, 
        text: "SpO₂ Trends",
        color: '#ffffff'
      },
      legend: {
        labels: {
          color: '#ffffff'
        }
      }
    },
    scales: {
      y: {
        ticks: { color: '#ffffff' },
        grid: { color: 'rgba(255,255,255,0.1)' }
      },
      x: {
        ticks: { color: '#ffffff' },
        grid: { color: 'rgba(255,255,255,0.1)' }
      }
    }
  }
});

let tempChart = new Chart(tempCtx, {
  type: "line",
  data: { labels: [], datasets: [] },
  options: { 
    responsive: true, 
    plugins: { 
      title: { 
        display: true, 
        text: "Temperature Trends",
        color: '#ffffff'
      },
      legend: {
        labels: {
          color: '#ffffff'
        }
      }
    },
    scales: {
      y: {
        ticks: { color: '#ffffff' },
        grid: { color: 'rgba(255,255,255,0.1)' }
      },
      x: {
        ticks: { color: '#ffffff' },
        grid: { color: 'rgba(255,255,255,0.1)' }
      }
    }
  }
});

const colors = ["#ff4444", "#00ff88", "#ffaa00", "#4444ff", "#ff44ff"];

function getRiskLevel(vital) {
  if (vital.heart_rate > 140 || vital.spo2 < 90 || vital.temperature > 39) {
    return "critical";
  } else if (vital.heart_rate > 120 || vital.spo2 < 92 || vital.temperature > 38) {
    return "warning";
  } else {
    return "normal";
  }
}

function getHeartbeatSpeed(heartRate) {
  // Convert BPM to animation duration (60 BPM = 1 second)
  const duration = 60 / heartRate;
  return Math.max(0.3, Math.min(2, duration)); // Clamp between 0.3s and 2s
}

function drawECG(canvas, bpm, color) {
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  // ECG waveform points (normalized, 0-1)
  // P QRS T
  const points = [
    [0.00, 0.5], [0.05, 0.48], [0.10, 0.52], // P
    [0.15, 0.5], [0.18, 0.7], [0.20, 0.1], [0.22, 0.9], [0.24, 0.5], // QRS
    [0.30, 0.55], [0.40, 0.45], [0.50, 0.5], // T
    [1.00, 0.5]
  ];

  // Animate by shifting horizontally
  const now = Date.now();
  const period = 60000 / bpm; // ms per beat
  const offset = ((now % period) / period) * w;

  ctx.save();
  ctx.translate(-offset, 0);
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.beginPath();
  for (let rep = 0; rep < 2; rep++) { // repeat for seamless scroll
    for (let i = 0; i < points.length; i++) {
      const [px, py] = points[i];
      const x = px * w + rep * w;
      const y = py * h;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
  }
  ctx.stroke();
  ctx.restore();
}

let allVitals = [];
let allPatientNames = [];
let selectedPatient = null;
let currentPatientData = {};

function updatePatientDropdown() {
  const dropdown = document.getElementById('patient-dropdown');
  dropdown.innerHTML = '';
  allPatientNames.forEach(name => {
    const option = document.createElement('option');
    option.value = name;
    option.textContent = name;
    dropdown.appendChild(option);
  });
  if (selectedPatient && allPatientNames.includes(selectedPatient)) {
    dropdown.value = selectedPatient;
  }
}

// Chat System Functions
let chatVisible = false;
let chatMessages = [];

function toggleChat() {
  const chatContainer = document.getElementById('chat-container');
  chatVisible = !chatVisible;
  
  if (chatVisible) {
    chatContainer.style.display = 'flex';
    // Add some sample messages
    if (chatMessages.length === 0) {
      addChatMessage('staff', 'Dr. Smith', 'Patient John Smith showing elevated heart rate. Anyone available?');
      addChatMessage('user', 'You', 'I can check on him. What are his current vitals?');
      addChatMessage('staff', 'Dr. Smith', 'HR: 145, SpO2: 88, Temp: 38.2. Concerned about the trend.');
      addChatMessage('user', 'You', 'I\'ll review his history and check for any recent changes.');
    }
  } else {
    chatContainer.style.display = 'none';
  }
}

function sendChatMessage() {
  const input = document.getElementById('chat-input');
  const message = input.value.trim();
  
  if (message) {
    addChatMessage('user', 'You', message);
    input.value = '';
    
    // Simulate staff response
    setTimeout(() => {
      const responses = [
        'Understood, I\'ll monitor the situation.',
        'Thanks for the update. I\'ll check the patient records.',
        'Noted. I\'ll alert the attending physician.',
        'I can see the trend in the dashboard. Will investigate further.',
        'Patient vitals are being tracked. Will update you shortly.'
      ];
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      addChatMessage('staff', 'Dr. Johnson', randomResponse);
    }, 1000 + Math.random() * 2000);
  }
}

function addChatMessage(type, sender, text) {
  const messagesContainer = document.getElementById('chat-messages');
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${type}`;
  
  const now = new Date();
  const timeString = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
  
  messageDiv.innerHTML = `
    <span class="message-time">${timeString}</span>
    <span class="message-text">${text}</span>
  `;
  
  messagesContainer.appendChild(messageDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
  
  // Store message
  chatMessages.push({
    type: type,
    sender: sender,
    text: text,
    timestamp: now
  });
  
  // Auto-hide system messages after 5 seconds
  if (type === 'system') {
    setTimeout(() => {
      messageDiv.style.opacity = '0.5';
    }, 5000);
  }
}

// Handle Enter key in chat input
document.addEventListener('DOMContentLoaded', function() {
  const chatInput = document.getElementById('chat-input');
  if (chatInput) {
    chatInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        sendChatMessage();
      }
    });
  }
});

// Add emergency chat notifications
function addEmergencyChatMessage(patientName, vitalType, value) {
  const message = `🚨 EMERGENCY: ${patientName} - ${vitalType}: ${value}. Immediate attention required!`;
  addChatMessage('system', 'System', message);
  
  // Make chat visible if it's hidden
  if (!chatVisible) {
    toggleChat();
  }
}

// Enhanced alert system with chat integration
function showAlertBanner(criticalPatients) {
  const banner = document.getElementById('alert-banner');
  if (criticalPatients.length === 0) {
    banner.style.display = 'none';
    banner.innerHTML = '';
    return;
  }
  
  const names = criticalPatients.map(p => `<b>${p.name}</b>`).join(', ');
  banner.innerHTML = `
    <i class='fa-solid fa-triangle-exclamation'></i>
    <span>Critical Alert: ${names} require immediate attention!</span>
    <button class='alert-close' onclick='this.parentElement.style.display="none";' title='Dismiss'>&times;</button>
  `;
  banner.style.display = 'flex';
  
  // Add emergency messages to chat
  criticalPatients.forEach(patient => {
    if (patient.heart_rate > 140) {
      addEmergencyChatMessage(patient.name, 'Heart Rate', patient.heart_rate + ' BPM');
    }
    if (patient.spo2 < 90) {
      addEmergencyChatMessage(patient.name, 'SpO2', patient.spo2 + '%');
    }
    if (patient.temperature > 39) {
      addEmergencyChatMessage(patient.name, 'Temperature', patient.temperature + '°C');
    }
  });
  
  // Play alert sound
  if (!window.__alertSound) {
    window.__alertSound = new Audio('https://cdn.pixabay.com/audio/2022/07/26/audio_124bfa4c7b.mp3');
    window.__alertSound.volume = 0.2;
  }
  window.__alertSound.currentTime = 0;
  window.__alertSound.play();
}

function openPatientModal(patientName, patientData) {
  currentPatientData = patientData;
  const modal = document.getElementById('patient-modal');
  const nameEl = document.getElementById('modal-patient-name');
  const ageEl = document.getElementById('modal-patient-age');
  const genderEl = document.getElementById('modal-patient-gender');
  const conditionEl = document.getElementById('modal-patient-condition');
  
  nameEl.textContent = patientName;
  ageEl.textContent = patientData.age || '--';
  genderEl.textContent = patientData.gender || '--';
  conditionEl.textContent = patientData.condition || '--';
  
  // Load saved notes
  const savedNotes = localStorage.getItem(`patient_notes_${patientName}`) || '';
  document.getElementById('patient-notes-text').value = savedNotes;
  
  // Create mini charts for patient history
  createPatientHistoryCharts(patientData.vitals);
  
  // Load ML prediction
  loadPatientPrediction(patientName);
  
  modal.style.display = 'block';
}

function closePatientModal() {
  document.getElementById('patient-modal').style.display = 'none';
}

function savePatientNotes() {
  const notes = document.getElementById('patient-notes-text').value;
  const patientName = document.getElementById('modal-patient-name').textContent;
  localStorage.setItem(`patient_notes_${patientName}`, notes);
  
  // Show save confirmation
  const btn = document.querySelector('.save-notes-btn');
  const originalText = btn.textContent;
  btn.textContent = 'Saved!';
  btn.style.background = 'linear-gradient(90deg, #00ff88, #00b4d8)';
  setTimeout(() => {
    btn.textContent = originalText;
    btn.style.background = 'linear-gradient(90deg, #3a86ff, #00b4d8)';
  }, 2000);
}

function createPatientHistoryCharts(vitals) {
  const labels = vitals.map(v => v.timestamp);
  const heartData = vitals.map(v => v.heart_rate);
  const spo2Data = vitals.map(v => v.spo2);
  const tempData = vitals.map(v => v.temperature);
  
  // Heart Rate Chart
  const heartCtx = document.getElementById('modal-heart-chart').getContext('2d');
  new Chart(heartCtx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Heart Rate',
        data: heartData,
        borderColor: '#ff4444',
        backgroundColor: 'rgba(255,68,68,0.1)',
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: { display: true, text: 'Heart Rate', color: '#fff' },
        legend: { display: false }
      },
      scales: {
        y: { ticks: { color: '#fff' } },
        x: { ticks: { color: '#fff' } }
      }
    }
  });
  
  // SpO2 Chart
  const spo2Ctx = document.getElementById('modal-spo2-chart').getContext('2d');
  new Chart(spo2Ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'SpO2',
        data: spo2Data,
        borderColor: '#00b4d8',
        backgroundColor: 'rgba(0,180,216,0.1)',
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: { display: true, text: 'SpO2', color: '#fff' },
        legend: { display: false }
      },
      scales: {
        y: { ticks: { color: '#fff' } },
        x: { ticks: { color: '#fff' } }
      }
    }
  });
  
  // Temperature Chart
  const tempCtx = document.getElementById('modal-temp-chart').getContext('2d');
  new Chart(tempCtx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Temperature',
        data: tempData,
        borderColor: '#ffaa00',
        backgroundColor: 'rgba(255,170,0,0.1)',
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: { display: true, text: 'Temperature', color: '#fff' },
        legend: { display: false }
      },
      scales: {
        y: { ticks: { color: '#fff' } },
        x: { ticks: { color: '#fff' } }
      }
    }
  });
}

function createMiniChart(canvasId, data, color, label) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: Array(data.length).fill(''),
      datasets: [{
        label: label,
        data: data,
        borderColor: color,
        backgroundColor: color + '20',
        borderWidth: 2,
        fill: false,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(0,0,0,0.8)',
          titleColor: '#fff',
          bodyColor: '#fff'
        }
      },
      scales: {
        x: { display: false },
        y: { display: false }
      },
      interaction: {
        intersect: false,
        mode: 'index'
      }
    }
  });
}

function updatePatientCards(vitals) {
  const container = document.getElementById("patient-container");
  container.innerHTML = "";
  
  // Group vitals by patient name
  const patients = {};
  vitals.forEach(v => {
    if (!patients[v.name]) {
      patients[v.name] = [];
    }
    patients[v.name].push(v);
  });
  
  allPatientNames = Object.keys(patients);
  updatePatientDropdown();
  let toShow = allPatientNames;
  if (selectedPatient && patients[selectedPatient]) {
    toShow = [selectedPatient];
  }
  
  toShow.forEach((patientName, idx) => {
    const patientVitals = patients[patientName];
    const latestVital = patientVitals[patientVitals.length - 1];
    const riskLevel = getRiskLevel(latestVital);
    const heartbeatSpeed = getHeartbeatSpeed(latestVital.heart_rate);
    const color = riskLevel === 'critical' ? '#ff4444' : riskLevel === 'warning' ? '#ffaa00' : '#00ff88';
    
    // Get recent data for mini charts (last 10 readings)
    const recentVitals = patientVitals.slice(-10);
    const heartData = recentVitals.map(v => v.heart_rate);
    const spo2Data = recentVitals.map(v => v.spo2);
    const tempData = recentVitals.map(v => v.temperature);
    
    const card = document.createElement('div');
    card.className = `patient-card ${riskLevel}`;
    card.style.cursor = 'pointer';
    card.onclick = () => {
      // Show alert banner only for critical patients
      if (riskLevel === 'critical') {
        showAlertBanner([latestVital]);
        // Add emergency message to chat
        addEmergencyChatMessage(patientName, 'Critical Patient Clicked', `HR: ${latestVital.heart_rate}, SpO2: ${latestVital.spo2}, Temp: ${latestVital.temperature}`);
      }
      
      openPatientModal(patientName, {
        vitals: patientVitals,
        age: Math.floor(Math.random() * 50) + 20, // Mock data
        gender: Math.random() > 0.5 ? 'Male' : 'Female',
        condition: 'Stable'
      });
    };
    
    card.innerHTML = `
      <div class="patient-name">👤 ${patientName}</div>
      <div class="heart-rate-display ${riskLevel}">
        ❤️ ${latestVital.heart_rate} BPM
      </div>
      <div class="heartbeat-meter">
        <canvas class="ecg-canvas" width="320" height="60" style="width:100%;height:60px;"></canvas>
      </div>
      <div class="vitals-grid">
        <div class="vital-item">
          <div class="vital-label">🩸 SpO₂</div>
          <div class="vital-value">${latestVital.spo2}%</div>
          <div class="mini-chart">
            <canvas id="spo2-mini-${idx}" width="120" height="40"></canvas>
          </div>
        </div>
        <div class="vital-item">
          <div class="vital-label">🌡 Temperature</div>
          <div class="vital-value">${latestVital.temperature}°C</div>
          <div class="mini-chart">
            <canvas id="temp-mini-${idx}" width="120" height="40"></canvas>
          </div>
        </div>
      </div>
      <div class="timestamp">📅 ${latestVital.timestamp}</div>
    `;
    container.appendChild(card);
    
    // Draw ECG and mini charts
    setTimeout(() => {
      const ecgCanvas = card.querySelector('.ecg-canvas');
      drawECG(ecgCanvas, latestVital.heart_rate, color);
      
      // Create mini charts
      createMiniChart(`spo2-mini-${idx}`, spo2Data, '#00b4d8', 'SpO2');
      createMiniChart(`temp-mini-${idx}`, tempData, '#ffaa00', 'Temperature');
    }, 0);
  });
  
  // Removed automatic critical patient detection - alerts only show when clicking critical patients
}

function filterPatientsBySearch() {
  const search = document.getElementById('patient-search').value.trim().toLowerCase();
  if (!search) {
    selectedPatient = null;
  } else {
    const found = allPatientNames.find(name => name.toLowerCase().includes(search));
    selectedPatient = found || null;
  }
  updatePatientCards(allVitals);
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('patient-search').addEventListener('input', filterPatientsBySearch);
  document.getElementById('patient-dropdown').addEventListener('change', e => {
    selectedPatient = e.target.value;
    updatePatientCards(allVitals);
  });
});

function updateCharts(vitals) {
  const timeLabels = vitals.map(v => v.timestamp);
  const patients = [...new Set(vitals.map(v => v.name))];

  heartChart.data.labels = timeLabels;
  spo2Chart.data.labels = timeLabels;
  tempChart.data.labels = timeLabels;

  heartChart.data.datasets = [];
  spo2Chart.data.datasets = [];
  tempChart.data.datasets = [];

  patients.forEach((name, index) => {
    const patientData = vitals.filter(v => v.name === name);
    const color = colors[index % colors.length];

    heartChart.data.datasets.push({
      label: name,
      data: patientData.map(v => v.heart_rate),
      borderColor: color,
      backgroundColor: color + '20',
      fill: false,
      tension: 0.4
    });
    spo2Chart.data.datasets.push({
      label: name,
      data: patientData.map(v => v.spo2),
      borderColor: color,
      backgroundColor: color + '20',
      fill: false,
      tension: 0.4
    });
    tempChart.data.datasets.push({
      label: name,
      data: patientData.map(v => v.temperature),
      borderColor: color,
      backgroundColor: color + '20',
      fill: false,
      tension: 0.4
    });
  });

  heartChart.update();
  spo2Chart.update();
  tempChart.update();
}

// Statistics Dashboard Functions
let statsData = {
  totalPatients: 0,
  criticalPatients: 0,
  warningPatients: 0,
  normalPatients: 0,
  aiPredictions: 0,
  totalAlerts: 0
};

function updateStatistics(vitals) {
  if (!vitals || vitals.length === 0) return;
  
  // Count patients by status
  const patientStatus = {};
  let criticalCount = 0;
  let warningCount = 0;
  let normalCount = 0;
  
  vitals.forEach(vital => {
    const riskLevel = getRiskLevel(vital);
    if (!patientStatus[vital.name]) {
      patientStatus[vital.name] = riskLevel;
      
      switch(riskLevel) {
        case 'critical':
          criticalCount++;
          break;
        case 'warning':
          warningCount++;
          break;
        case 'normal':
          normalCount++;
          break;
      }
    }
  });
  
  // Update stats
  statsData = {
    totalPatients: Object.keys(patientStatus).length,
    criticalPatients: criticalCount,
    warningPatients: warningCount,
    normalPatients: normalCount,
    aiPredictions: Math.floor(Math.random() * 50) + 20, // Simulated AI predictions
    totalAlerts: criticalCount + warningCount
  };
  
  // Update UI
  document.getElementById('total-patients').textContent = statsData.totalPatients;
  document.getElementById('critical-patients').textContent = statsData.criticalPatients;
  document.getElementById('warning-patients').textContent = statsData.warningPatients;
  document.getElementById('normal-patients').textContent = statsData.normalPatients;
  document.getElementById('ai-predictions').textContent = statsData.aiPredictions;
  document.getElementById('total-alerts').textContent = statsData.totalAlerts;
  
  // Add animation to changed values
  animateStatValue('total-patients');
  animateStatValue('critical-patients');
  animateStatValue('warning-patients');
  animateStatValue('normal-patients');
}

function animateStatValue(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.style.transform = 'scale(1.1)';
    element.style.color = '#ffc107';
    setTimeout(() => {
      element.style.transform = 'scale(1)';
      element.style.color = '#fff';
    }, 300);
  }
}

function refreshStats() {
  // Simulate refreshing statistics
  const refreshBtn = document.querySelector('.stats-refresh-btn');
  refreshBtn.style.transform = 'rotate(360deg)';
  
  setTimeout(() => {
    refreshBtn.style.transform = 'rotate(0deg)';
    // Update with current data
    if (allVitals.length > 0) {
      updateStatistics(allVitals);
    }
  }, 500);
}

// Enhanced fetchVitals function to include statistics
function fetchVitals() {
  fetch('/vitals')
    .then(response => response.json())
    .then(data => {
      allVitals = data;
      allPatientNames = [...new Set(data.map(vital => vital.name))];
      
      // Update statistics
      updateStatistics(data);
      
      // Update patient cards
      updatePatientCards(data);
      
      // Update charts
      updateCharts(data);
      
      // Update patient dropdown
      updatePatientDropdown();
      
      // Remove automatic alert banner - only show when clicking critical patients
      // const criticalPatients = data.filter(vital => getRiskLevel(vital) === 'critical');
      // showAlertBanner(criticalPatients);
    })
    .catch(error => {
      console.error('Error fetching vitals:', error);
    });
}

setInterval(fetchVitals, 3000);
fetchVitals();

// Animate ECGs
setInterval(() => {
  document.querySelectorAll('.ecg-canvas').forEach(canvas => {
    const card = canvas.closest('.patient-card');
    const bpmText = card.querySelector('.heart-rate-display').textContent.match(/(\d+)/);
    const bpm = bpmText ? parseInt(bpmText[1]) : 70;
    const riskLevel = card.classList.contains('critical') ? 'critical' : card.classList.contains('warning') ? 'warning' : 'normal';
    const color = riskLevel === 'critical' ? '#ff4444' : riskLevel === 'warning' ? '#ffaa00' : '#00ff88';
    drawECG(canvas, bpm, color);
  });
}, 30);

function openAddPatientModal() {
  document.getElementById('add-patient-modal').style.display = 'block';
  // Reset form
  document.getElementById('add-patient-form').reset();
}

function closeAddPatientModal() {
  document.getElementById('add-patient-modal').style.display = 'none';
}

function addNewPatient(event) {
  event.preventDefault();
  
  const formData = {
    name: document.getElementById('patient-name').value,
    age: parseInt(document.getElementById('patient-age').value),
    gender: document.getElementById('patient-gender').value,
    condition: document.getElementById('patient-condition').value,
    notes: document.getElementById('patient-notes').value
  };
  
  // Disable submit button
  const submitBtn = document.querySelector('.submit-btn');
  const originalText = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Adding...';
  
  fetch('/add-patient', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(formData)
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Show success message
      submitBtn.innerHTML = '<i class="fa-solid fa-check"></i> Added!';
      submitBtn.style.background = 'linear-gradient(90deg, #00ff88, #00b4d8)';
      
      // Close modal and refresh data with delay to ensure database commit
      setTimeout(() => {
        closeAddPatientModal();
        // Force refresh by clearing cache and refetching
        allVitals = [];
        allPatientNames = [];
        selectedPatient = null;
        fetchVitals(); // Refresh the dashboard
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        submitBtn.style.background = 'linear-gradient(90deg, #3a86ff, #00b4d8)';
      }, 2000); // Increased delay to 2 seconds
      
      // Show success alert
      showSuccessMessage(data.message);
    } else {
      throw new Error(data.error || 'Failed to add patient');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalText;
    showErrorMessage('Failed to add patient: ' + error.message);
  });
}

function showSuccessMessage(message) {
  // Create a temporary success banner
  const banner = document.createElement('div');
  banner.className = 'alert-banner';
  banner.style.background = 'linear-gradient(90deg, #00ff88 0%, #00b4d8 100%)';
  banner.innerHTML = `
    <i class="fa-solid fa-check-circle"></i>
    <span>${message}</span>
  `;
  document.body.insertBefore(banner, document.getElementById('alert-banner').nextSibling);
  
  setTimeout(() => {
    banner.remove();
  }, 3000);
}

function showErrorMessage(message) {
  // Create a temporary error banner
  const banner = document.createElement('div');
  banner.className = 'alert-banner';
  banner.style.background = 'linear-gradient(90deg, #ff4444 0%, #ff8800 100%)';
  banner.innerHTML = `
    <i class="fa-solid fa-exclamation-triangle"></i>
    <span>${message}</span>
  `;
  document.body.insertBefore(banner, document.getElementById('alert-banner').nextSibling);
  
  setTimeout(() => {
    banner.remove();
  }, 5000);
}

function manualRefresh() {
  // Clear all cached data
  allVitals = [];
  allPatientNames = [];
  selectedPatient = null;
  
  // Show loading state
  const refreshBtn = document.getElementById('refresh-btn');
  const originalHTML = refreshBtn.innerHTML;
  refreshBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
  refreshBtn.disabled = true;
  
  // Fetch fresh data
  fetchVitals();
  
  // Reset button after a short delay
  setTimeout(() => {
    refreshBtn.innerHTML = originalHTML;
    refreshBtn.disabled = false;
  }, 1000);
}

function trainMLModel() {
  const btn = document.getElementById('train-model-btn');
  const originalText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Training...';
  
  fetch('/train-model')
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        btn.innerHTML = '<i class="fa-solid fa-check"></i> Trained!';
        btn.style.background = 'linear-gradient(90deg, #00ff88, #00b4d8)';
        showSuccessMessage('AI model trained successfully!');
        
        setTimeout(() => {
          btn.innerHTML = originalText;
          btn.style.background = 'linear-gradient(90deg, #ff6b6b, #ff8e53)';
          btn.disabled = false;
        }, 2000);
      } else {
        throw new Error(data.message || 'Training failed');
      }
    })
    .catch(error => {
      console.error('Error training model:', error);
      btn.disabled = false;
      btn.innerHTML = originalText;
      showErrorMessage('Failed to train model: ' + error.message);
    });
}

function loadPatientPrediction(patientName) {
  const predictionContent = document.getElementById('prediction-content');
  predictionContent.innerHTML = '<div class="prediction-loading"><i class="fa-solid fa-spinner fa-spin"></i> Analyzing patient data...</div>';
  
  fetch(`/predict-risk/${encodeURIComponent(patientName)}`)
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        predictionContent.innerHTML = `<div class="prediction-item insight-alert"><p>${data.error}</p></div>`;
        return;
      }
      
      const prediction = data.prediction;
      const insights = data.insights;
      
      let riskClass = 'low';
      if (prediction.risk_level === 'High Risk') riskClass = 'high';
      else if (prediction.risk_level === 'Anomaly Detected') riskClass = 'anomaly';
      
      let html = `
        <div class="prediction-content">
          <div class="risk-level ${riskClass}">${prediction.risk_level}</div>
          <div class="prediction-item">
            <h4>Confidence Level</h4>
            <p>${(prediction.confidence * 100).toFixed(1)}% confident</p>
            <div class="confidence-bar">
              <div class="confidence-fill" style="width: ${prediction.confidence * 100}%"></div>
            </div>
          </div>
      `;
      
      if (prediction.risk_probability > 0) {
        html += `
          <div class="prediction-item">
            <h4>Risk Probability</h4>
            <p>${(prediction.risk_probability * 100).toFixed(1)}% chance of deterioration</p>
          </div>
        `;
      }
      
      if (insights.alerts && insights.alerts.length > 0) {
        html += '<div class="prediction-item insight-alert"><h4>⚠️ Alerts</h4>';
        insights.alerts.forEach(alert => {
          html += `<p>• ${alert}</p>`;
        });
        html += '</div>';
      }
      
      if (insights.recommendations && insights.recommendations.length > 0) {
        html += '<div class="prediction-item insight-recommendation"><h4>💡 Recommendations</h4>';
        insights.recommendations.forEach(rec => {
          html += `<p>• ${rec}</p>`;
        });
        html += '</div>';
      }
      
      if (insights.trends) {
        html += '<div class="prediction-item"><h4>📈 Trends</h4>';
        Object.entries(insights.trends).forEach(([vital, trend]) => {
          html += `<p>• ${vital.replace('_', ' ').toUpperCase()}: ${trend}</p>`;
        });
        html += '</div>';
      }
      
      html += '</div>';
      predictionContent.innerHTML = html;
    })
    .catch(error => {
      console.error('Error loading prediction:', error);
      predictionContent.innerHTML = '<div class="prediction-item insight-alert"><p>Failed to load prediction</p></div>';
    });
}

// AI Predictions Dashboard
function showAIPredictions() {
  // Create a modal to show all AI predictions
  const modal = document.createElement('div');
  modal.className = 'patient-modal';
  modal.style.display = 'flex';
  
  modal.innerHTML = `
    <div class="modal-content" style="max-width: 900px;">
      <div class="modal-header">
        <h2><i class="fa-solid fa-robot"></i> AI Predictions Dashboard</h2>
        <button class="modal-close" onclick="this.parentElement.parentElement.parentElement.remove()">&times;</button>
      </div>
      <div class="modal-body">
        <div class="ai-summary">
          <div class="ai-stat">
            <span class="ai-stat-label">Model Status:</span>
            <span class="ai-stat-value" id="model-status">Checking...</span>
          </div>
          <div class="ai-stat">
            <span class="ai-stat-label">Total Predictions:</span>
            <span class="ai-stat-value" id="total-predictions">0</span>
          </div>
          <div class="ai-stat">
            <span class="ai-stat-label">High Risk Patients:</span>
            <span class="ai-stat-value" id="high-risk-count">0</span>
          </div>
        </div>
        
        <div class="ai-predictions-list" id="ai-predictions-list">
          <div class="prediction-loading">
            <i class="fa-solid fa-spinner fa-spin"></i> Loading AI predictions...
          </div>
        </div>
        
        <div class="ai-actions">
          <button class="train-model-btn" onclick="trainMLModel()">
            <i class="fa-solid fa-brain"></i> Retrain Model
          </button>
          <button class="refresh-btn" onclick="refreshAIPredictions()">
            <i class="fa-solid fa-rotate"></i> Refresh Predictions
          </button>
        </div>
      </div>
    </div>
  `;
  
  document.body.appendChild(modal);
  
  // Load AI predictions
  loadAllAIPredictions();
}

function loadAllAIPredictions() {
  const predictionsList = document.getElementById('ai-predictions-list');
  const modelStatus = document.getElementById('model-status');
  const totalPredictions = document.getElementById('total-predictions');
  const highRiskCount = document.getElementById('high-risk-count');
  
  // Check if we have patient data
  if (!allVitals || allVitals.length === 0) {
    predictionsList.innerHTML = '<div class="no-data">No patient data available for AI predictions.</div>';
    return;
  }
  
  // Get unique patients
  const patients = [...new Set(allVitals.map(v => v.name))];
  let highRiskPatients = 0;
  let totalPreds = 0;
  
  predictionsList.innerHTML = '';
  
  patients.forEach((patientName, index) => {
    const patientVitals = allVitals.filter(v => v.name === patientName);
    const latestVital = patientVitals[patientVitals.length - 1];
    
    // Create prediction card
    const predictionCard = document.createElement('div');
    predictionCard.className = 'prediction-card';
    predictionCard.innerHTML = `
      <div class="prediction-header">
        <h4><i class="fa-solid fa-user"></i> ${patientName}</h4>
        <span class="prediction-status loading">Analyzing...</span>
      </div>
      <div class="prediction-details">
        <div class="vital-summary">
          <span>HR: ${latestVital.heart_rate} BPM</span>
          <span>SpO2: ${latestVital.spo2}%</span>
          <span>Temp: ${latestVital.temperature}°C</span>
        </div>
        <div class="prediction-content" id="prediction-${index}">
          <div class="prediction-loading">
            <i class="fa-solid fa-spinner fa-spin"></i> Running AI analysis...
          </div>
        </div>
      </div>
    `;
    
    predictionsList.appendChild(predictionCard);
    
    // Simulate AI prediction (in real app, this would call the ML model)
    setTimeout(() => {
      const riskLevel = getRiskLevel(latestVital);
      const confidence = Math.random() * 0.4 + 0.6; // 60-100% confidence
      const isAnomaly = Math.random() > 0.7; // 30% chance of anomaly
      
      let predictionText = '';
      let statusClass = '';
      
      if (riskLevel === 'critical' || isAnomaly) {
        predictionText = 'High Risk';
        statusClass = 'high-risk';
        highRiskPatients++;
      } else if (riskLevel === 'warning') {
        predictionText = 'Medium Risk';
        statusClass = 'medium-risk';
      } else {
        predictionText = 'Low Risk';
        statusClass = 'low-risk';
      }
      
      // Update prediction card
      const statusElement = predictionCard.querySelector('.prediction-status');
      const contentElement = predictionCard.querySelector('.prediction-content');
      
      statusElement.className = `prediction-status ${statusClass}`;
      statusElement.textContent = predictionText;
      
      contentElement.innerHTML = `
        <div class="prediction-item">
          <div class="prediction-item">
            <h4>Risk Assessment</h4>
            <p>${predictionText}</p>
          </div>
          <div class="prediction-item">
            <h4>Confidence</h4>
            <p>${(confidence * 100).toFixed(1)}%</p>
          </div>
          <div class="prediction-item">
            <h4>Anomaly Detection</h4>
            <p>${isAnomaly ? 'Anomaly Detected' : 'Normal Pattern'}</p>
          </div>
        </div>
      `;
      
      totalPreds++;
      
      // Update summary stats
      if (totalPreds === patients.length) {
        modelStatus.textContent = 'Active';
        modelStatus.className = 'ai-stat-value active';
        totalPredictions.textContent = totalPreds;
        highRiskCount.textContent = highRiskPatients;
      }
    }, 500 + index * 200); // Stagger the predictions
  });
}

function refreshAIPredictions() {
  loadAllAIPredictions();
}
