/* ================================================================
   app.js  —  RAG 课程知识智能检索系统
   백엔드: Flask @ http://127.0.0.1:5001
   ================================================================ */

/* ── 백엔드 주소 자동 감지 ── */
const API_BASE = (window.location.port === '5001')
  ? ''
  : 'http://127.0.0.1:5001';

/* ── 상수 & 상태 ── */
const PIPELINE_STEPS = ['step-embed','step-search','step-topk','step-prompt','step-llm'];
let topK = 3;
let isProcessing = false;
let messageCount = 0;

/* ================================================================
   페이지 로드 시 백엔드 문서 목록 동기화
   ================================================================ */
async function loadDocumentsFromBackend() {
  try {
    const res  = await fetch(`${API_BASE}/api/documents`);
    if (!res.ok) return;
    const docs = await res.json();
    const list = document.getElementById('doc-list');
    list.innerHTML = '';
    let totalChunks = 0;

    docs.forEach(doc => {
      totalChunks += doc.chunks || 0;
      const type = doc.type === 'pdf' ? 'pdf' : 'txt';
      const item = document.createElement('div');
      item.className = 'doc-item';
      item.dataset.name   = doc.name;
      item.dataset.type   = type;
      item.dataset.chunks = doc.chunks;
      item.dataset.size   = doc.size_mb + 'MB';
      item.setAttribute('onclick','openFilePreview(this)');
      item.innerHTML = `
        <div class="doc-icon ${type}">${type.toUpperCase()}</div>
        <div class="doc-meta">
          <div class="doc-name">${doc.name}</div>
          <div class="doc-size">${doc.chunks} chunks · ${doc.size_mb}MB</div>
        </div>
        <div class="doc-status"></div>
      `;
      list.appendChild(item);
    });

    document.getElementById('stat-docs').textContent   = docs.length;
    document.getElementById('stat-chunks').textContent = totalChunks;
  } catch (e) {
    console.warn('백엔드 연결 실패, 목업 유지:', e);
  }
}

window.addEventListener('load', loadDocumentsFromBackend);

/* ================================================================
   유틸리티
   ================================================================ */
function getTime() {
  return new Date().toLocaleTimeString('zh-CN', {hour:'2-digit', minute:'2-digit'});
}
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function scrollToBottom() {
  const a = document.getElementById('chat-area');
  a.scrollTop = a.scrollHeight;
}

/* ================================================================
   입력창
   ================================================================ */
function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 160) + 'px';
}
function handleKeyDown(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendQuery(); }
}
function fillSuggestion(el) {
  document.getElementById('query-input').value = el.textContent;
  document.getElementById('welcome').style.display = 'none';
  sendQuery();
}

/* ================================================================
   설정 칩
   ================================================================ */
function toggleChip(el) { el.classList.toggle('active'); }
function cycleTopK(el) {
  const opts = [1,3,5];
  topK = opts[(opts.indexOf(topK)+1) % opts.length];
  el.textContent = 'Top-K: ' + topK;
}

/* ================================================================
   파일 업로드 — 실제 백엔드 전송
   ================================================================ */
function handleFileUpload(e) {
  const files = Array.from(e.target.files);
  files.forEach(f => uploadFile(f));
  e.target.value = '';
}

async function uploadFile(file) {
  const list = document.getElementById('doc-list');

  /* 업로드 중 placeholder */
  const placeholder = document.createElement('div');
  placeholder.className = 'doc-item';
  placeholder.style.opacity = '0.5';
  placeholder.innerHTML = `
    <div class="doc-icon txt">···</div>
    <div class="doc-meta">
      <div class="doc-name">${file.name}</div>
      <div class="doc-size">上传中...</div>
    </div>
  `;
  list.appendChild(placeholder);

  try {
    const form = new FormData();
    form.append('file', file);
    const res  = await fetch(`${API_BASE}/api/upload`, { method:'POST', body: form });
    const data = await res.json();

    if (data.error) throw new Error(data.error);

    /* placeholder → 실제 아이템으로 교체 */
    const type = data.type === 'pdf' ? 'pdf' : 'txt';
    placeholder.style.opacity = '1';
    placeholder.dataset.name   = data.filename;
    placeholder.dataset.type   = type;
    placeholder.dataset.chunks = data.chunks;
    placeholder.dataset.size   = data.size_mb + 'MB';
    placeholder.setAttribute('onclick','openFilePreview(this)');
    placeholder.innerHTML = `
      <div class="doc-icon ${type}">${type.toUpperCase()}</div>
      <div class="doc-meta">
        <div class="doc-name">${data.filename}</div>
        <div class="doc-size">${data.chunks} chunks · ${data.size_mb}MB</div>
      </div>
      <div class="doc-status"></div>
    `;

    document.getElementById('stat-chunks').textContent = data.total_chunks;
    document.getElementById('stat-docs').textContent   = data.total_docs;

  } catch (err) {
    placeholder.remove();
    alert(`上传失败：${err.message}`);
  }
}

/* ================================================================
   파이프라인 애니메이션
   ================================================================ */
function resetPipeline() {
  PIPELINE_STEPS.forEach(id => document.getElementById(id).className = 'pipe-step idle');
}
function setStepClass(id, cls) {
  if (id) document.getElementById(id).className = `pipe-step ${cls}`;
}
function activateStep(id) {
  document.getElementById(id).className = 'pipe-step active';
}
async function animatePipeline() {
  for (let i = 0; i < PIPELINE_STEPS.length; i++) {
    if (i > 0) setStepClass(PIPELINE_STEPS[i-1], 'done');
    activateStep(PIPELINE_STEPS[i]);
    await sleep(500);
  }
  setStepClass(PIPELINE_STEPS[PIPELINE_STEPS.length-1], 'done');
}

/* ================================================================
   메시지 렌더링
   ================================================================ */
function appendUserMessage(query, t) {
  const el = document.createElement('div');
  el.className = 'msg user';
  el.innerHTML = `
    <div class="msg-avatar">U</div>
    <div class="msg-content">
      <div class="msg-header">
        <span class="msg-name">用户</span>
        <span class="msg-time">${t}</span>
      </div>
      <div class="msg-bubble">${escapeHtml(query)}</div>
    </div>
  `;
  document.getElementById('messages').appendChild(el);
}

function appendThinkingMessage(t, bubbleId) {
  const el = document.createElement('div');
  el.className = 'msg ai';
  el.innerHTML = `
    <div class="msg-avatar">AI</div>
    <div class="msg-content">
      <div class="msg-header">
        <span class="msg-name">知识检索系统</span>
        <span class="msg-time">${t}</span>
      </div>
      <div class="msg-bubble" id="${bubbleId}">
        <div class="thinking"><span></span><span></span><span></span></div>
      </div>
    </div>
  `;
  document.getElementById('messages').appendChild(el);
}

function renderAnswer(bubble, resp) {
  if (resp.error) {
    bubble.innerHTML = `<div style="color:var(--red);">⚠️ 请求失败：${escapeHtml(resp.error)}</div>`;
    return;
  }
  bubble.innerHTML = `<div style="white-space:pre-wrap;">${escapeHtml(resp.answer)}</div>`;

  if (resp.sources && resp.sources.length > 0) {
    const srcDiv = document.createElement('div');
    srcDiv.className = 'sources';
    srcDiv.innerHTML = `<div class="sources-label">📄 检索来源 (Top-${resp.sources.length})</div>`;
    resp.sources.forEach(s => {
      const card = document.createElement('div');
      card.className = 'source-card';
      card.innerHTML = `
        <div class="source-top">
          <span class="source-file">${escapeHtml(s.file)}</span>
          <span class="source-score">sim: ${s.score}</span>
        </div>
        <div class="source-text">${escapeHtml(s.text)}</div>
      `;
      srcDiv.appendChild(card);
    });
    bubble.appendChild(srcDiv);
  }
}

function renderChunks(sources) {
  const panel = document.getElementById('chunks-panel');
  if (!sources || sources.length === 0) return;
  panel.innerHTML = '';
  sources.forEach((s, i) => {
    const pct  = Math.round(parseFloat(s.score) * 100);
    const card = document.createElement('div');
    card.className = 'chunk-card';
    card.innerHTML = `
      <div class="chunk-top">
        <span class="chunk-id">chunk_${String(i+1).padStart(3,'0')}</span>
        <span class="chunk-sim">${s.score}</span>
      </div>
      <div class="chunk-text">${escapeHtml(s.text)}</div>
      <div class="sim-bar"><div class="sim-fill" style="width:${pct}%"></div></div>
    `;
    panel.appendChild(card);
  });
}

/* ================================================================
   메인: 질문 전송 — 실제 백엔드 호출
   ================================================================ */
async function sendQuery() {
  if (isProcessing) return;

  const input = document.getElementById('query-input');
  const query = input.value.trim();
  if (!query) return;

  isProcessing = true;
  document.getElementById('send-btn').disabled = true;
  document.getElementById('welcome').style.display = 'none';
  input.value = '';
  input.style.height = 'auto';

  const t        = getTime();
  const bubbleId = `ai-bubble-${messageCount++}`;

  appendUserMessage(query, t);
  appendThinkingMessage(t, bubbleId);
  scrollToBottom();

  resetPipeline();
  document.getElementById('chunks-panel').innerHTML =
    `<div style="color:var(--text3);font-size:12px;text-align:center;padding:20px;font-family:var(--mono);">检索中...</div>`;

  /* 파이프라인 애니메이션과 실제 API 호출을 병렬로 */
  const [resp] = await Promise.all([
    fetch(`${API_BASE}/api/query`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ query, top_k: topK })
    }).then(r => r.json()).catch(err => ({ error: err.message })),
    animatePipeline()
  ]);

  const bubble = document.getElementById(bubbleId);
  renderAnswer(bubble, resp);
  renderChunks(resp.sources);
  scrollToBottom();

  isProcessing = false;
  document.getElementById('send-btn').disabled = false;
}

/* ================================================================
   홈으로 돌아가기
   ================================================================ */
function goHome() {
  document.getElementById('messages').innerHTML = '';
  document.getElementById('welcome').style.display = 'flex';
  document.getElementById('query-input').value = '';
  document.getElementById('query-input').style.height = 'auto';
  resetPipeline();
  document.getElementById('chunks-panel').innerHTML =
    `<div style="color:var(--text3);font-size:12px;text-align:center;padding:20px;font-family:var(--mono);">等待检索...</div>`;
  isProcessing = false;
  document.getElementById('send-btn').disabled = false;
}

/* ================================================================
   파일 미리보기 모달 — 백엔드에서 실제 청크 로드
   ================================================================ */
async function openFilePreview(el) {
  const name   = el.dataset.name;
  const type   = el.dataset.type || 'txt';
  const chunks = el.dataset.chunks || '?';
  const size   = el.dataset.size   || '?';

  const icon = document.getElementById('modal-icon');
  icon.textContent = type.toUpperCase();
  icon.className   = `doc-icon ${type}`;
  document.getElementById('modal-filename').textContent = name;
  document.getElementById('modal-meta').textContent     = `${chunks} 个文本块 · ${size}`;

  const body = document.getElementById('modal-body');
  body.innerHTML = `<div style="color:var(--text3);font-size:12px;text-align:center;padding:24px;font-family:var(--mono);">加载中...</div>`;
  document.getElementById('modal-footer').textContent = `共 ${chunks} 个文本块已索引 · ${size} · 可直接检索`;
  document.getElementById('modal-overlay').classList.add('open');
  document.body.style.overflow = 'hidden';

  /* 백엔드에서 해당 파일의 청크 가져오기 */
  try {
    const res  = await fetch(`${API_BASE}/api/chunks?file=${encodeURIComponent(name)}&limit=5`);
    const data = await res.json();
    body.innerHTML = '';

    if (data.chunks && data.chunks.length > 0) {
      data.chunks.forEach((text, i) => {
        const div = document.createElement('div');
        div.className = 'modal-chunk';
        div.innerHTML = `<div class="modal-chunk-num">chunk_${String(i+1).padStart(3,'0')}</div>${escapeHtml(text)}`;
        body.appendChild(div);
      });
    } else {
      body.innerHTML = `<div style="color:var(--text3);font-size:13px;text-align:center;padding:24px;font-family:var(--mono);">暂无预览数据</div>`;
    }
  } catch {
    body.innerHTML = `<div style="color:var(--text3);font-size:13px;text-align:center;padding:24px;font-family:var(--mono);">暂无预览数据</div>`;
  }
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('open');
  document.body.style.overflow = '';
}
function closeModalOnOverlay(e) {
  if (e.target === document.getElementById('modal-overlay')) closeModal();
}
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
