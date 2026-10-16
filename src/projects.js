import './shared.js';
import './projects.css';
import { createDemoPlayback } from './research-media.js';

const showcase = document.querySelector('.case-generative');
showcase.querySelectorAll('video').forEach(video => {
  video.dataset.demo = '';
  video.muted = true;
  video.controls = false;
  video.tabIndex = 0;
  const show = () => { video.controls = true; };
  const hide = () => { if (document.activeElement !== video) video.controls = false; };
  video.addEventListener('pointerenter', show);
  video.addEventListener('pointerdown', show);
  video.addEventListener('focus', show);
  video.addEventListener('pointerleave', hide);
  video.addEventListener('blur', hide);
});
createDemoPlayback(showcase, document.querySelector('#project-motion-toggle')).refresh();
