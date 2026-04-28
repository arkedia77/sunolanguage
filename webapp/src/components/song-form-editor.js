import {
  addSection, removeSection, setActiveSection, loadPreset,
  addInstrumentToSection, removeInstrumentFromSection,
  updateInstrument, toggleDrum, setSectionVocalDirective,
  moveSectionUp, moveSectionDown, getActiveSection,
} from '../state/store.js';

const SECTION_TYPES = ['Intro', 'Verse', 'Pre-Chorus', 'Chorus', 'Bridge', 'Instrumental', 'Outro'];
const VOCAL_DIRECTIVES = ['instrumental', 'humming', 'spoken word', 'rap', 'belting', 'falsetto', 'whispering', 'ad-libs'];

let prevSectionsJSON = '';
let prevActiveId = null;

export function renderSongForm(container, state, data) {
  const sectionsJSON = JSON.stringify(state.sections.map(s => ({ id: s.id, label: s.label, instCount: s.instruments.length, drums: s.drums.length })));
  const needsFullRender = sectionsJSON !== prevSectionsJSON || state.activeSectionId !== prevActiveId;

  if (!needsFullRender) {
    updateDetailPanel(container, state, data);
    return;
  }

  prevSectionsJSON = sectionsJSON;
  prevActiveId = state.activeSectionId;

  let html = `
    <div class="panel-section">
      <div class="panel-section-title">Song Form</div>
      <div class="form-presets">
        <button class="form-preset-btn" data-preset="standard-pop">Standard Pop</button>
        <button class="form-preset-btn" data-preset="ballad">Ballad</button>
        <button class="form-preset-btn" data-preset="simple">Simple</button>
      </div>
      <div class="section-list">
  `;

  for (const sec of state.sections) {
    const isActive = sec.id === state.activeSectionId;
    const instSummary = sec.instruments.length > 0
      ? `${sec.instruments.length} instrument${sec.instruments.length > 1 ? 's' : ''}`
      : 'no instruments';
    const drumSummary = sec.drums.length > 0 ? `, ${sec.drums.length} drums` : '';
    const vocalSummary = sec.vocalDirective ? `, ${sec.vocalDirective}` : '';

    html += `
      <div class="section-card ${isActive ? 'active' : ''}" data-section-id="${sec.id}">
        <div>
          <div class="section-name">${sec.label}</div>
          <div class="section-summary">${instSummary}${drumSummary}${vocalSummary}</div>
        </div>
        <div style="display:flex;gap:2px;align-items:center;">
          <button class="section-delete" data-move="up" title="Move up">&uarr;</button>
          <button class="section-delete" data-move="down" title="Move down">&darr;</button>
          <button class="section-delete" data-delete="${sec.id}" title="Remove">&times;</button>
        </div>
      </div>
    `;
  }

  html += `
      </div>
      <div class="add-section-bar">
        ${SECTION_TYPES.map(t => `<button class="add-section-btn" data-type="${t}">+ ${t}</button>`).join('')}
      </div>
    </div>
  `;

  html += `<div id="section-detail-area"></div>`;

  container.innerHTML = html;

  container.querySelector('.form-presets').addEventListener('click', e => {
    const btn = e.target.closest('.form-preset-btn');
    if (btn) loadPreset(btn.dataset.preset);
  });

  container.querySelector('.section-list').addEventListener('click', e => {
    const delBtn = e.target.closest('[data-delete]');
    if (delBtn) {
      e.stopPropagation();
      removeSection(parseInt(delBtn.dataset.delete));
      return;
    }
    const moveBtn = e.target.closest('[data-move]');
    if (moveBtn) {
      e.stopPropagation();
      const card = moveBtn.closest('.section-card');
      const id = parseInt(card.dataset.sectionId);
      if (moveBtn.dataset.move === 'up') moveSectionUp(id);
      else moveSectionDown(id);
      return;
    }
    const card = e.target.closest('.section-card');
    if (card) setActiveSection(parseInt(card.dataset.sectionId));
  });

  container.querySelector('.add-section-bar').addEventListener('click', e => {
    const btn = e.target.closest('.add-section-btn');
    if (btn) addSection(btn.dataset.type);
  });

  updateDetailPanel(container, state, data);
}

function updateDetailPanel(container, state, data) {
  const detailArea = container.querySelector('#section-detail-area');
  if (!detailArea) return;

  const section = getActiveSection();
  if (!section) {
    detailArea.innerHTML = state.sections.length === 0
      ? '<div class="empty-state">Add sections above to start building your song structure.</div>'
      : '<div class="empty-state">Click a section to edit its instruments and settings.</div>';
    return;
  }

  const recs = state.global.genre ? (data.genreRecommendations[state.global.genre] || {}) : {};
  const recInstruments = new Set((recs.instrument || []).map(s => s.toLowerCase()));
  const recDrums = new Set((recs.drums || []).map(s => s.toLowerCase()));

  const instrumentOptions = data.instruments.map(inst => {
    const isRec = recInstruments.has(inst.name.toLowerCase());
    return `<option value="${inst.name}" ${isRec ? 'class="recommended"' : ''}>${isRec ? '★ ' : ''}${inst.name} (${inst.count})</option>`;
  }).join('');

  let html = `
    <div class="section-detail">
      <div class="section-detail-title">${section.label}</div>

      <div class="panel-section">
        <div class="panel-section-title">Instruments</div>
        <div id="instrument-rows">
  `;

  for (const inst of section.instruments) {
    const instData = data.instruments.find(i => i.name === inst.name);
    const modifiers = instData ? instData.modifiers.slice(0, 6) : [];
    const patterns = instData ? instData.patterns.slice(0, 5) : [];

    html += `
      <div class="instrument-row" data-inst-id="${inst.id}">
        <select class="inst-select" data-inst-id="${inst.id}">
          <option value="">— Select —</option>
          ${instrumentOptions}
        </select>
        <button class="remove-btn" data-remove-inst="${inst.id}">&times;</button>
      </div>
    `;

    if (inst.name) {
      html += `<div style="padding: 0 8px 8px; display: flex; flex-direction: column; gap: 4px;">`;
      if (modifiers.length > 0) {
        html += `<div class="chip-group" data-modifier-group="${inst.id}">
          ${modifiers.map(m => `<div class="chip ${inst.modifiers.includes(m.label) ? 'active' : ''}" data-mod="${m.label}" data-inst-id="${inst.id}">${m.label}</div>`).join('')}
        </div>`;
      }
      if (patterns.length > 0) {
        html += `<div class="chip-group" data-pattern-group="${inst.id}">
          ${patterns.map(p => `<div class="chip ${inst.pattern === p.label ? 'active' : ''}" data-pattern="${p.label}" data-inst-id="${inst.id}">${p.label}</div>`).join('')}
        </div>`;
      }
      html += `</div>`;
    }
  }

  html += `
        </div>
        <button class="add-instrument-btn" id="add-inst-btn">+ Add Instrument</button>
      </div>

      <div class="panel-section">
        <div class="panel-section-title">Drums</div>
        <div class="chip-group" id="drum-chips">
          ${data.drumComponents.map(d => {
            const isActive = section.drums.includes(d);
            const isRec = recDrums.has(d.toLowerCase());
            return `<div class="chip ${isActive ? 'active' : ''} ${isRec ? 'recommended' : ''}" data-drum="${d}">${d}</div>`;
          }).join('')}
        </div>
      </div>

      <div class="panel-section">
        <div class="panel-section-title">Vocal Directive</div>
        <div class="chip-group" id="vocal-directive-chips">
          ${VOCAL_DIRECTIVES.map(v =>
            `<div class="chip ${section.vocalDirective === v ? 'active' : ''}" data-vdir="${v}">${v}</div>`
          ).join('')}
        </div>
      </div>
    </div>
  `;

  detailArea.innerHTML = html;

  for (const sel of detailArea.querySelectorAll('.inst-select')) {
    const instId = parseInt(sel.dataset.instId);
    const inst = section.instruments.find(i => i.id === instId);
    if (inst) sel.value = inst.name;

    sel.addEventListener('change', () => {
      updateInstrument(section.id, instId, 'name', sel.value);
      updateInstrument(section.id, instId, 'modifiers', []);
      updateInstrument(section.id, instId, 'pattern', '');
    });
  }

  for (const btn of detailArea.querySelectorAll('[data-remove-inst]')) {
    btn.addEventListener('click', () => {
      removeInstrumentFromSection(section.id, parseInt(btn.dataset.removeInst));
    });
  }

  detailArea.querySelector('#add-inst-btn').addEventListener('click', () => {
    addInstrumentToSection(section.id, '');
  });

  for (const chip of detailArea.querySelectorAll('[data-mod]')) {
    chip.addEventListener('click', () => {
      const instId = parseInt(chip.dataset.instId);
      const inst = section.instruments.find(i => i.id === instId);
      if (!inst) return;
      const mod = chip.dataset.mod;
      const mods = [...inst.modifiers];
      const idx = mods.indexOf(mod);
      if (idx === -1) mods.push(mod);
      else mods.splice(idx, 1);
      updateInstrument(section.id, instId, 'modifiers', mods);
    });
  }

  for (const chip of detailArea.querySelectorAll('[data-pattern]')) {
    chip.addEventListener('click', () => {
      const instId = parseInt(chip.dataset.instId);
      const inst = section.instruments.find(i => i.id === instId);
      if (!inst) return;
      const pat = chip.dataset.pattern;
      updateInstrument(section.id, instId, 'pattern', inst.pattern === pat ? '' : pat);
    });
  }

  detailArea.querySelector('#drum-chips').addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (chip) toggleDrum(section.id, chip.dataset.drum);
  });

  detailArea.querySelector('#vocal-directive-chips').addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    const v = chip.dataset.vdir;
    setSectionVocalDirective(section.id, section.vocalDirective === v ? '' : v);
  });
}
