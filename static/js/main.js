/**
 * 主JavaScript文件
 */

// CSRF Token处理
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// 配置AJAX请求
fetch = (originalFetch => {
    return function(url, options = {}) {
        if (!options.headers) {
            options.headers = {};
        }
        if (options.method && options.method.toUpperCase() !== 'GET') {
            options.headers['X-CSRFToken'] = csrftoken;
        }
        return originalFetch(url, options);
    };
})(fetch);

// 显示加载提示
function showLoading(message = '加载中...') {
    const modal = document.createElement('div');
    modal.id = 'global-loading';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    modal.innerHTML = `
        <div style="background: white; padding: 40px; border-radius: 10px; text-align: center;">
            <div style="font-size: 48px; margin-bottom: 20px;">⏳</div>
            <div style="font-size: 18px; color: #333;">${message}</div>
        </div>
    `;
    document.body.appendChild(modal);
}

// 隐藏加载提示
function hideLoading() {
    const modal = document.getElementById('global-loading');
    if (modal) {
        modal.remove();
    }
}

// 显示提示消息
function showMessage(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 10000; min-width: 300px;';
    alertDiv.textContent = message;

    document.body.appendChild(alertDiv);

    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

// 确认对话框
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// 文件大小格式化
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
}

// 文件上传拖放功能
function initFileDragDrop(elementId, callback) {
    const element = document.getElementById(elementId);
    if (!element) return;

    element.addEventListener('dragover', (e) => {
        e.preventDefault();
        element.classList.add('dragging');
    });

    element.addEventListener('dragleave', (e) => {
        e.preventDefault();
        element.classList.remove('dragging');
    });

    element.addEventListener('drop', (e) => {
        e.preventDefault();
        element.classList.remove('dragging');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            callback(files);
        }
    });
}

// 表格搜索功能
function initTableSearch(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);

    if (!input || !table) return;

    input.addEventListener('keyup', function() {
        const filter = this.value.toLowerCase();
        const rows = table.getElementsByTagName('tr');

        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            const text = row.textContent.toLowerCase();

            if (text.includes(filter)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
}

// 自动保存功能
function initAutoSave(formId, saveUrl, interval = 30000) {
    const form = document.getElementById(formId);
    if (!form) return;

    setInterval(() => {
        const formData = new FormData(form);

        fetch(saveUrl, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('自动保存成功', data);
        })
        .catch(error => {
            console.error('自动保存失败', error);
        });
    }, interval);
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 自动关闭提示消息
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 3000);
    });

    // 为所有确认操作添加提示
    const confirmBtns = document.querySelectorAll('[data-confirm]');
    confirmBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // 表单验证增强
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.style.borderColor = 'red';
                    isValid = false;
                } else {
                    field.style.borderColor = '';
                }
            });

            if (!isValid) {
                e.preventDefault();
                showMessage('请填写所有必填字段', 'error');
            }
        });
    });
});

