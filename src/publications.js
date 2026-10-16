import { createPublicationPreviews } from './publication-preview.js';
import { publications, publicationBibTeX, allBibTeX } from './publication-data.js';

const resourceLabels = {
  pdf: 'PDF', code: 'Code', website: 'Website', video: 'Video', blog: 'Blog',
  html: 'HTML', poster: 'Poster', slides: 'Slides', supp: 'Supplement',
  doi: 'DOI', arxiv: 'arXiv', hal: 'HAL',
};
const initialized = new WeakMap();
const abbreviation = (paper) => typeof paper.abbr === 'object' ? paper.abbr?.label : paper.abbr;
const paperLabel = (paper) => abbreviation(paper) || paper.title;
const months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'];
const monthNumber = (value) => Number(value) || (value ? months.findIndex((month) => month.startsWith(String(value).toLowerCase())) + 1 : 0);

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

/** Local paths are relative to the deployment base, including legacy /assets/ paths. */
export function publicationUrl(value, pageUrl = document.baseURI, base = import.meta.env?.BASE_URL || './') {
  if (typeof value !== 'string' || !value.trim()) return null;
  const input = value.trim();
  try {
    const deployment = new URL(base, pageUrl);
    const local = input.startsWith('/') && !input.startsWith('//') ? input.slice(1) : input;
    const url = new URL(local, input.startsWith('#') ? pageUrl : deployment);
    return ['https:', 'http:'].includes(url.protocol) ? url.href : null;
  } catch { return null; }
}
const safeUrl = publicationUrl;

function anchor(label, url, className = '') {
  const href = safeUrl(url);
  if (!href) return element('span', className, label);
  const node = element('a', className, label);
  node.href = href;
  if (new URL(href).origin !== location.origin) {
    node.target = '_blank';
    node.rel = 'noopener noreferrer';
  }
  return node;
}

function resourceUrl(type, value) {
  const raw = typeof value === 'object' ? value?.url : value;
  if (typeof raw !== 'string' || !raw.trim()) return null;
  if (/^https?:\/\//i.test(raw) || raw.startsWith('/') || raw.startsWith('.')) return safeUrl(raw);
  if (type === 'doi' && /^10\.\d{4,9}\//.test(raw)) return safeUrl(`https://doi.org/${raw}`);
  if (type === 'arxiv' && /^(\d{4}\.\d{4,5}|[a-z.-]+\/\d{7})(v\d+)?$/i.test(raw)) return safeUrl(`https://arxiv.org/abs/${raw}`);
  if (type === 'hal' && /^hal-[\d]+(v\d+)?$/i.test(raw)) return safeUrl(`https://hal.science/${raw}`);
  return ['doi', 'arxiv', 'hal'].includes(type) ? null : safeUrl(raw);
}

function preview(paper, showcases) {
  const showcase = showcases.create(paper);
  if (showcase) return showcase;
  const container = element('div', 'publication-preview');
  const card = element('div', 'publication-monogram');
  card.dataset.theme = paper.monogram?.theme || 'blue';
  card.setAttribute('aria-hidden', 'true');
  card.append(element('span', 'monogram-kicker', 'RESEARCH / ' + paper.year));
  card.append(element('span', 'monogram-orbit monogram-orbit-one'));
  card.append(element('span', 'monogram-orbit monogram-orbit-two'));
  card.append(element('strong', 'monogram-label', paper.monogram?.label || paperLabel(paper)));
  card.append(element('span', 'monogram-caption', paper.tags?.[0] || 'Research'));
  container.append(card);
  return container;
}

function disclosure(label, className, paper) {
  const button = element('button', 'publication-panel-toggle', label);
  const panel = element('div', `publication-expanded-panel ${className}`);
  panel.id = `publication-${paper.id}-${label.toLowerCase()}`;
  panel.hidden = true;
  panel.setAttribute('role', 'region');
  button.type = 'button';
  button.id = `${panel.id}-toggle`;
  button.dataset.panel = label.toLowerCase();
  button.setAttribute('aria-label', `${label} for ${paperLabel(paper)}`);
  button.setAttribute('aria-controls', panel.id);
  button.setAttribute('aria-expanded', 'false');
  panel.setAttribute('aria-labelledby', button.id);
  button.addEventListener('click', () => {
    panel.hidden = !panel.hidden;
    button.setAttribute('aria-expanded', String(!panel.hidden));
  });
  return { button, panel };
}

async function copyText(text) {
  if (navigator.clipboard?.writeText && window.isSecureContext) {
    try { await navigator.clipboard.writeText(text); return true; } catch { /* Try local fallback. */ }
  }
  const area = element('textarea', 'publication-copy-buffer');
  area.value = text;
  area.setAttribute('readonly', '');
  area.style.cssText = 'position:fixed;left:-9999px;top:0;opacity:0';
  const focused = document.activeElement;
  document.body.append(area);
  area.select();
  let success = false;
  try { success = document.execCommand('copy'); } catch { /* Manual selection remains available. */ }
  area.remove();
  focused?.focus?.({ preventScroll: true });
  return success;
}

function renderPaper(paper, announce, showcases) {
  const article = element('article', 'publication');
  article.id = `publication-${paper.id}`;
  article.dataset.selected = String(Boolean(paper.selected));
  article.setAttribute('aria-labelledby', `${article.id}-title`);
  article.append(preview(paper, showcases));
  const info = element('div', 'publication-info');
  const meta = element('div', 'publication-meta');
  if (abbreviation(paper)) {
    const badge = anchor(abbreviation(paper), paper.abbr?.url || paper.abbr_url, 'publication-abbr');
    if (paper.abbr?.color || paper.abbr_color) badge.style.color = paper.abbr?.color || paper.abbr_color;
    meta.append(badge);
  }
  meta.append(element('span', 'publication-year', String(paper.year)));
  if (paper.selected) meta.append(element('span', 'publication-selected', 'Selected'));
  if (paper.award || paper.award_name) {
    const award = typeof paper.award === 'string' ? { label: paper.award } : paper.award;
    const badge = anchor(paper.award_name || award?.label, award?.url, 'publication-award');
    if (paper.award_name && typeof paper.award === 'string') badge.title = paper.award;
    meta.append(badge);
  }
  info.append(meta);
  const title = element('h3', 'publication-title', paper.title);
  title.id = `${article.id}-title`;
  info.append(title);
  const authors = element('p', 'publication-authors');
  const authorLimit = Math.max(1, Number(paper.authorLimit) || 6);
  const extraAuthors = element('span', 'publication-extra-authors');
  extraAuthors.id = `${article.id}-extra-authors`;
  extraAuthors.hidden = true;
  paper.authors.forEach((entry, index) => {
    const author = typeof entry === 'string' ? { name: entry } : entry;
    const target = index < authorLimit ? authors : extraAuthors;
    if (index) target.append(document.createTextNode(', '));
    const name = anchor(author.name, author.url, author.self ? 'publication-author is-self' : 'publication-author');
    if (author.self) name.setAttribute('aria-label', `${author.name}, site author`);
    target.append(name);
    if (author.annotation) {
      const marker = element('sup', 'author-annotation', author.annotation);
      target.append(marker);
    }
  });
  if (paper.authors.length > authorLimit) {
    const toggle = element('button', 'publication-authors-toggle', `+${paper.authors.length - authorLimit} authors`);
    toggle.type = 'button';
    toggle.setAttribute('aria-controls', extraAuthors.id);
    toggle.setAttribute('aria-expanded', 'false');
    toggle.addEventListener('click', () => {
      extraAuthors.hidden = !extraAuthors.hidden;
      toggle.setAttribute('aria-expanded', String(!extraAuthors.hidden));
      toggle.textContent = extraAuthors.hidden ? `+${paper.authors.length - authorLimit} authors` : 'Show fewer';
    });
    authors.append(extraAuthors, document.createTextNode(' '), toggle);
  }
  info.append(authors);
  const venue = [paper.journal, paper.booktitle, paper.school].filter(Boolean).join(' · ');
  if (venue || paper.month || paper.location) {
    const line = element('p', 'publication-venue');
    if (venue) line.append(anchor(venue, paper.venueUrl));
    const month = months[monthNumber(paper.month) - 1];
    const date = [month ? month[0].toUpperCase() + month.slice(1) : paper.month, paper.year].filter(Boolean).join(' ');
    line.append(document.createTextNode(`${venue ? ' · ' : ''}${[date, paper.location].filter(Boolean).join(' · ')}`));
    info.append(line);
  }
  if (paper.note) info.append(element('p', 'publication-note', paper.note));
  if (paper.additional_info) info.append(element('p', 'publication-additional-info', paper.additional_info));
  if (paper.summary) info.append(element('p', 'publication-summary', paper.summary));
  if (paper.annotation) info.append(element('p', 'publication-annotation', paper.annotation));
  const actions = element('div', 'publication-actions');
  const resources = element('div', 'publication-resources');
  resources.setAttribute('aria-label', `Resources for ${paperLabel(paper)}`);
  for (const [type, label] of Object.entries(resourceLabels)) {
    const url = resourceUrl(type, paper[type]);
    if (!url) continue;
    const resource = anchor(typeof paper[type] === 'object' && paper[type].label ? paper[type].label : label, url, 'publication-resource');
    resource.dataset.resource = type;
    resources.append(resource);
  }
  if (resources.childElementCount) actions.append(resources);
  const badges = element('div', 'publication-badges');
  for (const badge of paper.badges || []) {
    if (!badge?.label) continue;
    const label = badge.value === undefined || badge.value === null || badge.value === '' ? badge.label : `${badge.label}: ${badge.value}`;
    badges.append(anchor(label, badge.url, 'publication-badge'));
  }
  const panels = element('div', 'publication-panels');
  const expandedPanels = element('div', 'publication-expanded-panels');
  if (paper.abstract) {
    const abstract = disclosure('Abstract', 'publication-abstract', paper);
    abstract.panel.append(element('p', 'publication-abstract-text', paper.abstract));
    panels.append(abstract.button);
    expandedPanels.append(abstract.panel);
  }
  const citation = publicationBibTeX(paper);
  const bibtex = disclosure('BibTeX', 'publication-bibtex', paper);
  const code = element('code', '', citation);
  const pre = element('pre', 'publication-citation');
  pre.tabIndex = 0;
  pre.append(code);
  const copy = element('button', 'publication-copy', 'Copy BibTeX');
  copy.type = 'button';
  copy.addEventListener('click', async () => {
    const success = await copyText(citation);
    copy.textContent = success ? 'Copied' : 'Select citation to copy';
    announce(success ? `BibTeX for ${paperLabel(paper)} copied.` : 'Copy was unavailable. Select and copy the citation below.');
    if (!success) {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(code);
      selection?.removeAllRanges();
      selection?.addRange(range);
      pre.focus({ preventScroll: true });
    }
  });
  bibtex.panel.append(copy, pre);
  panels.append(bibtex.button);
  expandedPanels.append(bibtex.panel);
  actions.append(panels);
  info.append(actions, expandedPanels);
  if (badges.childElementCount) info.append(badges);
  article.append(info);
  return article;
}

function searchableText(paper) {
  return [paper.title, abbreviation(paper), paper.year, paper.month, paper.journal, paper.booktitle, paper.school,
    paper.location, paper.note, paper.additional_info, paper.summary, paper.abstract, paper.annotation, ...(paper.tags || []),
    ...paper.authors.map((a) => typeof a === 'string' ? a : a.name)]
    .filter(Boolean).join(' ').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
}

/** Pure matching helper, also usable by a future external search interface. */
export function filterPublications(papers, { query = '', year = '', selected = false } = {}) {
  const terms = String(query).normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim().split(/\s+/).filter(Boolean);
  return papers.filter((paper) => (!year || year === 'all' || String(paper.year) === String(year))
    && (!selected || paper.selected)
    && terms.every((term) => searchableText(paper).includes(term)))
    .sort((a, b) => Number(b.year) - Number(a.year) || monthNumber(b.month) - monthNumber(a.month));
}

/** Initialize after the page mounts exist. No side effects when imported alone.
 * Optional { root: Document|Element, papers: Publication[] }. Returns { render, destroy }.
 * Bindings: #publication-list, #publication-search, #year-filter, #selected-filter,
 * #export-bib, #result-count, and #copy-status. All but the list are optional.
 * Initial query: ?q=term, #q=term, #publication-ID, #ID, or an exact #abbreviation.
 */
export function initPublications({ root = document, papers = publications } = {}) {
  const list = root.querySelector('#publication-list');
  if (!list) return null;
  if (initialized.has(list)) return initialized.get(list);
  const search = root.querySelector('#publication-search');
  const year = root.querySelector('#year-filter');
  const selected = root.querySelector('#selected-filter');
  const exportButton = root.querySelector('#export-bib');
  const count = root.querySelector('#result-count');
  const total = root.querySelector('#publication-heading .sup-count');
  const status = root.querySelector('#copy-status');
  const url = new URL(location.href);
  let hash = url.hash.slice(1);
  try { hash = decodeURIComponent(hash); } catch { /* Ignore malformed encoding. */ }
  const linkedPaper = papers.find((paper) => [paper.id, `publication-${paper.id}`, abbreviation(paper)].includes(hash));
  const initialQuery = url.searchParams.get('q') ?? (hash.startsWith('q=') ? new URLSearchParams(hash).get('q') : linkedPaper && paperLabel(linkedPaper));
  if (search && initialQuery !== null && initialQuery !== undefined) search.value = initialQuery;
  const listeners = [];
  const on = (node, type, listener) => {
    if (!node) return;
    node.addEventListener(type, listener);
    listeners.push(() => node.removeEventListener(type, listener));
  };
  const announce = (message) => { if (status) status.textContent = message; };
  if (status) { status.setAttribute('role', 'status'); status.setAttribute('aria-live', 'polite'); }
  if (count) count.setAttribute('aria-live', 'polite');
  if (year) {
    const previousYear = year.value;
    year.replaceChildren(new Option('All years', ''));
    [...new Set(papers.map((paper) => paper.year))].sort((a, b) => b - a)
      .forEach((value) => year.append(new Option(String(value), String(value))));
    if ([...year.options].some((option) => option.value === previousYear)) year.value = previousYear;
  }
  const showcases = createPublicationPreviews(safeUrl, root.querySelector('#media-motion-toggle'));
  const render = () => {
    showcases.clear();
    const results = filterPublications(papers, { query: search?.value, year: year?.value, selected: selected?.checked });
    const fragment = document.createDocumentFragment();
    if (results.length) results.forEach((paper) => fragment.append(renderPaper(paper, announce, showcases)));
    else fragment.append(element('p', 'publication-empty', 'No publications match these filters. Try another search or clear the filters.'));
    list.replaceChildren(fragment);
    if (total) total.textContent = String(papers.length).padStart(2, '0');
    if (count) count.textContent = `${results.length} of ${papers.length} publication${papers.length === 1 ? '' : 's'}`;
    return results;
  };
  on(search, 'input', render);
  on(year, 'change', render);
  on(selected, 'change', render);
  on(exportButton, 'click', (event) => {
    event.preventDefault();
    const content = papers === publications ? allBibTeX : papers.map(publicationBibTeX).join('\n\n') + '\n';
    const url = URL.createObjectURL(new Blob([content], { type: 'application/x-bibtex;charset=utf-8' }));
    const download = element('a');
    download.href = url;
    download.download = 'zhilin-he-publications.bib';
    document.body.append(download);
    download.click();
    download.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    announce(`Downloaded BibTeX for all ${papers.length} publications.`);
  });
  const controller = { render, destroy() { showcases.destroy(); listeners.forEach((remove) => remove()); initialized.delete(list); } };
  initialized.set(list, controller);
  render();
  return controller;
}

export { publications, publicationBibTeX, allBibTeX };
