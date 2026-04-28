const listeners = new Set();

let nextId = 1;

const state = {
  global: {
    genre: '',
    bpm: 92,
    key: '',
    timeSignature: '4/4',
    vocalTypes: [],
    arrangement: '',
    mood: [],
    effects: [],
    mainInstruments: [],
  },
  sections: [],
  activeSectionId: null,
};

export function getState() {
  return state;
}

export function subscribe(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

function notify() {
  for (const fn of listeners) fn(state);
}

export function updateGlobal(key, value) {
  state.global[key] = value;
  notify();
}

export function toggleInArray(key, value) {
  const arr = state.global[key];
  const idx = arr.indexOf(value);
  if (idx === -1) arr.push(value);
  else arr.splice(idx, 1);
  notify();
}

export function addSection(type) {
  const counts = {};
  for (const s of state.sections) {
    counts[s.type] = (counts[s.type] || 0) + 1;
  }
  const needsNumber = ['Verse', 'Chorus', 'Bridge'].includes(type);
  const num = needsNumber ? (counts[type] || 0) + 1 : 0;
  const label = num > 0 ? `${type} ${num}` : type;

  const section = {
    id: nextId++,
    type,
    label,
    instruments: [],
    drums: [],
    vocalOverride: null,
    vocalDirective: '',
  };
  state.sections.push(section);
  state.activeSectionId = section.id;
  notify();
}

export function removeSection(id) {
  const idx = state.sections.findIndex(s => s.id === id);
  if (idx === -1) return;
  state.sections.splice(idx, 1);
  if (state.activeSectionId === id) {
    state.activeSectionId = state.sections.length > 0 ? state.sections[0].id : null;
  }
  notify();
}

export function setActiveSection(id) {
  state.activeSectionId = id;
  notify();
}

export function getActiveSection() {
  return state.sections.find(s => s.id === state.activeSectionId) || null;
}

export function addInstrumentToSection(sectionId, instrumentName) {
  const section = state.sections.find(s => s.id === sectionId);
  if (!section) return;
  section.instruments.push({
    id: nextId++,
    name: instrumentName,
    modifiers: [],
    pattern: '',
    effects: [],
  });
  notify();
}

export function removeInstrumentFromSection(sectionId, instrumentId) {
  const section = state.sections.find(s => s.id === sectionId);
  if (!section) return;
  section.instruments = section.instruments.filter(i => i.id !== instrumentId);
  notify();
}

export function updateInstrument(sectionId, instrumentId, key, value) {
  const section = state.sections.find(s => s.id === sectionId);
  if (!section) return;
  const inst = section.instruments.find(i => i.id === instrumentId);
  if (!inst) return;
  inst[key] = value;
  notify();
}

export function toggleDrum(sectionId, drum) {
  const section = state.sections.find(s => s.id === sectionId);
  if (!section) return;
  const idx = section.drums.indexOf(drum);
  if (idx === -1) section.drums.push(drum);
  else section.drums.splice(idx, 1);
  notify();
}

export function setSectionVocalDirective(sectionId, directive) {
  const section = state.sections.find(s => s.id === sectionId);
  if (!section) return;
  section.vocalDirective = directive;
  notify();
}

let currentPreset = '';

export function loadPreset(preset) {
  if (preset === currentPreset && state.sections.length > 0) {
    state.sections = [];
    state.activeSectionId = null;
    currentPreset = '';
    notify();
    return;
  }
  currentPreset = preset;
  state.sections = [];
  state.activeSectionId = null;
  const types = {
    'standard-pop': ['Intro', 'Verse', 'Pre-Chorus', 'Chorus', 'Verse', 'Pre-Chorus', 'Chorus', 'Bridge', 'Chorus', 'Outro'],
    'ballad': ['Intro', 'Verse', 'Chorus', 'Verse', 'Chorus', 'Bridge', 'Chorus', 'Outro'],
    'simple': ['Intro', 'Verse', 'Chorus', 'Verse', 'Chorus', 'Outro'],
    'k-pop': ['Intro', 'Verse', 'Pre-Chorus', 'Chorus', 'Verse', 'Rap', 'Chorus', 'Bridge', 'Dance Break', 'Chorus', 'Outro'],
    'rock': ['Intro', 'Verse', 'Chorus', 'Verse', 'Chorus', 'Solo', 'Bridge', 'Chorus', 'Outro'],
    'edm': ['Intro', 'Build', 'Drop', 'Breakdown', 'Build', 'Drop', 'Outro'],
    'sonata': ['Exposition', 'Development', 'Recapitulation', 'Coda'],
    'rondo': ['A', 'B', 'A', 'C', 'A', 'Coda'],
    'aaba': ['A', 'A', 'B', 'A'],
    'through-composed': ['Section A', 'Section B', 'Section C', 'Section D'],
    'concerto': ['Orchestral Intro', 'Exposition', 'Solo Cadenza', 'Development', 'Recapitulation', 'Coda'],
    'blues': ['Verse', 'Verse', 'Verse', 'Verse'],
  };
  for (const type of (types[preset] || [])) {
    addSection(type);
  }
}

export function moveSectionUp(id) {
  const idx = state.sections.findIndex(s => s.id === id);
  if (idx <= 0) return;
  [state.sections[idx - 1], state.sections[idx]] = [state.sections[idx], state.sections[idx - 1]];
  notify();
}

export function moveSectionDown(id) {
  const idx = state.sections.findIndex(s => s.id === id);
  if (idx === -1 || idx >= state.sections.length - 1) return;
  [state.sections[idx], state.sections[idx + 1]] = [state.sections[idx + 1], state.sections[idx]];
  notify();
}

export function reorderSections(oldIndex, newIndex) {
  const [moved] = state.sections.splice(oldIndex, 1);
  state.sections.splice(newIndex, 0, moved);
  notify();
}

export function autoFillFromGenre(fillData) {
  if (fillData.bpm) state.global.bpm = fillData.bpm;
  if (fillData.key) {
    state.global.key = fillData.key.split(' ').map(w => w[0].toUpperCase() + w.slice(1)).join(' ');
  }
  if (fillData.timeSignature) state.global.timeSignature = fillData.timeSignature;
  if (fillData.arrangement) state.global.arrangement = fillData.arrangement;
  if (fillData.effects?.length > 0) {
    for (const e of fillData.effects) {
      if (!state.global.effects.includes(e)) state.global.effects.push(e);
    }
  }
  if (fillData.vocal) {
    const parts = fillData.vocal.split(',').map(s => s.replace(/\s*vocals?\s*/gi, '').trim()).filter(Boolean);
    for (const v of parts) {
      if (!state.global.vocalTypes.includes(v)) {
        state.global.vocalTypes.push(v);
      }
    }
  }

  if (fillData.instruments?.length > 0) {
    for (const instName of fillData.instruments) {
      if (!state.global.mainInstruments.includes(instName)) {
        state.global.mainInstruments.push(instName);
      }
    }
  }

  for (const sec of state.sections) {
    if (sec.instruments.length === 0 && fillData.instruments.length > 0) {
      for (const instName of fillData.instruments) {
        sec.instruments.push({
          id: nextId++,
          name: instName,
          modifiers: [],
          pattern: '',
          effects: [],
        });
      }
    }
    if (sec.drums.length === 0 && fillData.drums.length > 0) {
      sec.drums = [...fillData.drums];
    }
  }

  notify();
}

export function loadTemplate(template) {
  state.global.genre = template.genre || '';
  state.global.bpm = template.bpm || 92;
  state.global.key = template.key || '';
  state.global.timeSignature = template.timeSignature || '4/4';
  state.global.arrangement = template.arrangement || '';
  state.global.vocalTypes = template.vocalTypes ? template.vocalTypes.slice() : [];
  state.global.effects = template.effects ? template.effects.slice() : [];
  state.global.mood = template.mood ? template.mood.slice() : [];
  state.global.mainInstruments = template.instruments ? template.instruments.slice() : [];

  loadPreset(template.preset || 'simple');

  for (const sec of state.sections) {
    if (template.instruments?.length > 0) {
      for (const instName of template.instruments) {
        sec.instruments.push({
          id: nextId++,
          name: instName,
          modifiers: [],
          pattern: '',
          effects: [],
        });
      }
    }
    if (template.drums?.length > 0) {
      sec.drums = template.drums.slice();
    }
  }

  notify();
}

export function toggleInstrumentEffect(sectionId, instrumentId, effect) {
  const section = state.sections.find(s => s.id === sectionId);
  if (!section) return;
  const inst = section.instruments.find(i => i.id === instrumentId);
  if (!inst) return;
  const idx = inst.effects.indexOf(effect);
  if (idx === -1) inst.effects.push(effect);
  else inst.effects.splice(idx, 1);
  notify();
}
