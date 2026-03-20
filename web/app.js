// ── Tab Switching ─────────────────────────────────────────────────────────────
function showTab(name) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  event.currentTarget.classList.add('active');
  if (name === 'about') loadKMStatus();
}

// ── Security Level Selection ──────────────────────────────────────────────────
document.querySelectorAll('.security-option').forEach(opt => {
  opt.addEventListener('click', () => {
    document.querySelectorAll('.security-option').forEach(o => o.classList.remove('selected'));
    opt.classList.add('selected');
  });
});

// ── KM Status Polling ─────────────────────────────────────────────────────────
async function checkKMStatus() {
  try {
    const res = await fetch('/api/v1/km/status');
    const data = await res.json();
    const dot = document.getElementById('kmDot');
    const text = document.getElementById('kmText');
    if (data.status === 'operational') {
      dot.className = 'km-dot online';
      text.textContent = `KM Online · ${data.available_keys} keys`;
    } else {
      dot.className = 'km-dot offline';
      text.textContent = 'KM Offline';
    }
  } catch {
    document.getElementById('kmDot').className = 'km-dot offline';
    document.getElementById('kmText').textContent = 'KM Error';
  }
}
checkKMStatus();
setInterval(checkKMStatus, 10000);

async function loadKMStatus() {
  try {
    const res = await fetch('/api/v1/km/status');
    const data = await res.json();
    document.getElementById('kmInfo').textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    document.getElementById('kmInfo').textContent = 'Error loading KM status: ' + e.message;
  }
}

// ── Send Email ────────────────────────────────────────────────────────────────
async function sendEmail() {
  const senderEmail = document.getElementById('senderEmail').value.trim();
  const appPassword = document.getElementById('appPassword').value.trim();
  const recipient = document.getElementById('recipient').value.trim();
  const subject = document.getElementById('subject').value.trim();
  const message = document.getElementById('message').value.trim();
  const secLevel = document.querySelector('input[name="secLevel"]:checked').value;

  if (!senderEmail || !appPassword || !recipient || !subject || !message) {
    showResult('error', '⚠️ Please fill in all fields.');
    return;
  }

  const btn = document.getElementById('sendBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Encrypting & Sending...';

  try {
    const res = await fetch('/api/v1/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sender_email: senderEmail, app_password: appPassword, recipient, subject, message, security_level: secLevel }),
    });
    const data = await res.json();

    if (data.success) {
      showResult('success', buildSuccessHTML(data));
    } else {
      showResult('error', `<p class="result-title">❌ Error</p><p>${escHtml(data.message)}</p>`);
    }
  } catch (e) {
    showResult('error', `<p class="result-title">❌ Network Error</p><p>${e.message}</p>`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '🚀 Send Secure Email';
  }
}

function buildSuccessHTML(data) {
  return `
    <p class="result-title">✅ Email Sent Successfully!</p>
    <p style="font-size:0.85rem;color:var(--text-muted);margin-bottom:14px;">${escHtml(data.message)}</p>
    <div class="detail-row"><span class="detail-label">Security Level:</span><span>${escHtml(data.security_level)}</span></div>
    <div class="detail-row"><span class="detail-label">Algorithm:</span><span>${escHtml(data.algorithm)}</span></div>
    <div class="detail-row"><span class="detail-label">Key ID:</span><span style="font-family:monospace;font-size:0.78rem">${escHtml(data.key_id)}</span></div>
    <p style="margin-top:14px;font-size:0.82rem;font-weight:600;color:var(--primary-light);">🔑 Encryption Key (click to copy — save this!):</p>
    <div class="key-box" onclick="copyKey(this, '${escHtml(data.key_hex)}')">${escHtml(data.key_hex)}</div>
    <p class="copy-hint">⚠️ Share this key securely with your recipient to allow decryption.</p>
  `;
}

async function copyKey(el, key) {
  try {
    await navigator.clipboard.writeText(key);
    const orig = el.textContent;
    el.textContent = '✅ Copied!';
    setTimeout(() => el.textContent = orig, 2000);
  } catch {
    el.textContent = 'Copy manually';
  }
}

function showResult(type, html) {
  const panel = document.getElementById('resultPanel');
  panel.style.display = 'block';
  panel.className = 'result-panel ' + type;
  document.getElementById('resultContent').innerHTML = html;
  panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ── Decrypt ───────────────────────────────────────────────────────────────────
async function decryptEmail() {
  const body = document.getElementById('encryptedBody').value.trim();
  const keyHex = document.getElementById('decryptKey').value.trim();

  if (!body || !keyHex) {
    showDecryptResult('error', '⚠️ Please provide both the email body and encryption key.');
    return;
  }

  try {
    const res = await fetch('/api/v1/decrypt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email_body: body, key_hex: keyHex }),
    });
    const data = await res.json();

    if (data.success) {
      showDecryptResult('success', `
        <p class="result-title">✅ Decryption Successful!</p>
        <div class="detail-row"><span class="detail-label">Security Level:</span><span>${escHtml(data.security_level)}</span></div>
        <p style="margin-top:12px;font-size:0.82rem;font-weight:600;color:var(--primary-light);">📧 Decrypted Message:</p>
        <div class="key-box" style="color:var(--text);font-family:inherit;word-break:normal;white-space:pre-wrap">${escHtml(data.plaintext)}</div>
      `);
    } else {
      showDecryptResult('error', `<p class="result-title">❌ Decryption Failed</p><p>${escHtml(data.message)}</p>`);
    }
  } catch (e) {
    showDecryptResult('error', `<p class="result-title">❌ Error</p><p>${e.message}</p>`);
  }
}

function showDecryptResult(type, html) {
  const panel = document.getElementById('decryptResult');
  panel.style.display = 'block';
  panel.className = 'result-panel ' + type;
  document.getElementById('decryptContent').innerHTML = html;
}

// ── Inbox ─────────────────────────────────────────────────────────────────────
async function fetchInbox() {
  const email = document.getElementById('inboxEmail').value.trim();
  const password = document.getElementById('inboxPassword').value.trim();

  if (!email || !password) {
    alert('Please enter email and password.');
    return;
  }

  const list = document.getElementById('inboxList');
  list.innerHTML = '<div class="loading"><span class="spinner"></span> Fetching inbox...</div>';

  try {
    const res = await fetch('/api/v1/inbox', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, app_password: password }),
    });
    const data = await res.json();

    if (!data.success) {
      list.innerHTML = `<div class="result-panel error"><p>${escHtml(data.message)}</p></div>`;
      return;
    }

    if (!data.emails.length) {
      list.innerHTML = '<div class="loading">No emails found.</div>';
      return;
    }

    list.innerHTML = data.emails.map(em => `
      <div class="inbox-item ${em.is_qumail ? 'qumail' : ''}">
        <div class="inbox-subject">
          ${escHtml(em.subject)}
          ${em.is_qumail ? '<span class="inbox-badge">🔐 QuMail</span>' : ''}
        </div>
        <div class="inbox-from">From: ${escHtml(em.from)}</div>
      </div>
    `).join('');
  } catch (e) {
    list.innerHTML = `<div class="result-panel error"><p>${e.message}</p></div>`;
  }
}

// ── Util ──────────────────────────────────────────────────────────────────────
function escHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
