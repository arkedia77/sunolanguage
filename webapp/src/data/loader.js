import rawDictionary from '@rag/suno_dictionary.json';
import rawGenreIndex from '@rag/genre_index.json';
import rawInstrumentIndex from '@rag/instrument_index.json';
import rawSlotMatrix from '@reanalysis/slot_genre_matrix.json';

function parseJsonArrayKey(key) {
  try {
    return JSON.parse(key.replace(/'/g, '"'));
  } catch {
    return [key];
  }
}

function extractUniqueItems(vocabObj) {
  const items = new Set();
  for (const key of Object.keys(vocabObj)) {
    for (const item of parseJsonArrayKey(key)) {
      items.add(item);
    }
  }
  return [...items].sort();
}

function buildInstrumentList() {
  const phrases = rawDictionary.instrument_phrases;
  return Object.entries(phrases)
    .map(([name, data]) => ({
      name,
      count: data.count,
      genreSpread: data.genre_spread,
      modifiers: (data.top_modifiers || []).map(m => {
        const parsed = parseJsonArrayKey(m.modifier);
        return { label: parsed.join(', '), freq: m.freq };
      }),
      patterns: (data.top_patterns || []).map(p => ({
        label: p.pattern,
        freq: p.freq,
      })),
    }))
    .sort((a, b) => b.count - a.count);
}

function buildGenreList() {
  return rawSlotMatrix.matrix
    .filter(g => g.genre !== '(미정)')
    .map(g => ({
      name: g.genre,
      songCount: g.song_count,
      slotsFilled: g.slots_filled,
      slots: g.slots,
    }))
    .sort((a, b) => b.songCount - a.songCount);
}

function buildVocalTypes() {
  const types = new Set();
  for (const key of Object.keys(rawDictionary.vocal_expressions)) {
    for (const v of parseJsonArrayKey(key)) {
      if (!['voice', 'singer', 'vocalist', 'singing', 'vocalizing'].includes(v)) {
        types.add(v);
      }
    }
  }
  return [...types].sort();
}

function buildDrumComponents() {
  const items = extractUniqueItems(rawDictionary.drum_vocab);
  return items.filter(d => !['drums', 'beat'].includes(d));
}

function buildKeys() {
  const ks = rawDictionary.key_signatures.keys;
  return Object.entries(ks)
    .sort((a, b) => b[1] - a[1])
    .map(([key, freq]) => ({
      label: key.split(' ').map(w => w[0].toUpperCase() + w.slice(1)).join(' '),
      freq,
    }));
}

function buildBpmPresets() {
  const bpms = rawDictionary.key_signatures.bpm;
  return Object.entries(bpms)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([bpm, freq]) => ({ value: parseInt(bpm), freq }));
}

function buildEffects() {
  const effects = new Set();
  const skip = new Set(['and chorus', 'centered in the mix', 'clock-ticking', 'dripping', 'forward in the mix', 'hum', 'in the mix', 'with chorus']);
  for (const key of Object.keys(rawDictionary.production_vocab)) {
    for (const item of parseJsonArrayKey(key)) {
      if (!skip.has(item)) effects.add(item);
    }
  }
  return [...effects].sort();
}

function buildMoods() {
  return Object.keys(rawDictionary.mood_emotion).sort();
}

function buildArrangements() {
  return ['sparse', 'intimate', 'minimal', 'lush', 'dense', 'full band', 'orchestral', 'stripped-back'];
}

function buildGenreRecommendations() {
  const recs = {};
  for (const g of rawSlotMatrix.matrix) {
    if (g.genre === '(미정)') continue;
    const rec = {};
    for (const [slot, data] of Object.entries(g.slots)) {
      rec[slot] = (data.top_entities || []).map(e => e.entity);
    }
    recs[g.genre] = rec;
  }
  return recs;
}

export const data = {
  instruments: buildInstrumentList(),
  genres: buildGenreList(),
  vocalTypes: buildVocalTypes(),
  drumComponents: buildDrumComponents(),
  keys: buildKeys(),
  bpmPresets: buildBpmPresets(),
  effects: buildEffects(),
  moods: buildMoods(),
  arrangements: buildArrangements(),
  genreRecommendations: buildGenreRecommendations(),
  genreIndex: rawGenreIndex,
  instrumentIndex: rawInstrumentIndex,
};
