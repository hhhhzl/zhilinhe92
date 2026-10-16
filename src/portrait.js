/** One photograph at a time; the headshot is always the initial view. */
export function initPortrait() {
  const button = document.querySelector('#portrait-switch');
  if (!button) return;
  const photos = [...button.querySelectorAll('.portrait-photo')];
  const count = document.querySelector('#portrait-count');
  let alternate = false;
  button.addEventListener('click', () => {
    alternate = !alternate;
    button.classList.toggle('is-alternate', alternate);
    photos.forEach((photo, index) => photo.setAttribute('aria-hidden', String(index !== Number(alternate))));
    button.setAttribute('aria-label', alternate ? 'Show the headshot of Zhilin He' : 'Show the second portrait of Zhilin He');
    count.textContent = alternate ? '02 / 02' : '01 / 02';
  });
}
