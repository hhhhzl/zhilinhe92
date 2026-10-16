import { profileDocuments, profileLinks } from './profile-data.js';
import './profile.css';

function linkUrl(value, allowEmail = false) {
  if (typeof value !== 'string' || !value.trim()) return null;
  if (allowEmail && /^mailto:[^\s?]+@[^\s?]+$/i.test(value.trim())) return value.trim();
  try {
    const url = new URL(value, new URL(import.meta.env.BASE_URL, document.baseURI));
    return ['https:', 'http:'].includes(url.protocol) ? url.href : null;
  } catch { return null; }
}

function externalLink(node, url) {
  node.href = url;
  if (/^https?:/.test(url) && new URL(url).origin !== location.origin) {
    node.target = '_blank';
    node.rel = 'noopener noreferrer';
  }
}

export function initProfile() {
  const documents = document.querySelector('#profile-documents');
  const socials = document.querySelector('#profile-socials');
  if (!documents || !socials) return;
  documents.replaceChildren();
  socials.replaceChildren();

  for (const item of profileDocuments) {
    const url = linkUrl(item.url);
    const control = document.createElement(url ? 'a' : 'span');
    control.className = 'profile-document';
    control.dataset.document = item.id;
    if (url) { externalLink(control, url); control.target = '_blank'; control.rel = 'noopener noreferrer'; }
    else {
      control.classList.add('is-unavailable');
      control.setAttribute('aria-disabled', 'true');
    }
    const label = document.createElement('span');
    label.className = 'profile-document-label';
    label.textContent = item.label;
    const marker = document.createElement('span');
    marker.className = 'profile-document-marker';
    marker.textContent = url ? '↗' : 'Coming soon';
    if (url) marker.setAttribute('aria-hidden', 'true');
    control.append(label, marker);
    documents.append(control);
  }

  for (const item of profileLinks) {
    const url = linkUrl(item.url, item.id === 'email');
    if (!url) continue;
    const link = document.createElement('a');
    link.className = 'profile-social';
    link.setAttribute('aria-label', item.label);
    externalLink(link, url);
    const icon = document.createElement('span');
    icon.className = 'profile-social-icon';
    icon.setAttribute('aria-hidden', 'true');
    icon.style.setProperty('--profile-icon', `url("${new URL(`assets/icons/${item.id}.svg`, new URL(import.meta.env.BASE_URL, document.baseURI)).href}")`);
    const tooltip = document.createElement('span');
    tooltip.className = 'profile-social-tooltip';
    tooltip.setAttribute('aria-hidden', 'true');
    tooltip.textContent = item.label;
    link.append(icon, tooltip);
    socials.append(link);
  }
  socials.hidden = !socials.childElementCount;
}
