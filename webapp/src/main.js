import { data } from './data/loader.js';
import { TEMPLATES } from './data/templates.js';
import { renderGlobalSettings } from './components/global-settings.js';
import { renderSongForm } from './components/song-form-editor.js';
import { renderPreview } from './components/preview-panel.js';
import { renderTemplateBar } from './components/template-bar.js';
import { subscribe, getState } from './state/store.js';

renderTemplateBar(document.getElementById('template-bar'), TEMPLATES);

function render() {
  const state = getState();
  renderGlobalSettings(document.getElementById('global-settings'), state, data);
  renderSongForm(document.getElementById('song-form'), state, data);
  renderPreview(document.getElementById('preview'), state, data);
}

subscribe(render);
render();
