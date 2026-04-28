import { updateGlobal, toggleInArray, autoFillFromGenre } from '../state/store.js';

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
        <div id="genre-categories"></div>
        <button class="autofill-btn" id="autofill-btn" style="display:none">Auto-fill from Genre</button>
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

    setupGenreCategories(container, data);
    setupEffectsChips(container, data);
    setupMoodChips(container, data);
    setupGenreSearch(container);
    setupAutoFill(container, data);
  }

  updateActiveStates(container, state, data);
}

function setupGenreCategories(container, data) {
  const el = container.querySelector('#genre-categories');
  let html = '';
  for (const cat of data.genreCategories) {
    html += `
      <div class="genre-category" data-cat="${cat.name}">
        <div class="genre-category-header">
          <span class="genre-cat-arrow">&#x25B6;</span>
          <span class="genre-cat-name">${cat.name}</span>
          <span class="genre-cat-count">${cat.totalSongs}</span>
        </div>
        <div class="genre-category-body" style="display:none">
          <div class="chip-group">
            ${cat.genres.map(g => `<div class="chip genre-chip" data-genre="${g.name}">${g.name} <span class="freq">${g.songCount}</span></div>`).join('')}
          </div>
        </div>
      </div>
    `;
  }
  el.innerHTML = html;

  el.addEventListener('click', e => {
    const header = e.target.closest('.genre-category-header');
    if (header) {
      const cat = header.closest('.genre-category');
      const body = cat.querySelector('.genre-category-body');
      const arrow = cat.querySelector('.genre-cat-arrow');
      const isOpen = body.style.display !== 'none';
      body.style.display = isOpen ? 'none' : '';
      arrow.innerHTML = isOpen ? '&#x25B6;' : '&#x25BC;';
      return;
    }
    const chip = e.target.closest('.genre-chip');
    if (chip) {
      updateGlobal('genre', chip.dataset.genre);
    }
  });
}

function setupGenreSearch(container) {
  const input = container.querySelector('#genre-search');
  const cats = container.querySelectorAll('.genre-category');
  input.addEventListener('input', () => {
    const q = input.value.toLowerCase();
    if (!q) {
      for (const cat of cats) {
        cat.style.display = '';
        cat.querySelector('.genre-category-body').style.display = 'none';
        cat.querySelector('.genre-cat-arrow').innerHTML = '&#x25B6;';
        for (const chip of cat.querySelectorAll('.genre-chip')) chip.style.display = '';
      }
      return;
    }
    for (const cat of cats) {
      const chips = cat.querySelectorAll('.genre-chip');
      let anyVisible = false;
      for (const chip of chips) {
        const match = chip.dataset.genre.toLowerCase().includes(q);
        chip.style.display = match ? '' : 'none';
        if (match) anyVisible = true;
      }
      cat.style.display = anyVisible ? '' : 'none';
      if (anyVisible) {
        cat.querySelector('.genre-category-body').style.display = '';
        cat.querySelector('.genre-cat-arrow').innerHTML = '&#x25BC;';
      }
    }
  });
}

function setupEffectsChips(container, data) {
  const el = container.querySelector('#effects-chips');
  el.innerHTML = data.effects.slice(0, 20)
    .map(e => `<div class="chip" data-effect="${e}">${e}</div>`)
    .join('');
  el.addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (chip) toggleInArray('effects', chip.dataset.effect);
  });
}

function setupMoodChips(container, data) {
  const el = container.querySelector('#mood-chips');
  el.innerHTML = data.moods
    .map(m => `<div class="chip" data-mood="${m}">${m}</div>`)
    .join('');
  el.addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (chip) toggleInArray('mood', chip.dataset.mood);
  });
}

function setupAutoFill(container, data) {
  container.querySelector('#autofill-btn').addEventListener('click', () => {
    const genre = container.querySelector('.genre-chip.active')?.dataset.genre;
    if (!genre) return;
    const fillData = data.genreAutoFill[genre];
    if (fillData) autoFillFromGenre(fillData);
  });
}

function updateActiveStates(container, state, data) {
  const g = state.global;

  for (const chip of container.querySelectorAll('.genre-chip')) {
    const isActive = chip.dataset.genre === g.genre;
    chip.classList.toggle('active', isActive);
    if (isActive) {
      const body = chip.closest('.genre-category-body');
      if (body && body.style.display === 'none') {
        body.style.display = '';
        body.closest('.genre-category').querySelector('.genre-cat-arrow').innerHTML = '&#x25BC;';
      }
    }
  }
  for (const chip of container.querySelectorAll('#effects-chips .chip')) {
    chip.classList.toggle('active', g.effects.includes(chip.dataset.effect));
  }
  for (const chip of container.querySelectorAll('#mood-chips .chip')) {
    chip.classList.toggle('active', g.mood.includes(chip.dataset.mood));
  }

  const autoBtn = container.querySelector('#autofill-btn');
  autoBtn.style.display = g.genre ? '' : 'none';

  const recs = data.genreRecommendations[g.genre];
  for (const chip of container.querySelectorAll('#effects-chips .chip')) {
    const isRec = recs && (recs.effect_electronic || []).some(e =>
      e.toLowerCase().includes(chip.dataset.effect.toLowerCase())
    );
    chip.classList.toggle('recommended', isRec);
  }
}
