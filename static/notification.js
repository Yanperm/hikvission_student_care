// Toast & Modal Notification System
// © 2025 SOFTUBON CO.,LTD.

// Toast Notification
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
        <span class="toast-close" onclick="this.parentElement.remove()">×</span>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// Modal Dialog
function showModal(title, message, options = {}) {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        
        const buttons = options.buttons || [
            { text: 'ตกลง', type: 'primary', value: true }
        ];
        
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <span class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</span>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    ${buttons.map((btn, i) => `
                        <button class="btn btn-${btn.type}" data-value="${btn.value}" data-index="${i}">
                            ${btn.text}
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        setTimeout(() => modal.classList.add('show'), 10);
        
        modal.querySelectorAll('button').forEach(btn => {
            btn.onclick = () => {
                const value = btn.dataset.value === 'true' ? true : btn.dataset.value === 'false' ? false : btn.dataset.value;
                modal.classList.remove('show');
                setTimeout(() => modal.remove(), 300);
                resolve(value);
            };
        });
    });
}

// Confirm Dialog
function showConfirm(title, message) {
    return showModal(title, message, {
        buttons: [
            { text: 'ยกเลิก', type: 'secondary', value: false },
            { text: 'ยืนยัน', type: 'primary', value: true }
        ]
    });
}

// Alert Dialog
function showAlert(title, message, type = 'info') {
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    return showModal(
        `${icons[type]} ${title}`,
        message,
        { buttons: [{ text: 'ตกลง', type: 'primary', value: true }] }
    );
}

// Replace native alert
window.alert = function(message) {
    showToast(message, 'info');
};

// Replace native confirm
window.confirm = function(message) {
    return showConfirm('ยืนยันการทำงาน', message);
};
