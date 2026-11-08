const linksByReference = new Map();

for (const [index, link] of [...document.querySelectorAll('a[role="doc-biblioref"]')].entries()) {
  const entry = document.getElementById(link.hash.slice(1));
  if (!entry) continue;
  link.id = `citation-${index + 1}`;
  link.title = entry.querySelector('.csl-right-inline')?.textContent.trim() ?? '';
  link.setAttribute('aria-label', `Перейти к источнику ${link.textContent.trim()}`);
  if (!linksByReference.has(entry)) linksByReference.set(entry, []);
  linksByReference.get(entry).push(link);
}

for (const [entry, citations] of linksByReference) {
  const backlinks = document.createElement('nav');
  backlinks.className = 'reference-backlinks';
  backlinks.setAttribute('aria-label', 'Упоминания источника в статье');
  for (const [index, citation] of citations.entries()) {
    const link = document.createElement('a');
    link.href = `#${citation.id}`;
    link.textContent = citations.length === 1 ? '↑ К тексту' : `↑ Упоминание ${index + 1}`;
    backlinks.append(link);
  }
  entry.querySelector('.csl-right-inline')?.append(backlinks);
}

for (const link of document.querySelectorAll('#refs a[href^="assets/papers/"][href$=".pdf"]')) {
  link.setAttribute('download', '');
  link.classList.add('reference-download');
}
