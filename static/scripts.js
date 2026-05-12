// static/script.js

// ========== تهيئة الصفحة ==========
document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
    updateTimers();
    initializeAnimations();
    initializeForms();
    initializeModalClose();
});

// ========== إدارة الأدمن ==========

// إظهار نافذة إضافة مستخدم
function showAddUserModal() {
    const modal = document.getElementById('addUserModal');
    if (modal) {
        modal.style.display = 'flex';
        // تنظيف الحقول
        document.getElementById('new_username').value = '';
        document.getElementById('new_password').value = '';
        document.getElementById('new_telegram').value = '';
        document.getElementById('new_days').value = '30';
        document.getElementById('new_max_bots').value = '5';
    }
}

// إظهار نافذة إضافة رابط
function showAddLinkModal() {
    const modal = document.getElementById('addLinkModal');
    if (modal) {
        modal.style.display = 'flex';
        // تنظيف الحقول
        document.getElementById('link_name').value = '';
        document.getElementById('link_url').value = '';
        document.getElementById('link_icon').value = 'fas fa-link';
    }
}

// إغلاق النافذة المنبثقة
function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'none';
    }
}

// تهيئة إغلاق النوافذ بالنقر خارجها
function initializeModalClose() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
            }
        });
    });
}

// إنشاء مستخدم جديد
function createUser() {
    const username = document.getElementById('new_username')?.value;
    const password = document.getElementById('new_password')?.value;
    const days = document.getElementById('new_days')?.value;
    const max_bots = document.getElementById('new_max_bots')?.value;
    const telegram = document.getElementById('new_telegram')?.value || '';
    
    if (!username || !password) {
        showNotification('الرجاء إدخال اسم المستخدم وكلمة المرور', 'error');
        return;
    }
    
    if (!days || parseInt(days) < 1) {
        showNotification('الرجاء إدخال مدة صحيحة', 'error');
        return;
    }
    
    if (!max_bots || parseInt(max_bots) < 1) {
        showNotification('الرجاء إدخال عدد بوتات صحيح', 'error');
        return;
    }
    
    const data = {
        username: username,
        password: password,
        telegram: telegram,
        days: parseInt(days),
        max_bots: parseInt(max_bots)
    };
    
    fetch('/create_user', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('✅ تم إنشاء المستخدم بنجاح', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('❌ ' + (data.error || 'حدث خطأ'), 'error');
        }
    })
    .catch(error => {
        showNotification('❌ خطأ في الاتصال', 'error');
        console.error('Error:', error);
    });
}

// إنشاء رابط جديد
function createLink() {
    const name = document.getElementById('link_name')?.value;
    const url = document.getElementById('link_url')?.value;
    let icon = document.getElementById('link_icon')?.value || 'fas fa-link';
    
    if (!name || !url) {
        showNotification('الرجاء إدخال اسم الرابط والرابط', 'error');
        return;
    }
    
    // التحقق من صحة الرابط
    try {
        new URL(url);
    } catch {
        showNotification('الرجاء إدخال رابط صحيح (يبدأ بـ http:// أو https://)', 'error');
        return;
    }
    
    // التأكد من الأيقونة
    if (!icon.startsWith('fa')) {
        icon = 'fas fa-link';
    }
    
    const data = {
        name: name,
        url: url,
        icon: icon
    };
    
    fetch('/add_link', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('✅ تم إضافة الرابط بنجاح', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('❌ ' + (data.error || 'حدث خطأ'), 'error');
        }
    })
    .catch(error => {
        showNotification('❌ خطأ في الاتصال', 'error');
        console.error('Error:', error);
    });
}

// حذف رابط
function deleteLink(id) {
    if (!id) return;
    
    if (confirm('هل أنت متأكد من حذف هذا الرابط؟')) {
        fetch('/delete_link/' + id, {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('✅ تم حذف الرابط بنجاح', 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                showNotification('❌ ' + (data.error || 'حدث خطأ'), 'error');
            }
        })
        .catch(error => {
            showNotification('❌ خطأ في الاتصال', 'error');
            console.error('Error:', error);
        });
    }
}

// عرض بوتات مستخدم
function viewUserBots(id) {
    if (id) {
        window.location.href = '/admin/user/' + id;
    }
}

// تعديل مستخدم
function editUser(id) {
    showNotification('قريباً - تعديل المستخدم', 'info');
}

// حذف مستخدم
function deleteUser(id) {
    if (!id) return;
    
    if (confirm('⚠️ هل أنت متأكد من حذف هذا المستخدم نهائياً؟\nسيتم حذف جميع بوتاته أيضاً!')) {
        fetch('/delete_user/' + id, {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('✅ تم حذف المستخدم بنجاح', 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                showNotification('❌ ' + (data.error || 'حدث خطأ'), 'error');
            }
        })
        .catch(error => {
            showNotification('❌ خطأ في الاتصال', 'error');
            console.error('Error:', error);
        });
    }
}

// ========== إدارة البوتات ==========

// التحكم في البوت (تشغيل/إيقاف/إعادة)
function controlBot(id, action) {
    if (!id || !action) return;
    
    const btn = event?.target;
    if (btn) {
        btn.disabled = true;
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري...';
    }
    
    fetch('/bot_action', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({bot_id: id, action: action})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`✅ تم ${action === 'start' ? 'تشغيل' : action === 'stop' ? 'إيقاف' : 'إعادة تشغيل'} البوت بنجاح`, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = originalText;
            }
            showNotification('❌ ' + (data.error || 'حدث خطأ'), 'error');
        }
    })
    .catch(error => {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
        showNotification('❌ خطأ في الاتصال', 'error');
        console.error('Error:', error);
    });
}

// حذف بوت
function deleteBot(id) {
    if (!id) return;
    
    if (confirm('⚠️ هل أنت متأكد من حذف هذا البوت نهائياً؟')) {
        fetch('/delete_bot/' + id, {method: 'POST'})
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('✅ تم حذف البوت بنجاح', 'success');
                setTimeout(() => {
                    if (window.location.pathname.includes('/bot/')) {
                        window.location.href = '/dashboard';
                    } else {
                        location.reload();
                    }
                }, 1000);
            } else {
                showNotification('❌ ' + (data.error || 'حدث خطأ'), 'error');
            }
        })
        .catch(error => {
            showNotification('❌ خطأ في الاتصال', 'error');
            console.error('Error:', error);
        });
    }
}

// تعديل حقل في البوت
let currentField = '';

function editField(field) {
    currentField = field;
    const modal = document.getElementById('editModal');
    const title = document.getElementById('modalTitle');
    
    if (!modal || !title) return;
    
    const titles = {
        'uid': 'تعديل الأيدي',
        'password': 'تعديل كلمة المرور',
        'bot_name': 'تعديل اسم البوت',
        'display_name': 'تعديل الاسم المعروض'
    };
    
    title.innerText = titles[field] || 'تعديل';
    modal.style.display = 'flex';
    document.getElementById('editValue').value = '';
}

function saveEdit() {
    const value = document.getElementById('editValue')?.value;
    if (!value) {
        showNotification('الرجاء إدخال القيمة الجديدة', 'error');
        return;
    }
    
    const botId = window.location.pathname.split('/').pop();
    const data = {};
    data[currentField] = value;
    
    fetch('/edit_bot/' + botId, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('✅ تم التعديل بنجاح', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('❌ ' + (data.error || 'حدث خطأ'), 'error');
        }
    })
    .catch(error => {
        showNotification('❌ خطأ في الاتصال', 'error');
        console.error('Error:', error);
    });
}

// إضافة لاعب
function addPlayer() {
    const uid = document.getElementById('player_uid')?.value;
    const duration = document.getElementById('duration')?.value;
    
    if (!uid || !duration) {
        showNotification('الرجاء إدخال أيدي اللاعب والمدة', 'error');
        return;
    }
    
    // التحقق من صيغة المدة
    if (!duration.match(/^\d+[dh]$/)) {
        showNotification('صيغة خاطئة - استخدم مثلاً: 30d أو 24h', 'error');
        return;
    }
    
    const botId = window.location.pathname.split('/').pop();
    
    fetch('/add_player', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            bot_id: parseInt(botId),
            player_uid: uid,
            duration: duration
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('✅ تم إضافة اللاعب بنجاح', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('❌ ' + (data.error || 'حدث خطأ'), 'error');
        }
    })
    .catch(error => {
        showNotification('❌ خطأ في الاتصال', 'error');
        console.error('Error:', error);
    });
}

// حذف لاعب
function removePlayer(id) {
    if (!id) return;
    
    if (confirm('هل أنت متأكد من حذف هذا اللاعب؟')) {
        fetch('/remove_player', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({player_id: id})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('✅ تم حذف اللاعب بنجاح', 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                showNotification('❌ ' + (data.error || 'حدث خطأ'), 'error');
            }
        })
        .catch(error => {
            showNotification('❌ خطأ في الاتصال', 'error');
            console.error('Error:', error);
        });
    }
}

// ========== دوال مساعدة ==========

// تسجيل الخروج
function logout() {
    if (confirm('تسجيل الخروج؟')) {
        window.location.href = '/logout';
    }
}

// تهيئة التلميحات
function initializeTooltips() {
    const tooltips = document.querySelectorAll('[title]');
    tooltips.forEach(el => {
        el.addEventListener('mouseenter', showTooltip);
        el.addEventListener('mouseleave', hideTooltip);
    });
}

// إظهار التلميح
function showTooltip(e) {
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = e.target.title;
    
    document.body.appendChild(tooltip);
    
    const rect = e.target.getBoundingClientRect();
    tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
    tooltip.style.left = rect.left + (rect.width - tooltip.offsetWidth) / 2 + 'px';
    
    e.target._tooltip = tooltip;
}

// إخفاء التلميح
function hideTooltip(e) {
    if (e.target._tooltip) {
        e.target._tooltip.remove();
        e.target._tooltip = null;
    }
}

// تحديث المؤقتات
function updateTimers() {
    const timers = document.querySelectorAll('.player-time');
    timers.forEach(timer => {
        const expiry = timer.dataset.expiry;
        if (expiry) {
            updateTimer(timer, expiry);
        }
    });
}

// تحديث مؤقت واحد
function updateTimer(element, expiryDate) {
    const expiry = new Date(expiryDate).getTime();
    const now = new Date().getTime();
    const distance = expiry - now;
    
    if (distance < 0) {
        element.innerHTML = '<span style="color: var(--danger);">انتهت المدة</span>';
        return;
    }
    
    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    
    const timeSpan = element.querySelector('span');
    if (timeSpan) {
        timeSpan.textContent = `${days}d ${hours}h ${minutes}m`;
    }
}

// تهيئة الأنيميشن
function initializeAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'slideIn 0.5s ease';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.bot-card, .stat-card, .link-card').forEach(el => {
        observer.observe(el);
    });
}

// تهيئة النماذج
function initializeForms() {
    const createBotForm = document.getElementById('createBotForm');
    if (createBotForm) {
        createBotForm.addEventListener('submit', handleCreateBot);
    }
}

// معالجة إنشاء بوت
function handleCreateBot(e) {
    e.preventDefault();
    
    const btn = document.getElementById('submitBtn');
    const msg = document.getElementById('message');
    
    if (!btn || !msg) return;
    
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري الإنشاء...';
    
    fetch('/create_bot', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            uid: document.getElementById('uid').value,
            password: document.getElementById('password').value,
            bot_name: document.getElementById('bot_name').value,
            display_name: document.getElementById('display_name').value
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            msg.style.display = 'block';
            msg.className = 'success-message';
            msg.innerHTML = '<i class="fas fa-check-circle"></i> تم إنشاء البوت بنجاح!';
            showNotification('✅ تم إنشاء البوت بنجاح', 'success');
            setTimeout(() => window.location.href = '/dashboard', 2000);
        } else {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-plus"></i> إنشاء البوت';
            msg.style.display = 'block';
            msg.className = 'error-message';
            msg.innerHTML = '<i class="fas fa-exclamation-circle"></i> ' + (data.error || 'حدث خطأ');
            showNotification('❌ ' + (data.error || 'حدث خطأ'), 'error');
        }
    })
    .catch(error => {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-plus"></i> إنشاء البوت';
        msg.style.display = 'block';
        msg.className = 'error-message';
        msg.innerHTML = '<i class="fas fa-exclamation-circle"></i> خطأ في الاتصال';
        showNotification('❌ خطأ في الاتصال', 'error');
        console.error('Error:', error);
    });
}

// إظهار إشعار
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// نسخ النص
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('تم النسخ!', 'success');
    }).catch(() => {
        showNotification('فشل النسخ', 'error');
    });
}

// ========== إضافة أنماط CSS ديناميكية ==========
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-30px);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    .custom-tooltip {
        position: fixed;
        background: var(--card);
        color: var(--primary);
        padding: 8px 15px;
        border-radius: 8px;
        font-size: 13px;
        border: 1px solid var(--border);
        z-index: 9999;
        pointer-events: none;
        animation: slideIn 0.2s ease;
        box-shadow: 0 5px 20px rgba(0,0,0,0.3);
    }
    
    .notification {
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: var(--card);
        padding: 15px 30px;
        border-radius: 50px;
        border: 1px solid var(--border);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: slideIn 0.3s ease;
    }
    
    .notification-success {
        color: var(--success);
        border-right: 4px solid var(--success);
    }
    
    .notification-error {
        color: var(--danger);
        border-right: 4px solid var(--danger);
    }
    
    .notification-info {
        color: var(--primary);
        border-right: 4px solid var(--primary);
    }
    
    .notification i {
        font-size: 20px;
    }
    
    .status.running {
        animation: pulse 2s infinite;
    }
    
    .fa-spinner {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
    
    .modal {
        animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
`;

document.head.appendChild(style);