import { data } from './data/loader.js';
import { renderGlobalSettings } from './components/global-settings.js';
import { renderSongForm } from './components/song-form-editor.js';
import { renderPreview } from './components/preview-panel.js';
import { subscribe, getState } from './state/store.js';

function render() {
  const state = getState();
  renderGlobalSettings(document.getElementById('global-settings'), state, data);
  renderSongForm(document.getElementById('song-form'), state, data);
  renderPreview(document.getElementById('preview'), state, data);
}

subscribe(render);
render();
