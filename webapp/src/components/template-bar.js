import { loadTemplate } from '../state/store.js';

const TAG_COLORS = {
  'Pop': '#6366f1',
  'Ballad': '#a78bfa',
  'Rock': '#ef4444',
  'R&B': '#f472b6',
  'Folk': '#22c55e',
  'Electronic': '#2dd4bf',
  'Hip-Hop': '#f59e0b',
  'Jazz': '#60a5fa',
  'Cinematic': '#8b5cf6',
  'World': '#fb923c',
};

export function renderTemplateBar(container, templates) {
  let html = `<div class="template-scroll">`;
  for (const t of templates) {
    const color = TAG_COLORS[t.tag] || '#6366f1';
    html += `
      <button class="template-card" data-template-id="${t.id}" style="--tag-color: ${color}">
        <span class="template-tag">${t.tag}</span>
        <span class="template-name">${t.name}</span>
        <span class="template-meta">${t.bpm} BPM · ${t.key}</span>
      </button>
    `;
  }
  html += `</div>`;
  container.innerHTML = html;

  container.addEventListener('click', e => {
    const card = e.target.closest('.template-card');
    if (!card) return;
    const t = templates.find(t => t.id === card.dataset.templateId);
    if (t) {
      loadTemplate(t);
      for (const c of container.querySelectorAll('.template-card')) {
        c.classList.toggle('active', c === card);
      }
    }
  });
}
