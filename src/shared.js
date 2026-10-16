import './style.css';
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
document.documentElement.classList.toggle('reduced-motion', reduced.matches);
const observer = new IntersectionObserver(entries => entries.forEach(entry => { if (entry.isIntersecting) { entry.target.classList.add('is-visible'); observer.unobserve(entry.target); } }), {threshold:.06});
document.querySelectorAll('.reveal').forEach(el=>observer.observe(el));
document.querySelectorAll('video').forEach(video=>{ new IntersectionObserver(entries=>{if(!entries[0].isIntersecting)video.pause();}).observe(video); });
