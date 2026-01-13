const out = document.getElementById('out');
const status = document.getElementById('status');
const meta = document.getElementById('meta');
const urlEl = document.getElementById('url');
const go = document.getElementById('go');

function setStatus(text, kind='ok'){
  const t = status.querySelector('.status-text') || status;
  t.textContent = text;

  status.classList.remove('is-working','is-error');
  if(kind === 'work') status.classList.add('is-working');
  if(kind === 'err') status.classList.add('is-error');
}

function esc(s){
  return (s ?? '').toString()
    .replaceAll('&','&amp;')
    .replaceAll('<','&lt;')
    .replaceAll('>','&gt;');
}

function metaHtml(cache, timing){
  const total = timing.total ?? 0;
  const parse = timing.parse ?? 0;
  const ai = timing.ai ?? 0;

  return `
    <span>${esc(cache)}</span>
    <span> • total <span class="sec">${total}ms</span></span>
    <span> • parse <span class="sec">${parse}ms</span></span>
    <span> • ai <span class="sec">${ai}ms</span></span>
  `;
}

function render(data){
  const sum = data.summary || {};
  const title = sum.title || 'Без заголовка';
  const bullets = Array.isArray(sum.bullets) ? sum.bullets : [];
  const takeaway = sum.takeaway || '';
  const tags = Array.isArray(sum.tags) ? sum.tags : [];

  const timing = data.timing_ms || {};
  const cache = data.cache_hit ? 'cache' : 'fresh';

  meta.innerHTML = metaHtml(cache, timing);

  out.innerHTML = `
    <div class="block">
      <div class="title">
        <span>Источник</span>
        <span class="pill">${esc(cache)}</span>
      </div>
      <div class="card2">
        <a href="${esc(data.source)}" target="_blank" rel="noreferrer">${esc(data.source)}</a>
        <div class="muted" style="margin-top:6px">${data.chars ?? 0} chars</div>
      </div>
    </div>

    <div class="block">
      <div class="title">
        <span>Заголовок</span>
        <span class="pill">title</span>
      </div>
      <div class="card2">${esc(title)}</div>
    </div>

    <div class="block">
      <div class="title">
        <span>Ключевые пункты</span>
        <span class="pill">${bullets.length} bullets</span>
      </div>
      <div class="card2">
        ${bullets.length ? `<ul>${bullets.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>` : `<span class="muted">Нет пунктов</span>`}
      </div>
    </div>

    <div class="block">
      <div class="title">
        <span>Вывод</span>
        <span class="pill">takeaway</span>
      </div>
      <div class="card2">${takeaway ? esc(takeaway) : `<span class="muted">Нет вывода</span>`}</div>
    </div>

    <div class="block">
      <div class="title">
        <span>Теги</span>
        <span class="pill">${tags.length} tags</span>
      </div>
      <div class="card2">
        <div class="kpi">
          ${tags.length ? tags.map(t=>`<span class="pill">${esc(t)}</span>`).join('') : `<span class="muted">Нет тегов</span>`}
        </div>
      </div>
    </div>
  `;
}

async function run(){
  const url = urlEl.value.trim();
  if(!url) return;

  go.disabled = true;
  setStatus('working', 'work');

  try {
    const r = await fetch('/summarize', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({url})
    });

    if(!r.ok){
      const err = await r.json().catch(()=>({detail:`HTTP ${r.status}`}));
      throw new Error(err.detail || `HTTP ${r.status}`);
    }

    const data = await r.json();
    render(data);
    setStatus('ready');
  } catch(e){
    meta.textContent = '';
    out.innerHTML = `
      <div class="block">
        <div class="title"><span>Ошибка</span><span class="pill">error</span></div>
        <div class="card2 err">${esc(e.message || e)}</div>
      </div>
    `;
    setStatus('error','err');
  } finally {
    go.disabled = false;
  }
}

go.addEventListener('click', run);
urlEl.addEventListener('keydown', (e)=>{
  if(e.key === 'Enter') run();
});

