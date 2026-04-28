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

function parseTempoKeyTime(raw) {
  try {
    const cleaned = raw.replace(/'/g, '"').replace(/\bNone\b/g, 'null');
    return JSON.parse(cleaned);
  } catch { return null; }
}

function buildGenreAutoFill() {
  const fills = {};
  for (const g of rawSlotMatrix.matrix) {
    if (g.genre === '(미정)') continue;
    const slots = g.slots;
    const fill = { instruments: [], drums: [], effects: [], arrangement: '', bpm: 0, key: '', timeSignature: '' };

    const instEntities = (slots.instrument?.top_entities || []).slice(0, 4);
    fill.instruments = instEntities.map(e => e.entity);

    const drumEntity = (slots.drums?.top_entities || [])[0];
    if (drumEntity) {
      fill.drums = drumEntity.entity.split(',').map(s => s.trim()).filter(s => s && s !== 'drums');
    }

    const effectSkip = new Set(['with chorus', 'and chorus', 'in the mix', 'forward in the mix', 'centered in the mix']);
    const rawEffects = (slots.effect_electronic?.top_entities || []).slice(0, 5)
      .flatMap(e => e.entity.split(',').map(s => s.trim()))
      .filter(e => e && !effectSkip.has(e));
    fill.effects = [...new Set(rawEffects)].slice(0, 4);

    const arrEntity = (slots.arrangement?.top_entities || []).find(e => e.entity !== 'arrangement');
    if (arrEntity) fill.arrangement = arrEntity.entity;

    const tktEntity = (slots.tempo_key_time?.top_entities || [])[0];
    if (tktEntity) {
      const parsed = parseTempoKeyTime(tktEntity.entity);
      if (parsed) {
        fill.bpm = parsed.bpm || 0;
        fill.key = parsed.key || '';
        fill.timeSignature = parsed.time_signature || '';
      }
    }

    const vocalEntity = (slots.vocal_main?.top_entities || []).find(e => e.entity !== 'vocals');
    fill.vocal = vocalEntity ? vocalEntity.entity : '';

    fills[g.genre] = fill;
  }
  return fills;
}

const GENRE_CATEGORY_MAP = {
  'Pop': ['Indie Pop', 'City Pop', 'Acoustic Pop', 'Dream Pop', 'Funk Pop', 'Electro Pop', 'Art Pop', 'Jazz Pop', 'Folk Pop', 'Dance Pop', 'Dark Pop', 'Lo-fi Pop', 'Disco Pop', 'Synth Pop', 'Bedroom Pop', 'Indie Synth Pop', 'Hyperpop', 'Pop', 'K-POP', 'K-Pop'],
  'Ballad': ['Korean Ballad', 'Acoustic Ballad', 'Jazz Ballad', 'Soul Ballad', 'Piano Ballad'],
  'Rock': ['Rock', 'Indie Rock', 'Alternative Rock', 'Pop Rock', 'Pop Punk', 'Post-Punk', 'Soft Rock', 'Synth-Punk', 'Alternative'],
  'R&B / Soul': ['R&B', 'Neo-Soul', 'Contemporary R&B', 'Soft R&B', 'Indie Soul', 'Soft Indie'],
  'Folk': ['Folk', 'Indie Folk', 'Acoustic Folk', 'Ambient Folk', 'Acoustic Indie'],
  'Electronic': ['Electronic', 'Electropop', 'Future Bass', 'Chillwave', 'Synth-Pop', 'Ambient'],
  'Hip-Hop': ['Hip-Hop'],
  'Jazz': ['Jazz Pop', 'Jazz Ballad'],
  'Cinematic': ['Cinematic', 'Cinematic Emotional'],
  'World': ['Bossa Nova', 'TROT'],
};

function buildGenreCategories(genres) {
  const genreSet = new Set(genres.map(g => g.name));
  const assigned = new Set();
  const categories = [];

  for (const [cat, members] of Object.entries(GENRE_CATEGORY_MAP)) {
    const matched = members
      .filter(m => genreSet.has(m) && !assigned.has(m))
      .map(m => genres.find(g => g.name === m));
    for (const m of matched) assigned.add(m.name);
    if (matched.length > 0) {
      const total = matched.reduce((s, g) => s + g.songCount, 0);
      categories.push({ name: cat, genres: matched, totalSongs: total });
    }
  }

  const unassigned = genres.filter(g => !assigned.has(g.name));
  if (unassigned.length > 0) {
    const total = unassigned.reduce((s, g) => s + g.songCount, 0);
    categories.push({ name: 'Other', genres: unassigned, totalSongs: total });
  }

  categories.sort((a, b) => b.totalSongs - a.totalSongs);
  return categories;
}

function buildInstrumentTechniques() {
  const techs = {};
  for (const [name, info] of Object.entries(rawInstrumentIndex)) {
    techs[name.toLowerCase()] = (info.co_techniques || []).slice(0, 12);
  }
  return techs;
}

const genreList = buildGenreList();

export const data = {
  instruments: buildInstrumentList(),
  genres: genreList,
  genreCategories: buildGenreCategories(genreList),
  vocalTypes: buildVocalTypes(),
  drumComponents: buildDrumComponents(),
  keys: buildKeys(),
  bpmPresets: buildBpmPresets(),
  effects: buildEffects(),
  moods: buildMoods(),
  arrangements: buildArrangements(),
  genreRecommendations: buildGenreRecommendations(),
  genreAutoFill: buildGenreAutoFill(),
  instrumentTechniques: buildInstrumentTechniques(),
  genreIndex: rawGenreIndex,
  instrumentIndex: rawInstrumentIndex,
};
