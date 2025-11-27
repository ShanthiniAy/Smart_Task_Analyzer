const tasks = [];
const resultsEl = document.getElementById('results');

document.getElementById('task-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const t = {
    id: Date.now().toString(),
    title: document.getElementById('title').value,
    due_date: document.getElementById('due_date').value || null,
    estimated_hours: parseFloat(document.getElementById('estimated_hours').value || 1),
    importance: parseInt(document.getElementById('importance').value || 5),
    dependencies: (document.getElementById('dependencies').value || "").split(',').map(s => s.trim()).filter(Boolean)
  };
  tasks.push(t);
  renderLocalList();
  e.target.reset();
});

function renderLocalList(){
  const out = document.createElement('div');
  out.innerHTML = '<h3>Local tasks</h3>';
  tasks.forEach(t=>{
    const d = document.createElement('div');
    d.className = 'task-item';
    d.textContent = `${t.title} — due: ${t.due_date || 'none'} — est: ${t.estimated_hours}h — imp: ${t.importance}`;
    out.appendChild(d);
  });
  const container = document.getElementById('results');
  container.innerHTML = '';
  container.appendChild(out);
}

async function callAnalyze(endpoint){
  let payload = tasks.slice();
  const bulkText = document.getElementById('bulk').value.trim();
  if (bulkText){
    try {
      const bulk = JSON.parse(bulkText);
      if (Array.isArray(bulk)) payload = bulk;
    } catch (err){
      alert('Bulk JSON invalid');
      return;
    }
  }
  const strategy = document.getElementById('strategy').value;
  const resp = await fetch(`/api/tasks/analyze/?strategy=${strategy}`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  });
  if (!resp.ok){
    const err = await resp.json();
    alert('Error: ' + (err.error || JSON.stringify(err)));
    return;
  }
  const data = await resp.json();
  showResults(data.tasks);
}

async function callSuggest(){
  let payload = tasks.slice();
  const bulkText = document.getElementById('bulk').value.trim();
  if (bulkText){
    try {
      const bulk = JSON.parse(bulkText);
      if (Array.isArray(bulk)) payload = bulk;
    } catch (err){
      alert('Bulk JSON invalid');
      return;
    }
  }
  const strategy = document.getElementById('strategy').value;
  const resp = await fetch(`/api/tasks/suggest/?strategy=${strategy}`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  });
  if (!resp.ok){
    const err = await resp.json();
    alert('Error: ' + (err.error || JSON.stringify(err)));
    return;
  }
  const data = await resp.json();
  showSuggestions(data.suggestions);
}

function showResults(list){
  const container = document.getElementById('results');
  container.innerHTML = '<h3>Analyzed tasks</h3>';
  list.forEach(t=>{
    const el = document.createElement('div');
    el.className = 'analyzed';
    let level = 'low';
    if (t.score >= 0.6) level = 'high';
    else if (t.score >= 0.4) level = 'medium';
    el.innerHTML = `<strong>${t.title}</strong> — score: ${t.score} <span class="badge ${level}">${level.toUpperCase()}</span>
      <div>${t.reason}</div>
      <div class="small">due: ${t.due_date || 'none'} — est: ${t.estimated_hours}h — imp: ${t.importance}</div>`;
    container.appendChild(el);
  });
}

function showSuggestions(suggestions){
  const container = document.getElementById('results');
  container.innerHTML = '<h3>Top Suggestions</h3>';
  suggestions.forEach(s=>{
    const t = s.task;
    const el = document.createElement('div');
    el.className = 'suggestion';
    el.innerHTML = `<strong>${t.title}</strong> — score: ${t.score}
      <div>${s.explanation}</div>`;
    container.appendChild(el);
  });
}

document.getElementById('analyze').addEventListener('click', ()=>callAnalyze());
document.getElementById('suggest').addEventListener('click', ()=>callSuggest());
