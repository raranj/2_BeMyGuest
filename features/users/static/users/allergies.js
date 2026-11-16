(() => {
  const endpoint = document.currentScript.dataset.suggestionsUrl;
  const stored = document.getElementById('id_allergies');
  if (!stored) return;
  const form = stored.form;
  const tags = document.createElement('div');
  tags.className = 'allergy-tags';
  tags.setAttribute('aria-label', 'Selected allergies');
  const input = document.createElement('input');
  input.type = 'text';
  input.id = 'allergy-search';
  input.maxLength = 100;
  input.placeholder = 'Type an allergy and press Enter';
  input.autocomplete = 'off';
  input.setAttribute('list', 'allergy-suggestions');
  input.setAttribute('aria-describedby', 'id_allergies_helptext');
  const suggestions = document.createElement('datalist');
  suggestions.id = 'allergy-suggestions';
  const status = document.createElement('span');
  status.setAttribute('role', 'status');
  let selected = [];
  const normalize = value => value.trim().replace(/\s+/g, ' ').toLowerCase();
  function render() {
    stored.value = selected.join(', ');
    tags.replaceChildren();
    selected.forEach(term => {
      const chip = document.createElement('span');
      chip.className = 'badge allergy-tag';
      chip.append(document.createTextNode(term));
      const remove = document.createElement('button');
      remove.type = 'button';
      remove.textContent = '×';
      remove.setAttribute('aria-label', `Remove ${term}`);
      remove.addEventListener('click', () => {
        selected = selected.filter(value => value !== term);
        render();
        status.textContent = `${term} removed.`;
        input.focus();
      });
      chip.append(remove);
      tags.append(chip);
    });
  }
  function add() {
    const terms = input.value.split(',').map(normalize).filter(Boolean);
    if (terms.some(term => term.length > 100)) return false;
    selected = [...new Set([...selected, ...terms])];
    input.value = '';
    suggestions.replaceChildren();
    render();
    if (terms.length) status.textContent = 'Allergy added. Save profile to keep your changes.';
    return true;
  }
  selected = [...new Set(stored.value.split(',').map(normalize).filter(Boolean))];
  stored.type = 'hidden';
  stored.before(tags, input, suggestions, status);
  const label = form.querySelector('label[for="id_allergies"]');
  if (label) label.htmlFor = input.id;
  render();
  input.addEventListener('keydown', event => {
    if (event.isComposing) return;
    if (event.key === 'Enter' || event.key === ',') {
      event.preventDefault();
      add();
    }
  });
  form.addEventListener('submit', event => {
    if (!add()) event.preventDefault();
  });
  let timer;
  let controller;
  input.addEventListener('input', () => {
    clearTimeout(timer);
    if (controller) controller.abort();
    suggestions.replaceChildren();
    const query = input.value.trim();
    if (!query) return;
    timer = setTimeout(async () => {
      controller = new AbortController();
      try {
        const url = new URL(endpoint, window.location.origin);
        url.searchParams.set('q', query);
        const response = await fetch(url, {signal: controller.signal});
        if (!response.ok) throw new Error('Suggestions unavailable');
        const data = await response.json();
        if (input.value.trim() !== query) return;
        suggestions.replaceChildren(...data.results.filter(term => !selected.includes(term)).map(term => {
          const option = document.createElement('option');
          option.value = term;
          return option;
        }));
      } catch (error) {
        if (error.name !== 'AbortError') status.textContent = 'Suggestions unavailable. You can still add a term with Enter.';
      }
    }, 150);
  });
})();
