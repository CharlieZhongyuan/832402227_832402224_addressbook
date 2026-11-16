let editingId = null;

async function loadContacts() {
    const res = await fetch("/api/contacts");
    const data = await res.json();
    const list = document.getElementById("contact-list");
    list.innerHTML = "";
    data.contacts.forEach(c => {
        const card = document.createElement("div");
        card.className = "contact-card" + (c.is_favorite ? " favorite" : "");
        let methodsHtml = "";
        c.methods.forEach(m => {
            const label = {phone:"📞", email:"✉️", social:"🔗", address:"🏠"}[m.method_type] || "";
            methodsHtml += `<div>${label} ${m.method_value}</div>`;
        });
        card.innerHTML = `
            <div class="contact-header">
                <span class="contact-name">${c.name}</span>
                <button class="star" data-id="${c.id}" data-fav="${c.is_favorite}">
                    ${c.is_favorite ? "★" : "☆"}
                </button>
            </div>
            <div class="methods">${methodsHtml || "<i>暂无联系方式</i>"}</div>
            <div class="card-actions">
                <button class="btn small edit-btn" data-id="${c.id}">编辑</button>
                <button class="btn small danger del-btn" data-id="${c.id}">删除</button>
            </div>
        `;
        list.appendChild(card);
    });

    document.querySelectorAll(".star").forEach(b => {
        b.onclick = () => toggleFav(b.dataset.id);
    });
    document.querySelectorAll(".edit-btn").forEach(b => {
        b.onclick = () => openModal(b.dataset.id);
    });
    document.querySelectorAll(".del-btn").forEach(b => {
        b.onclick = () => deleteContact(b.dataset.id);
    });
}

async function toggleFav(id) {
    await fetch(`/api/contacts/${id}/favorite`, { method: "PATCH" });
    loadContacts();
}

async function deleteContact(id) {
    if (!confirm("确定删除这个联系人？")) return;
    await fetch(`/api/contacts/${id}`, { method: "DELETE" });
    loadContacts();
}
function openModal(id) {
    editingId = id;
    document.getElementById("modal").classList.remove("hidden");
    document.getElementById("methods-container").innerHTML = `
        <div class="method-row">
            <select class="method-type">
                <option value="phone">电话</option>
                <option value="email">邮箱</option>
                <option value="social">社交账号</option>
                <option value="address">地址</option>
            </select>
            <input type="text" class="method-value" placeholder="输入联系方式">
            <button class="btn small remove-method" type="button">×</button>
        </div>
    `;
    if (id) {
        document.getElementById("modal-title").textContent = "编辑联系人";
        const data = dataCache.find(c => c.id == id);
        if (data) {
            document.getElementById("input-name").value = data.name;
            document.getElementById("methods-container").innerHTML = "";
            data.methods.forEach(m => addMethodRow(m.method_type, m.method_value));
        }
    } else {
        document.getElementById("modal-title").textContent = "新建联系人";
        document.getElementById("input-name").value = "";
    }
}

let dataCache = [];
async function refreshCache() {
    const res = await fetch("/api/contacts");
    const data = await res.json();
    dataCache = data.contacts;
}

function addMethodRow(type, value) {
    const div = document.createElement("div");
    div.className = "method-row";
    div.innerHTML = `
        <select class="method-type">
            <option value="phone">电话</option>
            <option value="email">邮箱</option>
            <option value="social">社交账号</option>
            <option value="address">地址</option>
        </select>
        <input type="text" class="method-value" placeholder="输入联系方式">
        <button class="btn small remove-method" type="button">×</button>
    `;
    if (type) div.querySelector(".method-type").value = type;
    if (value) div.querySelector(".method-value").value = value;
    document.getElementById("methods-container").appendChild(div);
    div.querySelector(".remove-method").onclick = () => div.remove();
}

document.getElementById("add-btn").onclick = async () => {
    await refreshCache();
    openModal(null);
};
document.getElementById("add-method").onclick = () => addMethodRow();
document.getElementById("cancel-btn").onclick = () => {
    document.getElementById("modal").classList.add("hidden");
};

document.getElementById("save-btn").onclick = async () => {
    const name = document.getElementById("input-name").value.trim();
    if (!name) { alert("请输入姓名"); return; }
    const methods = [];
    document.querySelectorAll(".method-row").forEach(row => {
        const v = row.querySelector(".method-value").value.trim();
        if (v) methods.push({ type: row.querySelector(".method-type").value, value: v });
    });
    if (editingId) {
        await fetch(`/api/contacts/${editingId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, methods })
        });
    } else {
        await fetch("/api/contacts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, methods })
        });
    }
    document.getElementById("modal").classList.add("hidden");
    loadContacts();
};

document.getElementById("export-btn").onclick = () => {
    window.location.href = "/api/export";
};

document.getElementById("import-file").onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    const res = await fetch("/api/import", { method: "POST", body: form });
    const data = await res.json();
    if (data.success) {
        alert(`成功导入 ${data.imported} 条联系人`);
        loadContacts();
    } else {
        alert(data.message);
    }
};

loadContacts();
