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

export function loadPreset(preset) {
  state.sections = [];
  state.activeSectionId = null;
  const types = {
    'standard-pop': ['Intro', 'Verse', 'Pre-Chorus', 'Chorus', 'Verse', 'Pre-Chorus', 'Chorus', 'Bridge', 'Chorus', 'Outro'],
    'ballad': ['Intro', 'Verse', 'Chorus', 'Verse', 'Chorus', 'Bridge', 'Chorus', 'Outro'],
    'simple': ['Intro', 'Verse', 'Chorus', 'Verse', 'Chorus', 'Outro'],
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
