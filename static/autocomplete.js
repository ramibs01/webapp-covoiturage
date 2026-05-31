const CITIES = [
  "Ariana","Beja","Ben Arous","Bizerte","Gabès","Gafsa","Jendouba","Kairouan",
  "Kasserine","Kébili","Kef","Mahdia","Manouba","Médenine","Monastir",
  "Nabeul","Sfax","Sidi Bouzid","Siliana","Sousse","Tataouine","Tozeur",
  "Tunis","Zaghouan","Hammamet","Djerba","Zarzis","Tabarka","Korba",
  "Kelibia","La Goulette","Carthage","La Marsa","Ben Gardane","Douz","Nefta"
];

function normalize(s) {
  return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

function setupAutocomplete(inputId, boxId) {
  const input = document.getElementById(inputId);
  const box = document.getElementById(boxId);
  let selected = -1;

  function showSuggestions(matches) {
    if (!matches.length) { box.classList.add('hidden'); return; }
    selected = -1;
    box.innerHTML = matches.map((city, i) =>
      `<div class="sug-item px-4 py-2 text-sm cursor-pointer hover:bg-slate-100 flex items-center gap-2 border-b border-slate-100 last:border-0" data-idx="${i}" data-val="${city}">
        <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
        ${city}
      </div>`
    ).join('');
    box.classList.remove('hidden');

    box.querySelectorAll('.sug-item').forEach(el => {
      el.addEventListener('mousedown', e => {
        e.preventDefault();
        input.value = el.dataset.val;
        box.classList.add('hidden');
      });
    });
  }

  // Show all cities on focus/click if input is empty
  input.addEventListener('focus', () => {
    const q = input.value.trim();
    const matches = q
      ? CITIES.filter(c => normalize(c).startsWith(normalize(q)))
      : [...CITIES];
    showSuggestions(matches);
  });

  input.addEventListener('click', () => {
    const q = input.value.trim();
    const matches = q
      ? CITIES.filter(c => normalize(c).startsWith(normalize(q)))
      : [...CITIES];
    showSuggestions(matches);
  });

  // Filter as user types
  input.addEventListener('input', () => {
    const q = input.value.trim();
    const matches = q
      ? CITIES.filter(c => normalize(c).startsWith(normalize(q)))
      : [...CITIES];
    showSuggestions(matches);
  });

  // Keyboard navigation
  input.addEventListener('keydown', e => {
    const items = box.querySelectorAll('.sug-item');
    if (!items.length) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      highlight(Math.min(selected + 1, items.length - 1), items);
      items[selected]?.scrollIntoView({ block: 'nearest' });
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      highlight(Math.max(selected - 1, 0), items);
      items[selected]?.scrollIntoView({ block: 'nearest' });
    } else if (e.key === 'Enter' && selected >= 0) {
      e.preventDefault();
      input.value = items[selected].dataset.val;
      box.classList.add('hidden');
    } else if (e.key === 'Escape') {
      box.classList.add('hidden');
    }
  });

  function highlight(idx, items) {
    items.forEach(el => el.classList.remove('bg-slate-100'));
    items[idx].classList.add('bg-slate-100');
    selected = idx;
  }

  input.addEventListener('blur', () => setTimeout(() => box.classList.add('hidden'), 150));
}

setupAutocomplete('departure', 'departure-suggestions');
setupAutocomplete('destination', 'destination-suggestions');