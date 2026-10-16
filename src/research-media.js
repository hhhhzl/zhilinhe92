/** Only play muted demos visible on screen; honor reduced motion and page visibility. */
export function createDemoPlayback(root, button) {
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  let paused = preference.matches;
  let observer;
  let videos = [];
  const visible = new Set();
  function sync() {
    videos.forEach(video => {
      if (!paused && !document.hidden && visible.has(video)) video.play().catch(() => {});
      else video.pause();
    });
    if (button) {
      button.textContent = paused ? 'Play demos ▷' : 'Pause demos Ⅱ';
      button.setAttribute('aria-pressed', String(paused));
    }
  }
  function refresh() {
    observer?.disconnect();
    videos.forEach(video => video.pause());
    visible.clear();
    videos = [...root.querySelectorAll('video[data-demo]')];
    observer = new IntersectionObserver(entries => {
      entries.forEach(({target, isIntersecting}) => {
        if (isIntersecting) visible.add(target); else visible.delete(target);
      });
      sync();
    }, {threshold: .1});
    videos.forEach(video => observer.observe(video));
    sync();
  }
  const toggle = () => { paused = !paused; sync(); };
  const reduce = () => { paused = preference.matches; sync(); };
  button?.addEventListener('click', toggle);
  document.addEventListener('visibilitychange', sync);
  preference.addEventListener('change', reduce);
  return {refresh, destroy() {
    observer?.disconnect();
    videos.forEach(video => video.pause());
    button?.removeEventListener('click', toggle);
    document.removeEventListener('visibilitychange', sync);
    preference.removeEventListener('change', reduce);
  }};
}
