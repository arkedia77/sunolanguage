import { updateGlobal, toggleInArray } from '../state/store.js';

let initialized = false;

export function renderGlobalSettings(container, state, data) {
  const g = state.global;

  if (!initialized) {
    initialized = true;
    container.innerHTML = `
      <div class="panel-section">
        <div class="panel-section-title">Genre</div>
        <div class="search-input">
          <input type="text" id="genre-search" placeholder="Search genres..." />
        </div>
        <div class="chip-group" id="genre-chips"></div>
      </div>

      <div class="panel-section">
        <div class="panel-section-title">Tempo (BPM)</div>
        <div class="range-row">
          <input type="range" id="bpm-slider" min="60" max="200" value="${g.bpm}" />
          <span class="range-value" id="bpm-value">${g.bpm}</span>
        </div>
        <div class="preset-row" id="bpm-presets"></div>
      </div>

      <div class="panel-section">
        <div class="panel-section-title">Key</div>
        <select id="key-select">
          <option value="">— Select Key —</option>
        </select>
      </div>

      <div class="panel-section">
        <div class="panel-section-title">Time Signature</div>
        <div class="radio-group" id="time-sig-group"></div>
      </div>

      <div class="panel-section">
        <div class="panel-section-title">Vocal</div>
        <div class="chip-group" id="vocal-chips"></div>
      </div>

      <div class="panel-section">
        <div class="panel-section-title">Arrangement</div>
        <div class="chip-group" id="arrangement-chips"></div>
      </div>

      <div class="panel-section">
        <div class="panel-section-title">Effects</div>
        <div class="chip-group" id="effects-chips"></div>
      </div>

      <div class="panel-section">
        <div class="panel-section-title">Mood</div>
        <div class="chip-group" id="mood-chips"></div>
      </div>
    `;

    setupGenreChips(container, data);
    setupBpmPresets(container, data);
    setupKeySelect(container, data);
    setupTimeSigGroup(container);
    setupVocalChips(container, data);
    setupArrangementChips(container, data);
    setupEffectsChips(container, data);
    setupMoodChips(container, data);
    setupGenreSearch(container);
  }

  updateActiveStates(container, state, data);
}

function setupGenreChips(container, data) {
  const el = container.querySelector('#genre-chips');
  el.innerHTML = data.genres
    .map(g => `<div class="chip" data-genre="${g.name}">${g.name} <span class="freq">${g.songCount}</span></div>`)
    .join('');
  el.addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    const name = chip.dataset.genre;
    updateGlobal('genre', name);
  });
}

function setupGenreSearch(container) {
  const input = container.querySelector('#genre-search');
  const chips = container.querySelector('#genre-chips');
  input.addEventListener('input', () => {
    const q = input.value.toLowerCase();
    for (const chip of chips.children) {
      chip.style.display = chip.dataset.genre.toLowerCase().includes(q) ? '' : 'none';
    }
  });
}

function setupBpmPresets(container, data) {
  const el = container.querySelector('#bpm-presets');
  const presets = [72, 85, 92, 105, 120, 128, 140];
  el.innerHTML = presets.map(v => `<button class="preset-btn" data-bpm="${v}">${v}</button>`).join('');
  el.addEventListener('click', e => {
    const btn = e.target.closest('.preset-btn');
    if (!btn) return;
    const bpm = parseInt(btn.dataset.bpm);
    updateGlobal('bpm', bpm);
    container.querySelector('#bpm-slider').value = bpm;
    container.querySelector('#bpm-value').textContent = bpm;
  });
  container.querySelector('#bpm-slider').addEventListener('input', e => {
    const bpm = parseInt(e.target.value);
    container.querySelector('#bpm-value').textContent = bpm;
    updateGlobal('bpm', bpm);
  });
}

function setupKeySelect(container, data) {
  const sel = container.querySelector('#key-select');
  for (const k of data.keys) {
    const opt = document.createElement('option');
    opt.value = k.label;
    opt.textContent = `${k.label} (${k.freq})`;
    sel.appendChild(opt);
  }
  sel.addEventListener('change', () => updateGlobal('key', sel.value));
}

function setupTimeSigGroup(container) {
  const el = container.querySelector('#time-sig-group');
  const sigs = ['4/4', '3/4', '6/8'];
  el.innerHTML = sigs.map(s => `<button class="radio-btn" data-sig="${s}">${s}</button>`).join('');
  el.addEventListener('click', e => {
    const btn = e.target.closest('.radio-btn');
    if (!btn) return;
    updateGlobal('timeSignature', btn.dataset.sig);
  });
}

function setupVocalChips(container, data) {
  const el = container.querySelector('#vocal-chips');
  el.innerHTML = data.vocalTypes
    .map(v => `<div class="chip" data-vocal="${v}">${v}</div>`)
    .join('');
  el.addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    toggleInArray('vocalTypes', chip.dataset.vocal);
  });
}

function setupArrangementChips(container, data) {
  const el = container.querySelector('#arrangement-chips');
  el.innerHTML = data.arrangements
    .map(a => `<div class="chip" data-arr="${a}">${a}</div>`)
    .join('');
  el.addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    updateGlobal('arrangement', chip.dataset.arr);
  });
}

function setupEffectsChips(container, data) {
  const el = container.querySelector('#effects-chips');
  const topEffects = data.effects.slice(0, 20);
  el.innerHTML = topEffects
    .map(e => `<div class="chip" data-effect="${e}">${e}</div>`)
    .join('');
  el.addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    toggleInArray('effects', chip.dataset.effect);
  });
}

function setupMoodChips(container, data) {
  const el = container.querySelector('#mood-chips');
  el.innerHTML = data.moods
    .map(m => `<div class="chip" data-mood="${m}">${m}</div>`)
    .join('');
  el.addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    toggleInArray('mood', chip.dataset.mood);
  });
}

function updateActiveStates(container, state, data) {
  const g = state.global;

  for (const chip of container.querySelectorAll('#genre-chips .chip')) {
    chip.classList.toggle('active', chip.dataset.genre === g.genre);
  }
  for (const chip of container.querySelectorAll('#vocal-chips .chip')) {
    chip.classList.toggle('active', g.vocalTypes.includes(chip.dataset.vocal));
  }
  for (const chip of container.querySelectorAll('#arrangement-chips .chip')) {
    chip.classList.toggle('active', chip.dataset.arr === g.arrangement);
  }
  for (const chip of container.querySelectorAll('#effects-chips .chip')) {
    chip.classList.toggle('active', g.effects.includes(chip.dataset.effect));
  }
  for (const chip of container.querySelectorAll('#mood-chips .chip')) {
    chip.classList.toggle('active', g.mood.includes(chip.dataset.mood));
  }
  for (const btn of container.querySelectorAll('#time-sig-group .radio-btn')) {
    btn.classList.toggle('active', btn.dataset.sig === g.timeSignature);
  }

  // Genre recommendations
  const recs = data.genreRecommendations[g.genre];
  if (recs) {
    const recInstruments = new Set(recs.instrument || []);
    for (const chip of container.querySelectorAll('#effects-chips .chip')) {
      const isRec = (recs.effect_electronic || []).some(e =>
        e.toLowerCase().includes(chip.dataset.effect.toLowerCase())
      );
      chip.classList.toggle('recommended', isRec);
    }
  }
}
