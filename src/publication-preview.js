import './publication-preview.css';

const isVideo = (item) => item.type === 'video' || /\.(mp4|webm)(?:[?#]|$)/i.test(item.src);
function node(tag, className, text) {
  const result = document.createElement(tag);
  if (className) result.className = className;
  if (text !== undefined) result.textContent = text;
  return result;
}
function control(label, symbol, className = '') {
  const button = node('button', 'preview-control ' + className, symbol);
  button.type = 'button';
  button.setAttribute('aria-label', label);
  button.title = label;
  return button;
}
function makeMedia(item, resolveUrl, expanded = false) {
  const media = node(isVideo(item) ? 'video' : 'img', 'publication-preview-media');
  if (item.width && item.height) { media.width = item.width; media.height = item.height; }
  if (isVideo(item)) {
    media.width = item.width || 1200;
    media.height = item.height || 900;
    media.muted = true;
    media.defaultMuted = true;
    media.loop = true;
    media.playsInline = true;
    media.preload = 'none';
    media.controls = expanded;
    media.setAttribute('aria-label', item.alt || item.caption);
    if (item.poster) media.poster = resolveUrl(item.poster);
  } else {
    media.alt = item.alt || item.caption || 'Paper figure';
    media.loading = expanded ? 'eager' : 'lazy';
    media.decoding = 'async';
  }
  media.src = resolveUrl(item.src);
  return media;
}
function release(media) {
  if (media?.tagName !== 'VIDEO') return;
  media.pause();
  media.removeAttribute('src');
  media.load();
}

/** One method figure and one simultaneous experiment montage. No slide rotation. */
function createPreview(paper, { resolveUrl, paused, onStateChange, open }) {
  const label = (typeof paper.abbr === 'object' ? paper.abbr.label : paper.abbr) || paper.title;
  const visuals = [paper.method, paper.montage].filter((item) => item && resolveUrl(item.src));
  if (!visuals.length) {
    const fallback = typeof paper.preview === 'string' ? { src: paper.preview } : paper.preview;
    if (fallback && resolveUrl(fallback.src)) visuals.push(fallback);
  }
  if (!visuals.length) return null;
  const container = node('div', 'publication-preview publication-showcase');
  container.setAttribute('role', 'group');
  container.setAttribute('aria-label', label + ' method and experiments');
  container.dataset.count = String(visuals.length);
  const players = [];
  let mediaPaused = paused;
  let covered = false;
  let visible = false;

  function sync() {
    for (const { media, toggle } of players) {
      if (visible && !mediaPaused && !covered && !document.hidden) media.play().catch(() => {});
      else media.pause();
      const action = (mediaPaused ? 'Play ' : 'Pause ') + label + ' experiment montage';
      toggle.textContent = mediaPaused ? '▷' : 'Ⅱ';
      toggle.setAttribute('aria-label', action);
      toggle.title = action;
      toggle.setAttribute('aria-pressed', String(mediaPaused));
    }
  }
  for (const [index, item] of visuals.entries()) {
    const kind = item === paper.method ? 'Method' : item === paper.montage ? (isVideo(item) ? 'Experiments' : 'Results') : 'Figure';
    const figure = node('figure', 'publication-visual publication-visual-' + kind.toLowerCase());
    const stage = node('button', 'preview-stage');
    stage.type = 'button';
    stage.setAttribute('aria-label', 'Enlarge ' + label + ' ' + kind.toLowerCase());
    const media = makeMedia(item, resolveUrl);
    const expand = node('span', 'preview-expand', '↗');
    expand.setAttribute('aria-hidden', 'true');
    stage.append(media, expand);
    stage.addEventListener('click', () => open(item, label + ' / ' + kind, mediaPaused, media));
    const caption = node('figcaption', 'preview-caption');
    caption.append(node('span', 'preview-kind', String(index + 1).padStart(2, '0') + ' / ' + kind));
    if (isVideo(item)) {
      const toggle = control('Pause ' + label + ' experiment montage', 'Ⅱ', 'preview-toggle');
      toggle.addEventListener('click', () => { mediaPaused = !mediaPaused; sync(); onStateChange(mediaPaused); });
      caption.append(toggle);
      players.push({ media, toggle });
    }
    figure.append(stage, caption);
    container.append(figure);
  }
  document.addEventListener('visibilitychange', sync);
  const observer = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; sync(); }, { threshold: 0 });
  observer.observe(container);
  sync();
  return {
    element: container,
    animated: players.length > 0,
    get paused() { return mediaPaused; },
    setPaused(value) { mediaPaused = value; sync(); },
    cover(value) { covered = value; sync(); },
    destroy() {
      observer.disconnect();
      document.removeEventListener('visibilitychange', sync);
      players.forEach(({ media }) => release(media));
    },
  };
}

/** Shared motion preference and a full-size viewer for the two publication visuals. */
export function createPublicationPreviews(resolveUrl, button) {
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  const previews = new Set();
  const paperPauseStates = new Map();
  let paused = preference.matches;
  let expanded;
  let expandedWasPlaying = false;
  const dialog = node('dialog', 'publication-viewer');
  dialog.setAttribute('aria-label', 'Full-size publication figure');
  const heading = node('h2', 'viewer-title');
  const close = control('Close full-size figure', '×', 'viewer-close');
  const header = node('div', 'viewer-header');
  header.append(heading, close);
  const stage = node('div', 'viewer-stage');
  const caption = node('p', 'viewer-caption');
  const download = node('a', 'viewer-download');
  const footer = node('div', 'viewer-footer');
  footer.append(caption, download);
  dialog.append(header, stage, footer);
  document.body.append(dialog);

  const open = (item, title, mediaPaused, source) => {
    dialog.style.setProperty('--visual-aspect', String(item.width && item.height ? item.width / item.height : 4 / 3));
    heading.textContent = title;
    caption.textContent = item.caption || item.alt || '';
    download.href = resolveUrl(item.gif || item.src);
    download.download = '';
    download.textContent = item.gif ? 'Download GIF ↓' : isVideo(item) ? 'Download video ↓' : 'Download figure ↓';
    expanded = makeMedia(item, resolveUrl, true);
    stage.replaceChildren(expanded);
    previews.forEach((preview) => preview.cover(true));
    dialog.showModal();
    document.documentElement.classList.add('publication-viewer-open');
    if (isVideo(item)) {
      const player = expanded;
      player.addEventListener('loadedmetadata', () => {
        if (source.currentTime && player.isConnected) player.currentTime = source.currentTime;
      }, { once: true });
      if (!mediaPaused && !document.hidden) player.play().catch(() => {});
    }
  };
  const finish = () => {
    release(expanded);
    expanded = null;
    stage.replaceChildren();
    document.documentElement.classList.remove('publication-viewer-open');
    previews.forEach((preview) => preview.cover(false));
  };
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', finish);
  dialog.addEventListener('click', (event) => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
  });
  const visibility = () => {
    if (!expanded || expanded.tagName !== 'VIDEO') return;
    if (document.hidden) { expandedWasPlaying = !expanded.paused; expanded.pause(); }
    else if (expandedWasPlaying) expanded.play().catch(() => {});
  };
  document.addEventListener('visibilitychange', visibility);
  const animated = () => [...previews].filter((preview) => preview.animated);
  const allPaused = () => animated().length ? animated().every((preview) => preview.paused) : paused;
  const updateButton = () => {
    if (!button) return;
    button.textContent = allPaused() ? 'Play demos ▷' : 'Pause demos Ⅱ';
    button.setAttribute('aria-pressed', String(allPaused()));
    button.setAttribute('aria-label', (allPaused() ? 'Play' : 'Pause') + ' all publication demos');
  };
  const setPaused = (value) => {
    paused = value;
    paperPauseStates.clear();
    previews.forEach((preview) => preview.setPaused(value));
    if (expanded?.tagName === 'VIDEO') {
      if (value) expanded.pause();
      else if (!document.hidden) expanded.play().catch(() => {});
    }
    updateButton();
  };
  const toggle = () => setPaused(!allPaused());
  const reduce = () => setPaused(preference.matches);
  const clear = () => {
    if (dialog.open) { dialog.close(); finish(); }
    previews.forEach((preview) => preview.destroy());
    previews.clear();
  };
  button?.addEventListener('click', toggle);
  preference.addEventListener('change', reduce);
  updateButton();
  return {
    create(paper) {
      const preview = createPreview(paper, {
        resolveUrl, paused: paperPauseStates.get(paper.id) ?? paused, open,
        onStateChange(value) { paperPauseStates.set(paper.id, value); updateButton(); },
      });
      if (preview) previews.add(preview);
      updateButton();
      return preview?.element;
    },
    clear,
    destroy() {
      clear();
      dialog.remove();
      document.removeEventListener('visibilitychange', visibility);
      button?.removeEventListener('click', toggle);
      preference.removeEventListener('change', reduce);
    },
  };
}
