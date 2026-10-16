import './publication-preview.css';

const SWITCH_INTERVAL = 3000;
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

/** A fixed window alternates the method and complete montage, never individual clips. */
function createPreview(paper, { resolveUrl, initial, onStateChange, open }) {
  const label = (typeof paper.abbr === 'object' ? paper.abbr.label : paper.abbr) || paper.title;
  const visuals = [
    paper.method && { item: paper.method, kind: 'Method' },
    paper.montage && { item: paper.montage, kind: isVideo(paper.montage) ? 'Experiments' : 'Results' },
  ].filter((entry) => entry && resolveUrl(entry.item.src));
  if (!visuals.length) {
    const fallback = typeof paper.preview === 'string' ? { src: paper.preview } : paper.preview;
    if (fallback && resolveUrl(fallback.src)) visuals.push({ item: fallback, kind: 'Figure' });
  }
  if (!visuals.length) return null;

  const container = node('div', 'publication-preview publication-showcase');
  container.setAttribute('role', 'group');
  container.setAttribute('aria-label', label + ' research preview');
  container.dataset.count = String(visuals.length);
  const panel = node('div', 'preview-panel');
  panel.id = 'preview-panel-' + paper.id;
  const stage = node('button', 'preview-stage');
  stage.type = 'button';
  const expand = node('span', 'preview-expand', '↗');
  expand.setAttribute('aria-hidden', 'true');
  panel.append(stage);
  const toolbar = node('div', 'preview-caption');
  const tabs = node('div', 'preview-tabs');
  const tabButtons = [];
  if (visuals.length > 1) {
    tabs.setAttribute('role', 'tablist');
    tabs.setAttribute('aria-label', label + ' preview selection');
    panel.setAttribute('role', 'tabpanel');
    visuals.forEach(({ kind }, index) => {
      const tab = node('button', 'preview-tab', kind);
      tab.type = 'button';
      tab.id = `preview-tab-${paper.id}-${index}`;
      tab.setAttribute('role', 'tab');
      tab.setAttribute('aria-controls', panel.id);
      tab.addEventListener('click', () => select(index, true));
      tab.addEventListener('keydown', (event) => {
        let target;
        if (event.key === 'ArrowRight') target = (index + 1) % visuals.length;
        else if (event.key === 'ArrowLeft') target = (index + visuals.length - 1) % visuals.length;
        else if (event.key === 'Home') target = 0;
        else if (event.key === 'End') target = visuals.length - 1;
        if (target !== undefined) {
          event.preventDefault();
          select(target, true);
          tabButtons[target].focus();
        }
      });
      tabButtons.push(tab);
      tabs.append(tab);
    });
  } else tabs.append(node('span', 'preview-kind', visuals[0].kind));
  const animated = visuals.length > 1 || visuals.some(({ item }) => isVideo(item));
  const toggle = control('Pause ' + label + ' preview', 'Ⅱ', 'preview-toggle');
  toolbar.append(tabs);
  if (animated) toolbar.append(toggle);
  const announcement = node('span', 'sr-only');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', 'polite');
  container.append(panel, toolbar, announcement);

  let index = Math.min(Math.max(initial.index || 0, 0), visuals.length - 1);
  let mediaPaused = initial.paused;
  let holdSelection = initial.holdSelection || false;
  let covered = false;
  let visible = false;
  let hovered = false;
  let pointerFocus = false;
  let destroyed = false;
  let remaining = SWITCH_INTERVAL;
  let timer;
  let started = 0;
  // Keep the video cached while its method figure is shown, so each visit resumes
  // the montage instead of repeatedly showing only its first three seconds.
  const mediaNodes = visuals.map(({ item }, itemIndex) => {
    const media = makeMedia(item, resolveUrl);
    const time = initial.mediaTimes?.[itemIndex];
    if (isVideo(item) && time > 0) media.addEventListener('loadedmetadata', () => {
      if (!destroyed && Number.isFinite(media.duration)) media.currentTime = Math.min(time, media.duration);
    }, { once: true });
    return media;
  });
  const state = () => ({
    paused: mediaPaused, index, holdSelection,
    mediaTimes: mediaNodes.map((media, itemIndex) => media.tagName === 'VIDEO'
      ? (media.readyState ? media.currentTime : initial.mediaTimes?.[itemIndex] || media.currentTime) : 0),
  });
  const remember = () => onStateChange(state());

  function stopTimer() {
    if (timer !== undefined) {
      clearTimeout(timer);
      remaining = Math.max(0, remaining - (performance.now() - started));
      timer = undefined;
    }
  }
  function sync() {
    if (destroyed) return;
    const canPlay = visible && !mediaPaused && !covered && !document.hidden;
    mediaNodes.forEach((media, itemIndex) => {
      if (media.tagName !== 'VIDEO') return;
      if (canPlay && itemIndex === index) media.play().catch(() => {});
      else media.pause();
    });
    const advancing = canPlay && visuals.length > 1 && !holdSelection && !hovered;
    container.dataset.playing = String(advancing);
    container.dataset.paused = String(mediaPaused);
    if (advancing && timer === undefined) {
      started = performance.now();
      timer = setTimeout(() => { timer = undefined; select((index + 1) % visuals.length); }, remaining);
    } else if (!advancing) stopTimer();
    const action = (mediaPaused ? 'Play ' : 'Pause ') + label + ' preview';
    toggle.textContent = mediaPaused ? '▷' : 'Ⅱ';
    toggle.setAttribute('aria-label', action);
    toggle.title = action;
    toggle.setAttribute('aria-pressed', String(mediaPaused));
  }
  function select(next, manual = false) {
    stopTimer();
    index = next;
    remaining = SWITCH_INTERVAL;
    if (manual) holdSelection = true;
    const { kind } = visuals[index];
    // Pause before detaching the old video: at most the visible media may play.
    mediaNodes.forEach((media) => { if (media.tagName === 'VIDEO') media.pause(); });
    stage.replaceChildren(mediaNodes[index], expand);
    stage.dataset.kind = kind.toLowerCase();
    stage.setAttribute('aria-label', 'Enlarge ' + label + ' ' + kind.toLowerCase());
    container.dataset.index = String(index);
    container.dataset.kind = kind.toLowerCase();
    tabButtons.forEach((tab, itemIndex) => {
      tab.setAttribute('aria-selected', String(itemIndex === index));
      tab.tabIndex = itemIndex === index ? 0 : -1;
    });
    if (tabButtons.length) panel.setAttribute('aria-labelledby', tabButtons[index].id);
    if (manual) announcement.textContent = label + ': ' + kind;
    remember();
    sync();
  }
  function setPaused(value) {
    stopTimer();
    mediaPaused = value;
    if (!value) { holdSelection = false; remaining = SWITCH_INTERVAL; }
    remember();
    sync();
  }
  toggle.addEventListener('click', () => setPaused(!mediaPaused));
  stage.addEventListener('click', () => open(visuals[index].item, label + ' / ' + visuals[index].kind, mediaPaused, mediaNodes[index]));
  container.addEventListener('pointerenter', () => { hovered = true; sync(); });
  container.addEventListener('pointerleave', () => { hovered = false; pointerFocus = false; sync(); });
  container.addEventListener('pointerdown', () => { pointerFocus = true; });
  container.addEventListener('pointerup', () => { pointerFocus = false; });
  container.addEventListener('pointercancel', () => { pointerFocus = false; });
  container.addEventListener('focusin', (event) => {
    if (!pointerFocus && !container.contains(event.relatedTarget)) {
      holdSelection = true;
      remember();
      sync();
    }
  });
  document.addEventListener('visibilitychange', sync);
  const observer = new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting && entry.intersectionRatio >= .15;
    sync();
  }, { threshold: .15 });
  observer.observe(container);
  select(index);
  return {
    element: container, animated,
    get paused() { return mediaPaused; },
    getState: state,
    setPaused,
    cover(value) { covered = value; sync(); },
    destroy() {
      remember();
      destroyed = true;
      stopTimer();
      observer.disconnect();
      document.removeEventListener('visibilitychange', sync);
      mediaNodes.forEach(release);
    },
  };
}

/** Shared preference, filter-persistent state and one full-size media viewer. */
export function createPublicationPreviews(resolveUrl, button) {
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  const previews = new Set();
  const paperStates = new Map();
  let paused = preference.matches;
  let expanded;
  let expandedSource;
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
    expandedSource = source;
    expandedWasPlaying = false;
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
    if (expanded?.tagName === 'VIDEO' && expandedSource?.tagName === 'VIDEO' && Number.isFinite(expanded.currentTime)) {
      try { expandedSource.currentTime = expanded.currentTime; } catch { /* A filtered preview may already be released. */ }
    }
    release(expanded);
    expanded = null;
    expandedSource = null;
    expandedWasPlaying = false;
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
    button.textContent = allPaused() ? 'Play previews ▷' : 'Pause previews Ⅱ';
    button.setAttribute('aria-pressed', String(allPaused()));
    button.setAttribute('aria-label', (allPaused() ? 'Play' : 'Pause') + ' all publication previews');
    button.disabled = animated().length === 0;
  };
  const setPaused = (value) => {
    paused = value;
    paperStates.clear();
    previews.forEach((preview) => preview.setPaused(value));
    if (expanded?.tagName === 'VIDEO') {
      if (value) { expandedWasPlaying = false; expanded.pause(); }
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
    updateButton();
  };
  button?.addEventListener('click', toggle);
  preference.addEventListener('change', reduce);
  updateButton();
  return {
    create(paper) {
      const preview = createPreview(paper, {
        resolveUrl, initial: paperStates.get(paper.id) || { paused }, open,
        onStateChange(value) { paperStates.set(paper.id, value); updateButton(); },
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
