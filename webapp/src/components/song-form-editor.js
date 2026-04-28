import {
  addSection, removeSection, setActiveSection, loadPreset,
  addInstrumentToSection, removeInstrumentFromSection,
  updateInstrument, toggleDrum, setSectionVocalDirective,
  moveSectionUp, moveSectionDown, getActiveSection,
  reorderSections, toggleInstrumentEffect,
  updateGlobal, toggleInArray,
} from '../state/store.js';
import Sortable from 'sortablejs';

const SECTION_TYPES = ['Intro', 'Verse', 'Pre-Chorus', 'Chorus', 'Bridge', 'Instrumental', 'Outro', 'Solo', 'Rap', 'Drop', 'Build', 'Breakdown', 'Dance Break', 'Exposition', 'Development', 'Recapitulation', 'Coda'];
const VOCAL_DIRECTIVES = ['instrumental', 'humming', 'spoken word', 'rap', 'belting', 'falsetto', 'whispering', 'ad-libs'];

let prevSectionsJSON = '';
let prevActiveId = null;
let sortableInstance = null;

export function renderSongForm(container, state, data) {
  const sectionsJSON = JSON.stringify(state.sections.map(s => ({ id: s.id, label: s.label, instCount: s.instruments.length, drums: s.drums.length })));
  const needsFullRender = sectionsJSON !== prevSectionsJSON || state.activeSectionId !== prevActiveId;

  if (!needsFullRender) {
    updateDetailPanel(container, state, data);
    return;
  }

  prevSectionsJSON = sectionsJSON;
  prevActiveId = state.activeSectionId;

  const g = state.global;

  let html = `
    <div class="settings-row">
      <div class="settings-cell">
        <label class="settings-label">BPM</label>
        <div class="range-row compact">
          <input type="range" id="center-bpm-slider" min="60" max="200" value="${g.bpm}" />
          <span class="range-value" id="center-bpm-value">${g.bpm}</span>
        </div>
      </div>
      <div class="settings-cell">
        <label class="settings-label">Key</label>
        <select id="center-key-select" class="compact-select">
          <option value="">—</option>
          ${data.keys.map(k => `<option value="${k.label}" ${k.label === g.key ? 'selected' : ''}>${k.label}</option>`).join('')}
        </select>
      </div>
      <div class="settings-cell">
        <label class="settings-label">Time</label>
        <div class="radio-group compact" id="center-time-sig">
          ${['4/4', '3/4', '6/8'].map(s => `<button class="radio-btn ${s === g.timeSignature ? 'active' : ''}" data-sig="${s}">${s}</button>`).join('')}
        </div>
      </div>
      <div class="settings-cell">
        <label class="settings-label">Vocal</label>
        <div class="chip-group compact" id="center-vocal-chips">
          ${data.vocalTypes.slice(0, 8).map(v => `<div class="chip mini ${g.vocalTypes.includes(v) ? 'active' : ''}" data-vocal="${v}">${v}</div>`).join('')}
        </div>
      </div>
      <div class="settings-cell">
        <label class="settings-label">Arrangement</label>
        <div class="chip-group compact" id="center-arr-chips">
          ${data.arrangements.map(a => `<div class="chip mini ${a === g.arrangement ? 'active' : ''}" data-arr="${a}">${a}</div>`).join('')}
        </div>
      </div>
    </div>

    <div class="settings-row">
      <div class="settings-cell" style="flex:1">
        <label class="settings-label">Effects <span class="label-hint-inline">프로덕션 이펙트 → SP에 반영</span></label>
        <div class="chip-group compact" id="center-effects-chips">
          ${data.effects.slice(0, 16).map(e => `<div class="chip mini ${g.effects.includes(e) ? 'active' : ''}" data-effect="${e}">${e}</div>`).join('')}
        </div>
      </div>
      <div class="settings-cell" style="flex:1">
        <label class="settings-label">Mood <span class="label-hint-inline">곡의 감정/분위기 → SP에 반영</span></label>
        <div class="chip-group compact" id="center-mood-chips">
          ${data.moods.slice(0, 16).map(m => `<div class="chip mini ${g.mood.includes(m) ? 'active' : ''}" data-mood="${m}">${m}</div>`).join('')}
        </div>
      </div>
    </div>

    <div class="panel-section">
      <div class="panel-section-title">Song Form</div>
      <div class="panel-desc">곡의 구조(섹션 순서)를 정합니다. 각 섹션 클릭 → 악기 등장/퇴장 배치 → 브래킷에 반영.</div>
      <div class="form-presets">
        <div class="preset-group">
          <span class="preset-group-label">Pop</span>
          <button class="form-preset-btn" data-preset="standard-pop">Standard</button>
          <button class="form-preset-btn" data-preset="ballad">Ballad</button>
          <button class="form-preset-btn" data-preset="simple">Simple</button>
          <button class="form-preset-btn" data-preset="k-pop">K-Pop</button>
        </div>
        <div class="preset-group">
          <span class="preset-group-label">Rock / EDM</span>
          <button class="form-preset-btn" data-preset="rock">Rock</button>
          <button class="form-preset-btn" data-preset="edm">EDM</button>
          <button class="form-preset-btn" data-preset="blues">Blues</button>
        </div>
        <div class="preset-group">
          <span class="preset-group-label">Classical</span>
          <button class="form-preset-btn" data-preset="sonata">Sonata</button>
          <button class="form-preset-btn" data-preset="rondo">Rondo</button>
          <button class="form-preset-btn" data-preset="aaba">AABA</button>
          <button class="form-preset-btn" data-preset="concerto">Concerto</button>
          <button class="form-preset-btn" data-preset="through-composed">Through</button>
        </div>
      </div>
      <div class="section-list" id="section-list">
  `;

  for (const sec of state.sections) {
    const isActive = sec.id === state.activeSectionId;
    const instSummary = sec.instruments.length > 0
      ? `${sec.instruments.length} inst`
      : 'no instruments';
    const drumSummary = sec.drums.length > 0 ? `, ${sec.drums.length} drums` : '';
    const vocalSummary = sec.vocalDirective ? `, ${sec.vocalDirective}` : '';

    html += `
      <div class="section-card ${isActive ? 'active' : ''}" data-section-id="${sec.id}">
        <div class="drag-handle" title="Drag to reorder">&#x2630;</div>
        <div class="section-info">
          <div class="section-name">${sec.label}</div>
          <div class="section-summary">${instSummary}${drumSummary}${vocalSummary}</div>
        </div>
        <div class="section-actions">
          <button class="section-action-btn" data-move="up" title="Move up">&uarr;</button>
          <button class="section-action-btn" data-move="down" title="Move down">&darr;</button>
          <button class="section-action-btn delete" data-delete="${sec.id}" title="Remove">&times;</button>
        </div>
      </div>
    `;
  }

  html += `
      </div>
      <div class="add-section-bar">
        ${SECTION_TYPES.slice(0, 7).map(t => `<button class="add-section-btn" data-type="${t}">+ ${t}</button>`).join('')}
        <button class="add-section-btn more-toggle" id="more-sections-toggle">More...</button>
      </div>
      <div class="add-section-bar add-section-extra" id="extra-sections" style="display:none;margin-top:4px;">
        ${SECTION_TYPES.slice(7).map(t => `<button class="add-section-btn" data-type="${t}">+ ${t}</button>`).join('')}
      </div>
    </div>
  `;

  html += `<div id="section-detail-area"></div>`;

  container.innerHTML = html;

  // SortableJS drag-drop
  const listEl = container.querySelector('#section-list');
  if (sortableInstance) sortableInstance.destroy();
  sortableInstance = Sortable.create(listEl, {
    handle: '.drag-handle',
    animation: 150,
    ghostClass: 'section-card-ghost',
    onEnd(evt) {
      if (evt.oldIndex !== evt.newIndex) {
        reorderSections(evt.oldIndex, evt.newIndex);
      }
    },
  });

  container.querySelector('.form-presets').addEventListener('click', e => {
    const btn = e.target.closest('.form-preset-btn');
    if (btn) loadPreset(btn.dataset.preset);
  });

  listEl.addEventListener('click', e => {
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

  // Settings row events
  container.querySelector('#center-bpm-slider')?.addEventListener('input', e => {
    const bpm = parseInt(e.target.value);
    container.querySelector('#center-bpm-value').textContent = bpm;
    updateGlobal('bpm', bpm);
  });
  container.querySelector('#center-key-select')?.addEventListener('change', e => {
    updateGlobal('key', e.target.value);
  });
  container.querySelector('#center-time-sig')?.addEventListener('click', e => {
    const btn = e.target.closest('.radio-btn');
    if (btn) updateGlobal('timeSignature', btn.dataset.sig);
  });
  container.querySelector('#center-vocal-chips')?.addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (chip) toggleInArray('vocalTypes', chip.dataset.vocal);
  });
  container.querySelector('#center-arr-chips')?.addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (chip) updateGlobal('arrangement', chip.dataset.arr);
  });
  container.querySelector('#center-effects-chips')?.addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (chip) toggleInArray('effects', chip.dataset.effect);
  });
  container.querySelector('#center-mood-chips')?.addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (chip) toggleInArray('mood', chip.dataset.mood);
  });

  container.querySelector('.add-section-bar').addEventListener('click', e => {
    const btn = e.target.closest('.add-section-btn');
    if (!btn) return;
    if (btn.id === 'more-sections-toggle') {
      const extra = container.querySelector('#extra-sections');
      const isOpen = extra.style.display !== 'none';
      extra.style.display = isOpen ? 'none' : '';
      btn.textContent = isOpen ? 'More...' : 'Less';
      return;
    }
    if (btn.dataset.type) addSection(btn.dataset.type);
  });

  container.querySelector('#extra-sections')?.addEventListener('click', e => {
    const btn = e.target.closest('.add-section-btn');
    if (btn?.dataset.type) addSection(btn.dataset.type);
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
    return `<option value="${inst.name}">${isRec ? '★ ' : ''}${inst.name} (${inst.count})</option>`;
  }).join('');

  const topEffects = data.effects.slice(0, 12);

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

    const techniques = inst.name ? (data.instrumentTechniques[inst.name.toLowerCase()] || []) : [];

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
      html += `<div class="instrument-detail-chips">`;

      if (modifiers.length > 0) {
        html += `<div class="chip-row-label">Modifiers</div>
        <div class="chip-group" data-modifier-group="${inst.id}">
          ${modifiers.map(m => `<div class="chip ${inst.modifiers.includes(m.label) ? 'active' : ''}" data-mod="${m.label}" data-inst-id="${inst.id}">${m.label}</div>`).join('')}
        </div>`;
      }

      if (patterns.length > 0) {
        html += `<div class="chip-row-label">Patterns</div>
        <div class="chip-group" data-pattern-group="${inst.id}">
          ${patterns.map(p => `<div class="chip ${inst.pattern === p.label ? 'active' : ''}" data-pattern="${p.label}" data-inst-id="${inst.id}">${p.label}</div>`).join('')}
        </div>`;
      }

      if (techniques.length > 0) {
        html += `<div class="chip-row-label">Techniques <span class="label-hint">from corpus</span></div>
        <div class="chip-group" data-technique-group="${inst.id}">
          ${techniques.map(t => `<div class="chip ${inst.pattern === t ? 'active' : ''}" data-technique="${t}" data-inst-id="${inst.id}">${t}</div>`).join('')}
        </div>`;
      }

      html += `<div class="chip-row-label">Effects</div>
      <div class="chip-group" data-effect-group="${inst.id}">
        ${topEffects.map(e => `<div class="chip ${inst.effects.includes(e) ? 'active' : ''}" data-inst-effect="${e}" data-inst-id="${inst.id}">${e}</div>`).join('')}
      </div>`;

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

  // Event: instrument select
  for (const sel of detailArea.querySelectorAll('.inst-select')) {
    const instId = parseInt(sel.dataset.instId);
    const inst = section.instruments.find(i => i.id === instId);
    if (inst) sel.value = inst.name;

    sel.addEventListener('change', () => {
      updateInstrument(section.id, instId, 'name', sel.value);
      updateInstrument(section.id, instId, 'modifiers', []);
      updateInstrument(section.id, instId, 'pattern', '');
      updateInstrument(section.id, instId, 'effects', []);
    });
  }

  // Event: remove instrument
  for (const btn of detailArea.querySelectorAll('[data-remove-inst]')) {
    btn.addEventListener('click', () => {
      removeInstrumentFromSection(section.id, parseInt(btn.dataset.removeInst));
    });
  }

  // Event: add instrument
  detailArea.querySelector('#add-inst-btn').addEventListener('click', () => {
    addInstrumentToSection(section.id, '');
  });

  // Event: modifier chips
  for (const chip of detailArea.querySelectorAll('[data-mod]')) {
    chip.addEventListener('click', () => {
      const instId = parseInt(chip.dataset.instId);
      const inst = section.instruments.find(i => i.id === instId);
      if (!inst) return;
      const mods = [...inst.modifiers];
      const idx = mods.indexOf(chip.dataset.mod);
      if (idx === -1) mods.push(chip.dataset.mod);
      else mods.splice(idx, 1);
      updateInstrument(section.id, instId, 'modifiers', mods);
    });
  }

  // Event: pattern chips
  for (const chip of detailArea.querySelectorAll('[data-pattern]')) {
    chip.addEventListener('click', () => {
      const instId = parseInt(chip.dataset.instId);
      const inst = section.instruments.find(i => i.id === instId);
      if (!inst) return;
      updateInstrument(section.id, instId, 'pattern', inst.pattern === chip.dataset.pattern ? '' : chip.dataset.pattern);
    });
  }

  // Event: technique chips (set as pattern)
  for (const chip of detailArea.querySelectorAll('[data-technique]')) {
    chip.addEventListener('click', () => {
      const instId = parseInt(chip.dataset.instId);
      const inst = section.instruments.find(i => i.id === instId);
      if (!inst) return;
      updateInstrument(section.id, instId, 'pattern', inst.pattern === chip.dataset.technique ? '' : chip.dataset.technique);
    });
  }

  // Event: per-instrument effect chips
  for (const chip of detailArea.querySelectorAll('[data-inst-effect]')) {
    chip.addEventListener('click', () => {
      const instId = parseInt(chip.dataset.instId);
      toggleInstrumentEffect(section.id, instId, chip.dataset.instEffect);
    });
  }

  // Event: drum chips
  detailArea.querySelector('#drum-chips').addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (chip) toggleDrum(section.id, chip.dataset.drum);
  });

  // Event: vocal directive chips
  detailArea.querySelector('#vocal-directive-chips').addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    const v = chip.dataset.vdir;
    setSectionVocalDirective(section.id, section.vocalDirective === v ? '' : v);
  });
}
