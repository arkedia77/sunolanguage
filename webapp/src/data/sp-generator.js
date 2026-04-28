export function generateSP(state, data) {
  const { global: g, sections } = state;
  const sentences = [];

  if (g.genre) {
    let genreSentence = g.genre;
    if (g.vocalTypes.length > 0) {
      const vocalDesc = g.vocalTypes.map(v => {
        const bare = ['male', 'female', 'tenor', 'alto', 'baritone', 'soprano', 'mezzo-soprano'];
        return bare.includes(v.toLowerCase()) ? `${v} vocals` : v;
      });
      genreSentence += ` featuring ${vocalDesc.join(' and ')}`;
    }
    sentences.push({ text: genreSentence + '.', slot: 'genre' });
  }

  const allInstruments = [];
  for (const sec of sections) {
    for (const inst of sec.instruments) {
      if (inst.name && !allInstruments.find(a => a.name === inst.name)) {
        allInstruments.push(inst);
      }
    }
  }

  for (const inst of allInstruments) {
    let text = '';
    const mods = inst.modifiers.length > 0 ? inst.modifiers.join(', ') + ' ' : '';
    const name = inst.name;
    if (inst.pattern) {
      text = `${capitalize(mods)}${name} ${inst.pattern}`;
    } else {
      text = `${capitalize(mods)}${name}`;
    }
    if (inst.effects.length > 0) {
      text += ` with ${inst.effects.join(' and ')}`;
    }
    sentences.push({ text: text + '.', slot: 'instrument' });
  }

  const allDrums = new Set();
  for (const sec of sections) {
    for (const d of sec.drums) allDrums.add(d);
  }
  if (allDrums.size > 0) {
    const drumList = [...allDrums];
    sentences.push({
      text: `The drums feature ${joinList(drumList)}.`,
      slot: 'drums',
    });
  }

  if (g.vocalTypes.length > 0 && !sentences.some(s => s.slot === 'genre' && s.text.includes('featuring'))) {
    sentences.push({
      text: `${capitalize(g.vocalTypes.join(' and '))}.`,
      slot: 'vocal',
    });
  }

  if (g.effects.length > 0) {
    sentences.push({
      text: `${capitalize(joinList(g.effects))}.`,
      slot: 'effect',
    });
  }

  const tempoparts = [];
  if (g.bpm) tempoparts.push(`${g.bpm} BPM`);
  if (g.key) tempoparts.push(`Key of ${g.key}`);
  if (g.timeSignature) tempoparts.push(`${g.timeSignature} time`);
  if (tempoparts.length > 0) {
    sentences.push({
      text: tempoparts.join('. ') + '.',
      slot: 'tempo',
    });
  }

  if (g.mood && g.mood.length > 0) {
    sentences.push({
      text: `${capitalize(joinList(g.mood))} mood.`,
      slot: 'mood',
    });
  }

  if (g.arrangement) {
    sentences.push({
      text: `The arrangement is ${g.arrangement}.`,
      slot: 'arrangement',
    });
  }

  return sentences;
}

export function generateBrackets(state) {
  const { sections, global: g } = state;
  const lines = [];

  for (const sec of sections) {
    lines.push({ text: `[${sec.label}]`, type: 'section' });

    for (const inst of sec.instruments) {
      if (!inst.name) continue;
      const mods = inst.modifiers.length > 0 ? inst.modifiers.join(', ') + ' ' : '';
      let desc = `${mods}${inst.name}`;
      if (inst.pattern) desc += ' ' + inst.pattern;
      if (inst.effects.length > 0) desc += ` with ${inst.effects.join(' and ')}`;
      lines.push({ text: `[${desc}]`, type: 'instrument' });
    }

    if (sec.drums.length > 0) {
      lines.push({ text: `[${sec.drums.join(', ')}]`, type: 'instrument' });
    }

    if (sec.vocalDirective) {
      lines.push({ text: `(${sec.vocalDirective})`, type: 'vocal' });
    } else if (sec.type === 'Intro' || sec.type === 'Outro' || sec.type === 'Instrumental') {
      lines.push({ text: '(instrumental)', type: 'vocal' });
    } else if (g.vocalTypes.length > 0) {
      lines.push({ text: `(${g.vocalTypes[0]})`, type: 'vocal' });
    }

    if (!['Intro', 'Outro', 'Instrumental'].includes(sec.type)) {
      lines.push({ text: '(Your lyrics here)', type: 'placeholder' });
    }

    lines.push({ text: '', type: 'blank' });
  }

  return lines;
}

export function spToPlainText(sentences) {
  return sentences.map(s => s.text).join(' ');
}

export function bracketsToPlainText(lines) {
  return lines.map(l => l.text).join('\n');
}

function capitalize(str) {
  if (!str) return str;
  return str[0].toUpperCase() + str.slice(1);
}

function joinList(arr) {
  if (arr.length === 0) return '';
  if (arr.length === 1) return arr[0];
  if (arr.length === 2) return `${arr[0]} and ${arr[1]}`;
  return arr.slice(0, -1).join(', ') + ', and ' + arr[arr.length - 1];
}
