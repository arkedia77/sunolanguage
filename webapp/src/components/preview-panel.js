import { generateSP, generateBrackets, spToPlainText, bracketsToPlainText } from '../data/sp-generator.js';

export function renderPreview(container, state, data) {
  const spSentences = generateSP(state, data);
  const bracketLines = generateBrackets(state);
  const spPlain = spToPlainText(spSentences);
  const bracketsPlain = bracketsToPlainText(bracketLines);
  const spLen = spPlain.length;
  const brLen = bracketsPlain.length;

  const spClass = spLen > 900 ? 'danger' : spLen > 700 ? 'warning' : '';
  const brClass = brLen > 2800 ? 'danger' : brLen > 2000 ? 'warning' : '';

  let spHtml = '';
  for (const s of spSentences) {
    spHtml += `<span class="sp-${s.slot}">${escapeHtml(s.text)}</span> `;
  }

  let brHtml = '';
  for (const l of bracketLines) {
    if (l.type === 'blank') {
      brHtml += '\n';
    } else if (l.type === 'section') {
      brHtml += `<span class="bracket-section">${escapeHtml(l.text)}</span>\n`;
    } else if (l.type === 'instrument') {
      brHtml += `<span class="bracket-instrument">${escapeHtml(l.text)}</span>\n`;
    } else if (l.type === 'vocal') {
      brHtml += `<span class="bracket-vocal">${escapeHtml(l.text)}</span>\n`;
    } else if (l.type === 'placeholder') {
      brHtml += `<span class="bracket-placeholder">${escapeHtml(l.text)}</span>\n`;
    }
  }

  container.innerHTML = `
    <div class="preview-block">
      <div class="preview-label">
        <span>Style Prompt</span>
        <span class="char-count ${spClass}">${spLen} chars</span>
      </div>
      <div class="preview-text" id="sp-preview">${spHtml || '<span style="color:var(--text-muted)">Select genre and instruments to generate SP...</span>'}</div>
    </div>

    <div class="preview-block">
      <div class="preview-label">
        <span>Lyrics Brackets</span>
        <span class="char-count ${brClass}">${brLen} chars</span>
      </div>
      <div class="preview-text" id="bracket-preview">${brHtml || '<span style="color:var(--text-muted)">Add song sections to generate bracket structure...</span>'}</div>
    </div>

    <div class="copy-bar">
      <button class="copy-btn primary" id="copy-sp">Copy SP</button>
      <button class="copy-btn secondary" id="copy-lyrics">Copy Lyrics</button>
      <button class="copy-btn secondary" id="copy-both">Copy Both</button>
    </div>
  `;

  container.querySelector('#copy-sp').addEventListener('click', () => copyWithFeedback('copy-sp', spPlain));
  container.querySelector('#copy-lyrics').addEventListener('click', () => copyWithFeedback('copy-lyrics', bracketsPlain));
  container.querySelector('#copy-both').addEventListener('click', () => copyWithFeedback('copy-both', spPlain + '\n\n---\n\n' + bracketsPlain));
}

async function copyWithFeedback(btnId, text) {
  if (!text.trim()) return;
  try {
    await navigator.clipboard.writeText(text);
    const btn = document.getElementById(btnId);
    const orig = btn.textContent;
    btn.textContent = 'Copied!';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.textContent = orig;
      btn.classList.remove('copied');
    }, 1500);
  } catch {
    // fallback
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    ta.remove();
  }
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
