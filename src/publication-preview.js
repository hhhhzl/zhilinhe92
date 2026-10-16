import './publication-preview.css';

const INTERVAL = 6500;
const pad = (number) => String(number).padStart(2, '0');
const videoSource = (media) => media.type === 'video' || /\.(mp4|webm|ogg|mov)(?:[?#]|$)/i.test(media.src);
const gifSource = (media) => media.type === 'gif' || /\.gif(?:[?#]|$)/i.test(media.src);

function node(tag, className, text) {
  const result = document.createElement(tag);
  if (className) result.className = className;
  if (text !== undefined) result.textContent = text;
  return result;
}

function control(label, symbol, className = '') {
  const button = node('button', `preview-control ${className}`, symbol);
  button.type = 'button';
  button.setAttribute('aria-label', label);
  button.title = label;
  return button;
}

/** One small media window per paper; only its current asset is mounted. */
function createPreview(paper, { resolveUrl, paused, onStateChange }) {
  const label = (typeof paper.abbr === 'object' ? paper.abbr.label : paper.abbr) || paper.title;
  const fallback = typeof paper.preview === 'string' ? { src: paper.preview } : paper.preview;
  const sources = Array.isArray(paper.media) && paper.media.length ? paper.media : [fallback];
  const media = sources.filter((item) => item && resolveUrl(item.src));
  if (!media.length) return null;

  const container = node('div', 'publication-preview publication-showcase');
  container.setAttribute('role', 'region');
  container.setAttribute('aria-roledescription', 'carousel');
  container.setAttribute('aria-label', `${label} experiments and figures`);
  container.dataset.count = String(media.length);

  const stage = node('a', 'preview-stage');
  stage.target = '_blank';
  stage.rel = 'noopener noreferrer';
  const slide = node('div', 'preview-slide');
  slide.setAttribute('role', 'group');
  slide.setAttribute('aria-roledescription', 'slide');
  stage.append(slide);

  const toolbar = node('div', 'preview-toolbar');
  const previous = control(`Previous ${label} experiment`, '←');
  const next = control(`Next ${label} experiment`, '→');
  const counter = node('span', 'preview-counter');
  counter.setAttribute('aria-hidden', 'true');
  const toggle = control(`Pause ${label} showcase`, 'Ⅱ', 'preview-toggle');
  const open = node('a', 'preview-control preview-open', '↗');
  open.target = '_blank';
  open.rel = 'noopener noreferrer';
  toolbar.append(previous, counter, next, toggle, open);

  const markers = node('div', 'preview-markers');
  markers.setAttribute('aria-label', `${label} experiment selection`);
  const markerButtons = media.map((item, index) => {
    const button = control(`Show ${label} ${index + 1} of ${media.length}: ${item.caption || item.alt || 'research preview'}`, '', 'preview-marker');
    button.append(node('span', 'preview-marker-track'));
    button.firstElementChild.append(node('span', 'preview-marker-fill'));
    button.addEventListener('click', () => select(index, true));
    markers.append(button);
    return button;
  });
  const caption = node('p', 'preview-caption');
  const announcement = node('span', 'sr-only');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', 'polite');
  container.append(stage, toolbar, markers, caption, announcement);

  let current = 0;
  let currentNode;
  let rotationPaused = paused;
  let mediaPaused = paused;
  let hovered = false;
  let pointerFocus = false;
  let visible = false;
  let destroyed = false;
  let remaining = INTERVAL;
  let started = 0;
  let timer;
  let progress;

  function stopTimer() {
    if (timer !== undefined) {
      clearTimeout(timer);
      remaining = Math.max(0, remaining - (performance.now() - started));
      timer = undefined;
    }
    progress?.pause();
  }

  function sync() {
    if (destroyed) return;
    const inView = visible && !document.hidden;
    const advancing = inView && !rotationPaused && !hovered && media.length > 1;
    container.dataset.playing = String(advancing);
    if (advancing && timer === undefined) {
      started = performance.now();
      timer = setTimeout(() => { timer = undefined; select(current + 1); }, remaining);
      progress?.play();
    } else if (!advancing) stopTimer();
    if (currentNode?.tagName === 'VIDEO') {
      if (inView && !mediaPaused) currentNode.play().catch(() => {});
      else currentNode.pause();
    }
    // GIFs cannot pause natively: use their poster, or a decoded still frame.
    if (currentNode?.tagName === 'IMG' && gifSource(media[current])) {
      const running = inView && !mediaPaused;
      const poster = resolveUrl(media[current].poster);
      const source = running ? resolveUrl(media[current].src) : poster || currentNode.dataset.frozen;
      if (source && currentNode.src !== source) currentNode.src = source;
      if (!source && !running) freezeGif(currentNode);
    }
    const buttonLabel = `${rotationPaused ? 'Play' : 'Pause'} ${label} showcase`;
    toggle.textContent = rotationPaused ? '▷' : 'Ⅱ';
    toggle.setAttribute('aria-label', buttonLabel);
    toggle.title = buttonLabel;
    toggle.setAttribute('aria-pressed', String(rotationPaused));
  }

  function freezeGif(image) {
    if (!image.complete || !image.naturalWidth || image.dataset.frozen) return;
    const canvas = document.createElement('canvas');
    canvas.width = image.naturalWidth;
    canvas.height = image.naturalHeight;
    try {
      canvas.getContext('2d').drawImage(image, 0, 0);
      const still = canvas.toDataURL('image/png');
      image.dataset.frozen = still;
      image.src = still;
    } catch { /* External GIFs should supply a local poster to permit freezing. */ }
  }

  function releaseMedia() {
    if (currentNode?.tagName === 'VIDEO') {
      currentNode.pause();
      currentNode.removeAttribute('src');
      currentNode.load();
    }
  }

  function select(index, manual = false) {
    stopTimer();
    progress?.cancel();
    releaseMedia();
    current = (index + media.length) % media.length;
    remaining = INTERVAL;
    if (manual) rotationPaused = true;
    const item = media[current];
    const description = item.caption || item.alt || `${label} research preview`;
    const source = resolveUrl(item.src);
    const isVideo = videoSource(item);
    currentNode = node(isVideo ? 'video' : 'img', 'publication-preview-media');
    if (isVideo) {
      currentNode.muted = true;
      currentNode.defaultMuted = true;
      currentNode.loop = true;
      currentNode.playsInline = true;
      currentNode.preload = 'none';
      currentNode.setAttribute('aria-label', item.alt || description);
      const poster = resolveUrl(item.poster);
      if (poster) currentNode.poster = poster;
    } else {
      currentNode.alt = item.alt || description;
      currentNode.decoding = 'async';
      currentNode.loading = 'lazy';
      if (gifSource(item)) currentNode.addEventListener('load', sync);
    }
    currentNode.src = source;
    slide.replaceChildren(currentNode);
    slide.setAttribute('aria-label', `${current + 1} of ${media.length}: ${description}`);
    stage.href = source;
    stage.setAttribute('aria-label', `Open full ${isVideo ? 'video' : 'figure'}: ${description}`);
    open.href = source;
    open.title = 'Open full size';
    open.setAttribute('aria-label', `Open ${label} ${isVideo ? 'video' : 'figure'} at full size`);
    counter.textContent = `${pad(current + 1)} / ${pad(media.length)}`;
    caption.textContent = description;
    caption.title = description;
    container.dataset.index = String(current);
    markerButtons.forEach((button, itemIndex) => button.setAttribute('aria-current', String(itemIndex === current)));
    const fill = markerButtons[current].querySelector('.preview-marker-fill');
    progress = fill.animate?.([{ transform: 'scaleX(0)' }, { transform: 'scaleX(1)' }], { duration: INTERVAL, fill: 'forwards' });
    progress?.pause();
    if (manual) {
      announcement.textContent = `${label}, ${current + 1} of ${media.length}: ${description}`;
      onStateChange();
    }
    sync();
  }

  function setPaused(value) {
    rotationPaused = value;
    mediaPaused = value;
    sync();
  }

  previous.addEventListener('click', () => select(current - 1, true));
  next.addEventListener('click', () => select(current + 1, true));
  toggle.addEventListener('click', () => { setPaused(!rotationPaused); onStateChange(); });
  container.addEventListener('pointerenter', () => { hovered = true; sync(); });
  container.addEventListener('pointerleave', () => { hovered = false; sync(); });
  container.addEventListener('pointerdown', () => { pointerFocus = true; });
  container.addEventListener('pointerup', () => { pointerFocus = false; });
  container.addEventListener('focusin', (event) => {
    if (!pointerFocus && !container.contains(event.relatedTarget)) {
      rotationPaused = true;
      sync();
      onStateChange();
    }
  });
  document.addEventListener('visibilitychange', sync);
  const observer = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting && entry.intersectionRatio >= .2; sync(); }, { threshold: .2 });
  observer.observe(container);
  select(0);

  return { element: container, get paused() { return rotationPaused; }, setPaused, destroy() {
    destroyed = true;
    stopTimer();
    progress?.cancel();
    observer.disconnect();
    document.removeEventListener('visibilitychange', sync);
    releaseMedia();
  } };
}

/** Shared motion preference and disposal when the publication filters rerender. */
export function createPublicationPreviews(resolveUrl, button) {
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  const previews = new Set();
  let paused = preference.matches;
  const updateButton = () => {
    if (!button) return;
    const allPaused = previews.size ? [...previews].every((preview) => preview.paused) : paused;
    button.textContent = allPaused ? 'Play previews ▷' : 'Pause previews Ⅱ';
    button.setAttribute('aria-pressed', String(allPaused));
    button.setAttribute('aria-label', `${allPaused ? 'Play' : 'Pause'} all publication previews`);
  };
  const setPaused = (value) => {
    paused = value;
    previews.forEach((preview) => preview.setPaused(value));
    updateButton();
  };
  const toggle = () => setPaused(![...previews].every((preview) => preview.paused));
  const reduce = () => setPaused(preference.matches);
  const clear = () => { previews.forEach((preview) => preview.destroy()); previews.clear(); };
  button?.addEventListener('click', toggle);
  preference.addEventListener('change', reduce);
  updateButton();
  return {
    create(paper) {
      const preview = createPreview(paper, { resolveUrl, paused, onStateChange: updateButton });
      if (preview) previews.add(preview);
      updateButton();
      return preview?.element;
    },
    clear,
    destroy() {
      clear();
      button?.removeEventListener('click', toggle);
      preference.removeEventListener('change', reduce);
    },
  };
}
