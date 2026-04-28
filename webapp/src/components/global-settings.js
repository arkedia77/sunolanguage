import { updateGlobal, toggleInArray, autoFillFromGenre } from '../state/store.js';

let initialized = false;

export function renderGlobalSettings(container, state, data) {
  const g = state.global;

  if (!initialized) {
    initialized = true;
    container.innerHTML = `
      <div class="panel-section">
        <div class="panel-section-title">Genre</div>
        <div class="panel-desc">SP 첫 문장. Suno가 곡 전체 스타일을 결정합니다.</div>
        <div class="search-input">
          <input type="text" id="genre-search" placeholder="Search genres..." />
        </div>
        <div id="genre-categories"></div>
        <button class="autofill-btn" id="autofill-btn" style="display:none">Auto-fill from Genre</button>
      </div>

      <div class="panel-section">
        <div class="panel-section-title">Main Instruments</div>
        <div class="panel-desc">곡 전체의 메인 악기 → SP에 반영. 섹션별 배치는 Song Form에서.</div>
        <div class="search-input">
          <input type="text" id="inst-search" placeholder="Search instruments..." />
        </div>
        <div class="chip-group" id="main-inst-chips"></div>
      </div>
    `;

    setupGenreCategories(container, data);
    setupMainInstruments(container, data);
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

function setupMainInstruments(container, data) {
  const el = container.querySelector('#main-inst-chips');
  const recs = () => {
    const genre = container.querySelector('.genre-chip.active')?.dataset.genre;
    if (!genre) return new Set();
    const r = data.genreRecommendations[genre];
    return new Set((r?.instrument || []).map(s => s.toLowerCase()));
  };

  function renderChips(filter) {
    const recSet = recs();
    const filtered = filter
      ? data.instruments.filter(i => i.name.toLowerCase().includes(filter))
      : data.instruments.slice(0, 30);
    el.innerHTML = filtered
      .map(i => {
        const isRec = recSet.has(i.name.toLowerCase());
        return `<div class="chip ${isRec ? 'recommended' : ''}" data-main-inst="${i.name}">${i.name} <span class="freq">${i.count}</span></div>`;
      }).join('');
  }

  renderChips('');

  const search = container.querySelector('#inst-search');
  search.addEventListener('input', () => renderChips(search.value.toLowerCase()));

  el.addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (chip) toggleInArray('mainInstruments', chip.dataset.mainInst);
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

  for (const chip of container.querySelectorAll('#main-inst-chips .chip')) {
    chip.classList.toggle('active', g.mainInstruments.includes(chip.dataset.mainInst));
  }

  const autoBtn = container.querySelector('#autofill-btn');
  autoBtn.style.display = g.genre ? '' : 'none';
}
