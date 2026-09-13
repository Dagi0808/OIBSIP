'use strict';

// ── State ────────────────────────────────────────────────────────────────────
let socket;
let currentRoom = 'General';
const AVATAR_COLORS = [
  '#5865f2','#3ba55c','#faa61a','#ed4245',
  '#eb459e','#57f287','#fee75c','#5865f2',
];

function avatarColor(username) {
  let hash = 0;
  for (let i = 0; i < username.length; i++) hash += username.charCodeAt(i);
  return AVATAR_COLORS[hash % AVATAR_COLORS.length];
}

// ── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  socket = io();

  // Auto-resize textarea
  const input = document.getElementById('msg-input');
  input.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 140) + 'px';
  });

  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Request desktop notification permission
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
  }

  // Join initial room
  joinRoom('General');

  // ── Socket events ──────────────────────────────────────────────────────────

  socket.on('history', function (data) {
    if (data.room !== currentRoom) return;
    const msgs = document.getElementById('messages');
    msgs.innerHTML = '';
    data.messages.forEach(function (m) {
      appendMessage(m.username, m.content, m.timestamp, false);
    });
    scrollToBottom();
  });

  socket.on('message', function (data) {
    if (data.room !== currentRoom) return;
    appendMessage(data.username, data.content, data.timestamp, true);
    scrollToBottom();

    // Desktop notification when window not focused
    if (document.hidden && data.username !== USERNAME) {
      showNotification(data.username, data.content, data.room);
    }
  });

  socket.on('status', function (data) {
    if (data.room !== currentRoom) return;
    appendStatus(data.msg);
    updateOnlineList(data.online || []);
    scrollToBottom();
  });
});

// ── Room management ───────────────────────────────────────────────────────────
function joinRoom(room) {
  if (currentRoom && currentRoom !== room) {
    socket.emit('leave', { room: currentRoom });
  }

  currentRoom = room;

  // Update UI
  document.getElementById('room-name').textContent = room;
  document.getElementById('room-desc').textContent = 'Welcome to the ' + room + ' channel';
  document.getElementById('msg-input').placeholder = 'Message #' + room;
  const msgs = document.getElementById('messages');
  msgs.innerHTML = '<div class="empty-state" id="empty-state">' +
    '<div class="empty-icon">💬</div>' +
    '<div class="empty-title">Welcome to #' + room + '</div>' +
    '<div class="empty-sub">This is the beginning of the conversation. Say hello!</div>' +
    '</div>';

  // Highlight active room in sidebar
  document.querySelectorAll('.room-item').forEach(function (el) {
    el.classList.toggle('active', el.dataset.room === room);
  });

  socket.emit('join', { room: room });
}

function switchRoom(room) {
  if (room === currentRoom) return;
  joinRoom(room);
}

function openCreateRoom() {
  document.getElementById('create-room-modal').classList.add('open');
  document.getElementById('new-room-input').focus();
}

function closeCreateRoom() {
  document.getElementById('create-room-modal').classList.remove('open');
  document.getElementById('new-room-input').value = '';
}

function submitCreateRoom() {
  const name = document.getElementById('new-room-input').value.trim();
  if (!name) return;

  fetch('/create-room', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'room_name=' + encodeURIComponent(name),
  }).then(function () {
    // Add to sidebar if not already there
    const list = document.getElementById('room-list');
    const exists = Array.from(list.querySelectorAll('.room-item'))
      .some(function (el) { return el.dataset.room === name; });

    if (!exists) {
      const el = document.createElement('div');
      el.className = 'room-item';
      el.dataset.room = name;
      el.onclick = function () { switchRoom(name); };
      el.textContent = name;
      list.appendChild(el);
    }

    closeCreateRoom();
    switchRoom(name);
  });
}

// ── Messaging ─────────────────────────────────────────────────────────────────
function sendMessage() {
  const input = document.getElementById('msg-input');
  const content = input.value.trim();
  if (!content) return;

  socket.emit('message', { room: currentRoom, content: content });
  input.value = '';
  input.style.height = 'auto';
  input.focus();
}

// ── Render helpers ─────────────────────────────────────────────────────────────
function appendMessage(username, content, timestamp, animate) {
  const msgs = document.getElementById('messages');

  // Remove empty state
  const empty = document.getElementById('empty-state');
  if (empty) empty.remove();

  const isOwn = username === USERNAME;
  const row = document.createElement('div');
  row.className = 'msg-row' + (isOwn ? ' own' : '');

  const color = avatarColor(username);
  row.innerHTML =
    '<div class="msg-avatar" style="background:' + color + '">' +
    escapeHtml(username[0].toUpperCase()) + '</div>' +
    '<div class="msg-body">' +
    '<div class="msg-meta">' +
    '<span class="msg-username" style="color:' + color + '">' + escapeHtml(username) + '</span>' +
    '<span class="msg-time">' + escapeHtml(timestamp) + '</span>' +
    '</div>' +
    '<div class="msg-content">' + escapeHtml(content) + '</div>' +
    '</div>';

  msgs.appendChild(row);
}

function appendStatus(msg) {
  const msgs = document.getElementById('messages');
  const el = document.createElement('div');
  el.className = 'status-line';
  el.textContent = msg;
  msgs.appendChild(el);
}

function updateOnlineList(users) {
  const list = document.getElementById('online-list');
  const count = document.getElementById('online-num');
  const badge = document.getElementById('online-count');

  list.innerHTML = '';
  users.forEach(function (u) {
    const color = avatarColor(u);
    const el = document.createElement('div');
    el.className = 'online-user';
    el.innerHTML =
      '<div class="online-avatar" style="background:' + color + '">' +
      escapeHtml(u[0].toUpperCase()) +
      '<div class="online-dot"></div></div>' +
      '<span class="online-username">' + escapeHtml(u) + '</span>';
    list.appendChild(el);
  });

  count.textContent = users.length;
  badge.textContent = users.length + ' online';
}

function scrollToBottom() {
  const msgs = document.getElementById('messages');
  msgs.scrollTop = msgs.scrollHeight;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// ── Desktop notifications ─────────────────────────────────────────────────────
function showNotification(username, content, room) {
  if (!('Notification' in window) || Notification.permission !== 'granted') return;
  new Notification(username + ' in #' + room, {
    body: content.length > 80 ? content.slice(0, 80) + '…' : content,
    icon: '/static/icon.png',
  });
}

// ── CSS animation ─────────────────────────────────────────────────────────────
const style = document.createElement('style');
style.textContent = '@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }';
document.head.appendChild(style);
