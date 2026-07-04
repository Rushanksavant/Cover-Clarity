/* ──────────────────────────────────────────────
   TOAST SYSTEM
────────────────────────────────────────────── */
function toast(msg, type = 'info', duration = 3500) {
  const icons = { info: 'ℹ️', success: '✅', error: '❌', warn: '⚠️' };
  const rack = document.getElementById('toast-rack');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<span class="toast-icon">${
    icons[type] || 'ℹ️'
  }</span><span>${msg}</span>`;
  rack.appendChild(el);
  setTimeout(() => {
    el.classList.add('fade-out');
    setTimeout(() => el.remove(), 320);
  }, duration);
}

/* ──────────────────────────────────────────────
   ANIMATED KNOWLEDGE GRAPH (Landing hero)
────────────────────────────────────────────── */
(function buildKG() {
  const svg = document.getElementById('kg-svg');
  if (!svg) return;
  const W = window.innerWidth,
    H = window.innerHeight;
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);

  const NODES = [
    { x: W * 0.18, y: H * 0.22, r: 10, label: 'Annual Max', pulse: 5200 },
    { x: W * 0.72, y: H * 0.15, r: 8, label: 'Deductible', pulse: 4800 },
    { x: W * 0.88, y: H * 0.45, r: 12, label: 'Crown', pulse: 6100 },
    { x: W * 0.78, y: H * 0.78, r: 7, label: 'D2740', pulse: 4400 },
    { x: W * 0.12, y: H * 0.65, r: 9, label: 'Root Canal', pulse: 5500 },
    { x: W * 0.35, y: H * 0.85, r: 6, label: 'Waiting Pd', pulse: 4000 },
    { x: W * 0.55, y: H * 0.55, r: 14, label: 'Policy', pulse: 7000 },
    { x: W * 0.42, y: H * 0.25, r: 8, label: 'Exclusion', pulse: 4600 },
    { x: W * 0.25, y: H * 0.45, r: 7, label: 'Copay', pulse: 5100 },
    { x: W * 0.65, y: H * 0.35, r: 9, label: 'Network', pulse: 4900 },
  ];
  const EDGES = [
    [0, 6],
    [1, 6],
    [2, 6],
    [3, 6],
    [4, 6],
    [5, 6],
    [7, 6],
    [8, 6],
    [9, 6],
    [0, 8],
    [1, 9],
    [2, 3],
    [4, 5],
    [7, 1],
    [9, 2],
  ];

  // Defs
  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
  const lg = document.createElementNS(
    'http://www.w3.org/2000/svg',
    'radialGradient',
  );
  lg.setAttribute('id', 'kgGrad');
  [
    ['0%', 'rgba(0,194,224,0.7)'],
    ['100%', 'rgba(14,165,160,0.1)'],
  ].forEach(([o, c]) => {
    const s = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    s.setAttribute('offset', o);
    s.setAttribute('stop-color', c);
    lg.appendChild(s);
  });
  defs.appendChild(lg);
  svg.appendChild(defs);

  // Edges
  EDGES.forEach(([a, b]) => {
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    const na = NODES[a],
      nb = NODES[b];
    line.setAttribute('x1', na.x);
    line.setAttribute('y1', na.y);
    line.setAttribute('x2', nb.x);
    line.setAttribute('y2', nb.y);
    line.setAttribute('stroke', 'rgba(0,194,224,0.12)');
    line.setAttribute('stroke-width', '1');
    svg.appendChild(line);
  });

  // Nodes
  NODES.forEach((n, i) => {
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    // Pulse ring
    const ring = document.createElementNS(
      'http://www.w3.org/2000/svg',
      'circle',
    );
    ring.setAttribute('cx', n.x);
    ring.setAttribute('cy', n.y);
    ring.setAttribute('r', n.r);
    ring.setAttribute('fill', 'none');
    ring.setAttribute('stroke', 'rgba(0,194,224,0.35)');
    ring.setAttribute('stroke-width', '1');
    const animR = document.createElementNS(
      'http://www.w3.org/2000/svg',
      'animate',
    );
    animR.setAttribute('attributeName', 'r');
    animR.setAttribute('values', `${n.r};${n.r * 2.5};${n.r}`);
    animR.setAttribute('dur', `${n.pulse}ms`);
    animR.setAttribute('repeatCount', 'indefinite');
    const animO = document.createElementNS(
      'http://www.w3.org/2000/svg',
      'animate',
    );
    animO.setAttribute('attributeName', 'opacity');
    animO.setAttribute('values', '0.5;0;0.5');
    animO.setAttribute('dur', `${n.pulse}ms`);
    animO.setAttribute('repeatCount', 'indefinite');
    ring.appendChild(animR);
    ring.appendChild(animO);
    g.appendChild(ring);
    // Core dot
    const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    c.setAttribute('cx', n.x);
    c.setAttribute('cy', n.y);
    c.setAttribute('r', n.r);
    c.setAttribute('fill', i === 6 ? 'url(#kgGrad)' : 'rgba(0,194,224,0.15)');
    c.setAttribute(
      'stroke',
      i === 6 ? 'rgba(0,194,224,0.8)' : 'rgba(0,194,224,0.4)',
    );
    c.setAttribute('stroke-width', i === 6 ? '1.5' : '1');
    g.appendChild(c);
    // Float animation
    const animCY = document.createElementNS(
      'http://www.w3.org/2000/svg',
      'animate',
    );
    animCY.setAttribute('attributeName', 'cy');
    const drift = i % 2 === 0 ? 6 : -6;
    animCY.setAttribute('values', `${n.y};${n.y + drift};${n.y}`);
    animCY.setAttribute('dur', `${n.pulse * 1.4}ms`);
    animCY.setAttribute('repeatCount', 'indefinite');
    c.appendChild(animCY);
    svg.appendChild(g);
  });
})();

/* ──────────────────────────────────────────────
   MEDICAL HISTORY
────────────────────────────────────────────── */
let medicalHistoryCache = {}; // { session_id: data | null }

function openMedicalHistoryModal() {
  document.getElementById('mh-modal').classList.add('open');
  const saved = currentSession
    ? medicalHistoryCache[currentSession.session_id]
    : null;
  if (saved) populateMHForm(saved);
}

function closeMedicalHistoryModal() {
  document.getElementById('mh-modal').classList.remove('open');
}

function skipMedicalHistory() {
  closeMedicalHistoryModal();
  toast(
    'You can add patient info anytime using the header badge',
    'info',
    3500,
  );
}

// ── Conditions ──
function addCondition(data = {}) {
  const list = document.getElementById('conditions-list');
  const id = Date.now();
  const div = document.createElement('div');
  div.className = 'mh-list-item';
  div.dataset.id = id;
  div.innerHTML = `
    <div class="mh-field">
      <label>Condition Name</label>
      <input class="mh-input cond-name" type="text" placeholder="e.g. Diabetes" value="${escRaw(
        data.condition_name || '',
      )}"/>
    </div>
    <div class="mh-field" style="max-width:130px">
      <label>Severity</label>
      <select class="mh-input cond-severity">
        <option ${data.severity === 'Mild' ? 'selected' : ''}>Mild</option>
        <option ${
          !data.severity || data.severity === 'Moderate' ? 'selected' : ''
        }>Moderate</option>
        <option ${data.severity === 'Severe' ? 'selected' : ''}>Severe</option>
      </select>
    </div>
    <div class="mh-field">
      <label>Notes (optional)</label>
      <input class="mh-input cond-notes" type="text" placeholder="Any notes…" value="${escRaw(
        data.notes || '',
      )}"/>
    </div>
    <button class="mh-remove-btn" onclick="this.closest('.mh-list-item').remove()" title="Remove">✕</button>`;
  list.appendChild(div);
}

// ── Medications ──
function addMedication(data = {}) {
  const list = document.getElementById('medications-list');
  const div = document.createElement('div');
  div.className = 'mh-list-item';
  div.innerHTML = `
    <div class="mh-field">
      <label>Medication Name</label>
      <input class="mh-input med-name" type="text" placeholder="e.g. Metformin" value="${escRaw(
        data.name || '',
      )}"/>
    </div>
    <div class="mh-field" style="max-width:110px">
      <label>Dosage</label>
      <input class="mh-input med-dosage" type="text" placeholder="500mg" value="${escRaw(
        data.dosage || '',
      )}"/>
    </div>
    <div class="mh-field" style="max-width:130px">
      <label>Frequency</label>
      <input class="mh-input med-freq" type="text" placeholder="Twice daily" value="${escRaw(
        data.frequency || '',
      )}"/>
    </div>
    <button class="mh-remove-btn" onclick="this.closest('.mh-list-item').remove()" title="Remove">✕</button>`;
  list.appendChild(div);
}

// ── Tag inputs (allergies, procedures) ──
function handleTagInput(e, wrapId, inputId) {
  if (e.key === 'Enter' || e.key === ',') {
    e.preventDefault();
    const input = document.getElementById(inputId);
    const val = input.value.replace(/,/g, '').trim();
    if (val) addTag(wrapId, inputId, val);
    input.value = '';
  } else if (e.key === 'Backspace' && !e.target.value) {
    const wrap = document.getElementById(wrapId);
    const tags = wrap.querySelectorAll('.tag');
    if (tags.length) tags[tags.length - 1].remove();
  }
}

function addTag(wrapId, inputId, text) {
  const wrap = document.getElementById(wrapId);
  const input = document.getElementById(inputId);
  const tag = document.createElement('span');
  tag.className = 'tag';
  tag.innerHTML = `${escRaw(
    text,
  )}<button class="tag-remove" onclick="this.parentElement.remove()">✕</button>`;
  wrap.insertBefore(tag, input);
}

function getTagValues(wrapId) {
  return [...document.querySelectorAll(`#${wrapId} .tag`)]
    .map((t) => t.textContent.replace('✕', '').trim())
    .filter(Boolean);
}

// ── Populate form from saved data ──
function populateMHForm(data) {
  document.getElementById('mh-age').value = data.age || '';
  document.getElementById('mh-patient-id').value = data.patient_id || '';

  document.getElementById('conditions-list').innerHTML = '';
  (data.chronic_conditions || []).forEach((c) => addCondition(c));

  document.getElementById('medications-list').innerHTML = '';
  (data.current_medications || []).forEach((m) => addMedication(m));

  // Clear and repopulate tags
  const aWrap = document.getElementById('allergies-wrap');
  const aInput = document.getElementById('allergy-input');
  [...aWrap.querySelectorAll('.tag')].forEach((t) => t.remove());
  (data.allergies || []).forEach((a) =>
    addTag('allergies-wrap', 'allergy-input', a),
  );

  const pWrap = document.getElementById('procedures-wrap');
  const pInput = document.getElementById('procedure-input');
  [...pWrap.querySelectorAll('.tag')].forEach((t) => t.remove());
  (data.past_dental_procedures || []).forEach((p) =>
    addTag('procedures-wrap', 'procedure-input', p),
  );
}

// ── Build payload from form ──
function buildMHPayload() {
  const age = parseInt(document.getElementById('mh-age').value);
  if (!age || age < 1 || age > 120) return null;

  const conditions = [
    ...document.querySelectorAll('#conditions-list .mh-list-item'),
  ]
    .map((row) => ({
      condition_name: row.querySelector('.cond-name').value.trim(),
      severity: row.querySelector('.cond-severity').value,
      notes: row.querySelector('.cond-notes').value.trim() || null,
    }))
    .filter((c) => c.condition_name);

  const medications = [
    ...document.querySelectorAll('#medications-list .mh-list-item'),
  ]
    .map((row) => ({
      name: row.querySelector('.med-name').value.trim(),
      dosage: row.querySelector('.med-dosage').value.trim(),
      frequency: row.querySelector('.med-freq').value.trim(),
    }))
    .filter((m) => m.name);

  return {
    patient_id:
      document.getElementById('mh-patient-id').value.trim() ||
      `patient_${Date.now()}`,
    age,
    chronic_conditions: conditions,
    current_medications: medications,
    allergies: getTagValues('allergies-wrap'),
    past_dental_procedures: getTagValues('procedures-wrap'),
  };
}

// ── Save ──
async function saveMedicalHistory() {
  const payload = buildMHPayload();
  if (!payload) {
    toast('Please enter a valid age before saving', 'warn');
    document.getElementById('mh-age').focus();
    return;
  }
  if (!currentSession) {
    toast('No active session selected', 'error');
    return;
  }

  const btn = document.getElementById('mh-save-btn');
  btn.disabled = true;
  btn.textContent = 'Saving…';

  try {
    await api(
      'POST',
      `/sessions/${currentSession.session_id}/medical-history`,
      payload,
    );
    medicalHistoryCache[currentSession.session_id] = payload;
    updateMHBadge(true);
    closeMedicalHistoryModal();
    toast('Patient info saved — you can now start chatting!', 'success');
  } catch (e) {
    toast('Failed to save: ' + e.message, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Save & Start Chatting';
  }
}

// ── Update header badge + input block ──
function updateMHBadge(hasMH) {
  const badge = document.getElementById('mh-status-badge');
  const banner = document.getElementById('input-blocked-banner');
  const sendBtn = document.getElementById('send-btn');
  const queryInput = document.getElementById('query-input');

  badge.style.display = '';
  if (hasMH) {
    badge.className = 'mh-status-badge saved';
    badge.textContent = '✅ Patient Info';
    banner.style.display = 'none';
    sendBtn.disabled = false;
    queryInput.disabled = false;
    queryInput.placeholder = 'Ask about any dental procedure or coverage…';
  } else {
    badge.className = 'mh-status-badge missing';
    badge.textContent = '⚠️ Add Patient Info';
    banner.style.display = 'block';
    sendBtn.disabled = true;
    queryInput.disabled = true;
    queryInput.placeholder = 'Fill in patient info above to start chatting…';
  }
}

// ── Fetch MH on session load ──
async function fetchMedicalHistory(session_id) {
  if (medicalHistoryCache[session_id] !== undefined) {
    updateMHBadge(!!medicalHistoryCache[session_id]);
    return;
  }
  try {
    const data = await api('GET', `/sessions/${session_id}/medical-history`);
    const hasMH = data && Object.keys(data).length > 0;
    medicalHistoryCache[session_id] = hasMH ? data : null;
    updateMHBadge(hasMH);
    if (!hasMH) {
      // Auto-open form for new sessions
      setTimeout(() => openMedicalHistoryModal(), 400);
    }
  } catch {
    medicalHistoryCache[session_id] = null;
    updateMHBadge(false);
  }
}

/* ──────────────────────────────────────────────
   MARKDOWN RENDERER (lightweight, no deps)
────────────────────────────────────────────── */
function renderMarkdown(text) {
  let html = text
    // Escape HTML first
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // Code blocks (``` ... ```)
    .replace(
      /```(\w*)\n?([\s\S]*?)```/g,
      (_, lang, code) =>
        `<pre><code class="lang-${lang}">${code.trim()}</code></pre>`,
    )
    // Inline code
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Headers
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Bold + italic
    .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Blockquote
    .replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>')
    // Unordered lists (- or *)
    .replace(/^[\-\*] (.+)$/gm, '<li>$1</li>')
    // Ordered lists
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // Wrap consecutive <li> in <ul>
    .replace(/((<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>')
    // Links
    .replace(
      /\[([^\]]+)\]\(([^)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener">$1</a>',
    )
    // Line breaks → paragraphs (double newline)
    .replace(/\n\n+/g, '</p><p>')
    // Single newline
    .replace(/\n/g, '<br>');

  // Wrap in paragraph if not already block-level
  if (!/^<(h[1-6]|ul|ol|pre|blockquote|p)/.test(html)) {
    html = `<p>${html}</p>`;
  }

  return html;
}

/* ──────────────────────────────────────────────
   APP STATE
────────────────────────────────────────────── */
const historyCache = {};
const API = ''; // same-origin; change to 'http://localhost:8000' for local dev
let token = null,
  currentUser = null,
  currentSession = null,
  sessions = [];

/* ──────────────────────────────────────────────
   HELPERS
────────────────────────────────────────────── */
async function api(method, path, body) {
  const res = await fetch(API + path, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

function fmtDate(iso) {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}
function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 140) + 'px';
}
function fillExample(el) {
  if (!currentSession) {
    openAuth('login');
    return;
  }
  document.getElementById('query-input').value = el.textContent;
  sendChat();
}

/* ──────────────────────────────────────────────
   AUTH
────────────────────────────────────────────── */
let authMode = 'login';

function openAuth(mode) {
  authMode = mode;
  switchTab(mode);
  document.getElementById('auth-overlay').classList.add('open');
  setTimeout(() => document.getElementById('auth-username').focus(), 100);
}
function closeAuth() {
  document.getElementById('auth-overlay').classList.remove('open');
  document.getElementById('auth-err').textContent = '';
}
document.getElementById('auth-overlay').addEventListener('click', (e) => {
  if (e.target === document.getElementById('auth-overlay')) closeAuth();
});

function switchTab(mode) {
  authMode = mode;
  document
    .querySelectorAll('.tab')
    .forEach((t, i) =>
      t.classList.toggle('active', (i === 0) === (mode === 'login')),
    );
  const isLogin = mode === 'login';
  document.getElementById('auth-btn').textContent = isLogin
    ? 'Sign In'
    : 'Create Account';
  document.getElementById('auth-heading').textContent = isLogin
    ? 'Welcome back'
    : 'Create account';
  document.getElementById('auth-sub').textContent = isLogin
    ? 'Sign in to check your dental claim coverage'
    : 'Get started with Cover-Clarity today';
  document.getElementById('auth-err').textContent = '';
}

async function submitAuth() {
  const username = document.getElementById('auth-username').value.trim();
  const password = document.getElementById('auth-password').value;
  const errEl = document.getElementById('auth-err');
  errEl.textContent = '';
  if (!username || !password) {
    errEl.textContent = 'Username and password are required';
    return;
  }
  const btn = document.getElementById('auth-btn');
  btn.disabled = true;
  btn.textContent = 'Please wait…';
  try {
    const endpoint = authMode === 'login' ? '/auth/login' : '/auth/signup';
    const data = await api('POST', endpoint, { username, password });
    token = data.token;
    currentUser = username;
    sessions =
      data.sessions ||
      (data.default_session_id
        ? [
            {
              session_id: data.default_session_id,
              label: 'Default Session',
              created_at: new Date().toISOString(),
            },
          ]
        : []);
    closeAuth();
    enterApp();
    toast(`Welcome, @${username}! 👋`, 'success');
  } catch (e) {
    errEl.textContent = e.message;
    toast(e.message, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = authMode === 'login' ? 'Sign In' : 'Create Account';
  }
}

/* ──────────────────────────────────────────────
   APP LIFECYCLE
────────────────────────────────────────────── */
function enterApp() {
  document.getElementById('landing').style.display = 'none';
  document.getElementById('app').classList.add('visible');
  document.getElementById('username-label').textContent = '@' + currentUser;
  document.getElementById('user-avatar').textContent =
    currentUser[0].toUpperCase();
  renderSessions();
  if (sessions.length) loadSession(sessions[0]);
}

function logout() {
  token = null;
  currentUser = null;
  currentSession = null;
  sessions = [];
  medicalHistoryCache = {};
  document.getElementById('mh-status-badge').style.display = 'none';
  document.getElementById('input-blocked-banner').style.display = 'none';
  document.getElementById('app').classList.remove('visible');
  document.getElementById('landing').style.display = 'flex';
  document.getElementById('auth-password').value = '';
  resetMessages();
  toast('Signed out successfully', 'info', 2500);
}

/* ──────────────────────────────────────────────
   MOBILE SIDEBAR
────────────────────────────────────────────── */
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('sidebar-overlay').classList.toggle('open');
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebar-overlay').classList.remove('open');
}

/* ──────────────────────────────────────────────
   SESSIONS
────────────────────────────────────────────── */
function renderSessions() {
  const list = document.getElementById('session-list');
  list.innerHTML = sessions
    .map(
      (s) => `
<div class="session-item ${
        currentSession?.session_id === s.session_id ? 'active' : ''
      }"
   onclick='loadSession(${JSON.stringify(s).replace(/"/g, '&quot;')})'>
<div class="s-label">${escRaw(s.label)}</div>
<div class="s-date">${fmtDate(s.created_at)}</div>
</div>`,
    )
    .join('');
}
function escRaw(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

async function createSession() {
  const label = prompt('Session name (optional):') || '';
  try {
    const s = await api('POST', '/sessions', { label });
    sessions.unshift(s);
    renderSessions();
    loadSession(s);
    toast('New session created', 'success', 2000);
  } catch (e) {
    toast(e.message, 'error');
  }
  closeSidebar();
}

async function loadSession(session) {
  currentSession = session;
  closeSidebar();
  document.getElementById('chat-title').textContent = session.label;
  document.getElementById('session-badge').style.display = '';
  renderSessions();

  // Check medical history for this session (gates chat input)
  fetchMedicalHistory(session.session_id);
  // Show Bronze Plan badge
  const planBadge = document.getElementById('plan-badge');
  if (planBadge) planBadge.style.display = '';

  if (historyCache[session.session_id]) {
    renderHistory(historyCache[session.session_id]);
    return;
  }
  resetMessages(
    '<div class="empty-state"><div class="empty-icon">⏳</div><p>Loading history…</p></div>',
  );
  try {
    const history = await api('GET', `/sessions/${session.session_id}/history`);
    historyCache[session.session_id] = history;
    renderHistory(history);
  } catch (e) {
    resetMessages(
      `<div class="empty-state"><p style="color:var(--danger)">${e.message}</p></div>`,
    );
    toast(e.message, 'error');
  }
}

function resetMessages(html) {
  const inner = document.getElementById('messages-inner');
  inner.innerHTML =
    html ||
    `<div class="empty-state" id="empty-state">
<div class="empty-icon">🦷</div>
<p>Ask about any dental procedure, code, or clause in your policy.</p>
<div class="empty-examples">
<div class="example-chip" onclick="fillExample(this)">Will my plan cover a crown on tooth #14?</div>
<div class="example-chip" onclick="fillExample(this)">Is there a waiting period for root canals?</div>
<div class="example-chip" onclick="fillExample(this)">How much of my annual maximum is remaining?</div>
</div>
  </div>`;
}

function renderHistory(history) {
  const inner = document.getElementById('messages-inner');
  if (!history.length) {
    inner.innerHTML = `<div class="empty-state"><div class="empty-icon">✨</div><p>No messages yet. Ask your first claim question!</p></div>`;
    return;
  }
  inner.innerHTML = '';
  history.forEach((turn) =>
    appendTurn(
      turn.question,
      turn.answer,
      turn.time,
      turn.used_session_context_ids || [],
      true,
    ),
  );
  scrollToBottom();
}

/* ──────────────────────────────────────────────
   CHAT
────────────────────────────────────────────── */
async function sendChat() {
  if (!currentSession) {
    toast('Select or create a session first', 'warn');
    return;
  }
  if (!medicalHistoryCache[currentSession.session_id]) {
    toast('Please fill in the Patient Medical History first', 'warn');
    openMedicalHistoryModal();
    return;
  }
  const input = document.getElementById('query-input');
  const query = input.value.trim();
  if (!query) return;
  input.value = '';
  input.style.height = 'auto';
  document.getElementById('send-btn').disabled = true;
  const inner = document.getElementById('messages-inner');
  inner.querySelector('.empty-state')?.remove();

  // User bubble
  const userRow = document.createElement('div');
  userRow.className = 'msg-row user';
  userRow.innerHTML = `<div class="msg-bubble user">${escRaw(
    query,
  )}<div class="msg-meta">${new Date().toLocaleTimeString()}</div></div>`;
  inner.appendChild(userRow);
  scrollToBottom();

  // Thinking indicator
  const thinkingRow = document.createElement('div');
  thinkingRow.className = 'thinking-row';
  thinkingRow.innerHTML = `
<div class="agent-avatar">AI</div>
<div class="thinking-content">
<div class="thinking-label">Scanning policy knowledge graph…</div>
<div class="pulse-dots"><span></span><span></span><span></span></div>
<div class="shimmer-lines"><div class="shimmer"></div><div class="shimmer"></div><div class="shimmer"></div></div>
</div>`;
  inner.appendChild(thinkingRow);
  scrollToBottom();

  try {
    const result = await api(
      'POST',
      `/sessions/${currentSession.session_id}/chat`,
      { query },
    );
    thinkingRow.remove();
    if (!historyCache[currentSession.session_id])
      historyCache[currentSession.session_id] = [];
    historyCache[currentSession.session_id].push({
      question: query,
      answer: result.answer,
      time: new Date().toISOString(),
      used_session_context_ids: result.trace_ids || [],
    });
    appendTurn(
      null,
      result.answer,
      new Date().toISOString(),
      result.trace_ids || [],
      false,
    );
  } catch (e) {
    thinkingRow.remove();
    const errRow = document.createElement('div');
    errRow.className = 'msg-row agent';
    errRow.innerHTML = `<div class="agent-avatar">AI</div><div class="msg-bubble agent" style="color:var(--danger)">${e.message}</div>`;
    inner.appendChild(errRow);
    toast('Failed to get a response — ' + e.message, 'error');
  } finally {
    document.getElementById('send-btn').disabled = false;
    scrollToBottom();
  }
}

function appendTurn(question, answer, time, traceIds, showQuestion) {
  const inner = document.getElementById('messages-inner');
  if (showQuestion && question) {
    const uRow = document.createElement('div');
    uRow.className = 'msg-row user';
    uRow.innerHTML = `<div class="msg-bubble user">${escRaw(
      question,
    )}<div class="msg-meta">${fmtDate(time)}</div></div>`;
    inner.appendChild(uRow);
  }
  const aRow = document.createElement('div');
  aRow.className = 'msg-row agent';
  const traceHtml = traceIds.length
    ? `<button class="trace-btn" onclick='showGraph(${JSON.stringify(
        traceIds,
      )})'>🔍 View policy trace <span style="opacity:.55">(${
        traceIds.length
      } nodes)</span></button>`
    : '';
  aRow.innerHTML = `
<div class="agent-avatar">AI</div>
<div class="msg-bubble agent">
${renderMarkdown(answer)}
<div class="msg-meta">${fmtDate(time)}</div>
${traceHtml}
</div>`;
  inner.appendChild(aRow);
}

function scrollToBottom() {
  const m = document.getElementById('messages');
  m.scrollTop = m.scrollHeight;
}

/* ──────────────────────────────────────────────
   EXPORT
────────────────────────────────────────────── */
async function exportHistory(fmt) {
  if (!currentSession) {
    toast('Select a session first', 'warn');
    return;
  }
  toast('Preparing PDF export…', 'info', 2000);
  try {
    const res = await fetch(
      `${API}/sessions/${currentSession.session_id}/export/${fmt}`,
      { headers: { Authorization: `Bearer ${token}` } },
    );
    if (!res.ok) throw new Error('Export failed');
    const blob = await res.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `${currentSession.session_id}.${fmt}`;
    a.click();
    toast('PDF downloaded!', 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

/* ──────────────────────────────────────────────
   GRAPH MODAL (D3)
────────────────────────────────────────────── */
function showGraph(ids) {
  document.getElementById('graph-modal').classList.add('open');
  renderGraph(ids);
}
function closeGraph() {
  document.getElementById('graph-modal').classList.remove('open');
}
document.getElementById('graph-modal').addEventListener('click', (e) => {
  if (e.target === document.getElementById('graph-modal')) closeGraph();
});

function renderGraph(ids) {
  const svgEl = document.getElementById('graph-svg');
  const svg = d3.select(svgEl);
  svg.selectAll('*').remove();

  if (!ids || !ids.length) {
    svg
      .append('text')
      .attr('x', '50%')
      .attr('y', '50%')
      .attr('text-anchor', 'middle')
      .attr('fill', '#4d6b8a')
      .text('No graph trace data available.');
    return;
  }

  const W = svgEl.clientWidth || 660,
    H = 330;
  const center = { id: 'answer', type: 'answer' };
  const contextNodes = ids.map((id) => ({
    id,
    shortId: id.slice(0, 8),
    type: 'context',
  }));
  const nodes = [center, ...contextNodes];
  const links = contextNodes.map((n) => ({ source: 'answer', target: n.id }));

  // ── Run simulation fully headless (no DOM ticks) ──
  const sim = d3
    .forceSimulation(nodes)
    .force(
      'link',
      d3
        .forceLink(links)
        .id((d) => d.id)
        .distance(110),
    )
    .force('charge', d3.forceManyBody().strength(-220))
    .force('center', d3.forceCenter(W / 2, H / 2))
    .stop();

  // Tick to convergence upfront — instant, no repaints
  for (let i = 0; i < 300; i++) sim.tick();

  // ── Draw static result ──
  const defs = svg.append('defs');
  const grad = defs.append('radialGradient').attr('id', 'answerGrad');
  grad.append('stop').attr('offset', '0%').attr('stop-color', '#00c2e0');
  grad.append('stop').attr('offset', '100%').attr('stop-color', '#0ea5a0');

  // Glow filter for answer node
  const filter = defs.append('filter').attr('id', 'glow');
  filter
    .append('feGaussianBlur')
    .attr('stdDeviation', '3')
    .attr('result', 'blur');
  const merge = filter.append('feMerge');
  merge.append('feMergeNode').attr('in', 'blur');
  merge.append('feMergeNode').attr('in', 'SourceGraphic');

  const g = svg.append('g');

  // Links
  g.append('g')
    .selectAll('line')
    .data(links)
    .join('line')
    .attr('stroke', 'rgba(0,194,224,0.22)')
    .attr('stroke-width', 1.5)
    .attr('x1', (d) => d.source.x)
    .attr('y1', (d) => d.source.y)
    .attr('x2', (d) => d.target.x)
    .attr('y2', (d) => d.target.y);

  // Node groups
  const node = g
    .append('g')
    .selectAll('g')
    .data(nodes)
    .join('g')
    .attr('transform', (d) => `translate(${d.x},${d.y})`);

  node
    .append('circle')
    .attr('r', (d) => (d.type === 'answer' ? 24 : 14))
    .attr('fill', (d) =>
      d.type === 'answer' ? 'url(#answerGrad)' : 'rgba(0,194,224,0.08)',
    )
    .attr('stroke', (d) =>
      d.type === 'answer' ? 'none' : 'rgba(0,194,224,0.45)',
    )
    .attr('stroke-width', 1.5)
    .attr('filter', (d) => (d.type === 'answer' ? 'url(#glow)' : null));

  node
    .append('text')
    .attr('text-anchor', 'middle')
    .attr('dy', '0.35em')
    .attr('fill', '#ddeaf5')
    .attr('font-size', (d) => (d.type === 'answer' ? '9px' : '8px'))
    .attr('font-family', 'Inter,sans-serif')
    .attr('pointer-events', 'none')
    .text((d) => (d.type === 'answer' ? 'Answer' : d.shortId + '…'));

  node.append('title').text((d) => d.id);

  // Node count + legend line
  svg
    .append('text')
    .attr('x', W - 10)
    .attr('y', H - 8)
    .attr('text-anchor', 'end')
    .attr('fill', '#4d6b8a')
    .attr('font-size', '9px')
    .attr('font-family', 'Inter,sans-serif')
    .text(`${ids.length} context nodes retrieved from knowledge graph`);
}
