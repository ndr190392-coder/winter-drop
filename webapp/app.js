const tg = window.Telegram.WebApp;
tg.expand();

const userId = tg.initDataUnsafe?.user?.id || 9090771899;
let currentCase = null;

async function loadUserData() {
    const res = await fetch(`/api/user?user_id=${userId}`);
    const data = await res.json();
    document.getElementById('balance').innerText = data.balance.toFixed(2);
    document.getElementById('username').innerText = tg.initDataUnsafe?.user?.first_name || "Игрок";
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.currentTarget.classList.add('active');
}

function selectCase(caseKey) {
    currentCase = caseKey;
    document.getElementById('roulette-modal').style.display = 'flex';
    document.getElementById('track').style.transform = 'translateX(0px)';
}

function closeModal() {
    document.getElementById('roulette-modal').style.display = 'none';
}

async function spin() {
    const btn = document.getElementById('spin-btn');
    btn.disabled = true;

    const res = await fetch('/api/open_case', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ user_id: userId, case_key: currentCase })
    });

    const data = await res.json();
    if (!data.success) {
        alert(data.msg);
        btn.disabled = false;
        return;
    }

    const track = document.getElementById('track');
    track.innerHTML = '';
    data.tape.forEach(item => {
        const div = document.createElement('div');
        div.className = `item-card ${item.rarity}`;
        div.innerHTML = `<div>${item.name}</div>`;
        track.appendChild(div);
    });

    const winIndex = data.tape.length - 6;
    const itemWidth = 100;
    const offset = -(winIndex * itemWidth - 150);

    setTimeout(() => {
        track.style.transform = `translateX(${offset}px)`;
    }, 100);

    setTimeout(() => {
        alert(`🎉 Вы выиграли: ${data.won_item.name}`);
        document.getElementById('balance').innerText = data.new_balance.toFixed(2);
        btn.disabled = false;
    }, 4500);
}

async function claimDaily() {
    const res = await fetch('/api/daily', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ user_id: userId })
    });
    const data = await res.json();
    alert(data.msg || `Получено: ${data.reward} ❄️!`);
    if(data.success) document.getElementById('balance').innerText = data.new_balance.toFixed(2);
}

async function linkSteam() {
    const steamId = document.getElementById('steam-input').value;
    if(!steamId) return alert('Введите SteamID!');
    
    const res = await fetch('/api/link_steam', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ user_id: userId, steam_id: steamId })
    });
    const data = await res.json();
    alert(data.msg);
}

loadUserData();