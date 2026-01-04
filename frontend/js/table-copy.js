// 表格完整复制功能
// 在"提取表格"时添加复制按钮，保留Word和Excel复制功能

// 为所有表格添加复制按钮
function addCopyButtonsToTables() {
    const resultSection = document.getElementById('resultContent');
    if (!resultSection) return;

    const tables = resultSection.querySelectorAll('table');
    tables.forEach((table, index) => {
        // 避免重复添加
        if (table.dataset.copyButtonAdded) return;
        table.dataset.copyButtonAdded = 'true';

        // 创建按钮容器
        const buttonContainer = document.createElement('div');
        buttonContainer.style.cssText = `
            margin-bottom: 10px;
            display: flex;
            gap: 10px;
        `;

        // 创建复制表格按钮（Word格式）
        const copyTableBtn = document.createElement('button');
        copyTableBtn.innerHTML = '📋 复制表格(含格式)';
        copyTableBtn.style.cssText = `
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
            transition: all 0.3s;
        `;
        copyTableBtn.onmouseover = () => {
            copyTableBtn.style.transform = 'translateY(-2px)';
            copyTableBtn.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
        };
        copyTableBtn.onmouseout = () => {
            copyTableBtn.style.transform = 'translateY(0)';
            copyTableBtn.style.boxShadow = '0 2px 8px rgba(102, 126, 234, 0.3)';
        };
        copyTableBtn.onclick = () => copyTableWithFormat(table);

        // 创建复制为Excel按钮
        const copyExcelBtn = document.createElement('button');
        copyExcelBtn.innerHTML = '📊 复制为Excel';
        copyExcelBtn.style.cssText = `
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            box-shadow: 0 2px 8px rgba(17, 153, 142, 0.3);
            transition: all 0.3s;
        `;
        copyExcelBtn.onmouseover = () => {
            copyExcelBtn.style.transform = 'translateY(-2px)';
            copyExcelBtn.style.boxShadow = '0 4px 12px rgba(17, 153, 142, 0.4)';
        };
        copyExcelBtn.onmouseout = () => {
            copyExcelBtn.style.transform = 'translateY(0)';
            copyExcelBtn.style.boxShadow = '0 2px 8px rgba(17, 153, 142, 0.3)';
        };
        copyExcelBtn.onclick = () => copyTableForExcel(table);

        buttonContainer.appendChild(copyTableBtn);
        buttonContainer.appendChild(copyExcelBtn);

        // 在表格前插入按钮
        table.parentNode.insertBefore(buttonContainer, table);
    });
}

// 复制表格（HTML格式，适合粘贴到Word）
function copyTableWithFormat(table) {
    try {
        const container = document.createElement('div');
        const clonedTable = table.cloneNode(true);

        clonedTable.style.borderCollapse = 'collapse';
        clonedTable.style.width = '100%';
        clonedTable.style.border = '1px solid #000';

        const cells = clonedTable.querySelectorAll('td, th');
        cells.forEach(cell => {
            cell.style.border = '1px solid #000';
            cell.style.padding = '8px';
            cell.style.backgroundColor = cell.tagName === 'TH' ? '#4a5568' : '#fff';
            cell.style.color = cell.tagName === 'TH' ? '#fff' : '#000';
        });

        container.appendChild(clonedTable);

        const blob = new Blob([container.innerHTML], { type: 'text/html' });
        const data = [new ClipboardItem({ 'text/html': blob })];

        navigator.clipboard.write(data).then(() => {
            alert('✅ 表格已复制！\n可以粘贴到Word、Excel等应用中，格式会保留。');
        }).catch(() => {
            fallbackCopyTable(table);
        });
    } catch (error) {
        fallbackCopyTable(table);
    }
}

// 复制表格为Excel格式（制表符分隔）
function copyTableForExcel(table) {
    const rows = table.querySelectorAll('tr');
    let textContent = '';

    rows.forEach(row => {
        const cells = row.querySelectorAll('td, th');
        const rowData = Array.from(cells).map(cell => {
            return cell.textContent.trim().replace(/\s+/g, ' ');
        });
        textContent += rowData.join('\t') + '\n';
    });

    navigator.clipboard.writeText(textContent).then(() => {
        alert('✅ 表格已复制为Excel格式！\n' +
            '1. 打开Excel\n' +
            '2. 粘贴(Ctrl+V)\n' +
            '3. 表格会自动分列');
    }).catch(() => {
        alert('❌ 复制失败，请手动选择表格复制');
    });
}

// 降级方案
function fallbackCopyTable(table) {
    const range = document.createRange();
    range.selectNode(table);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);

    try {
        document.execCommand('copy');
        alert('✅ 表格已复制！');
    } catch (err) {
        alert('❌ 复制失败，请手动选择表格后按Ctrl+C复制');
    }

    window.getSelection().removeAllRanges();
}

// 监听结果区域的变化，自动为表格添加复制按钮
const resultObserver = new MutationObserver(() => {
    addCopyButtonsToTables();
});

document.addEventListener('DOMContentLoaded', () => {
    const resultSection = document.getElementById('resultContent');
    if (resultSection) {
        resultObserver.observe(resultSection, {
            childList: true,
            subtree: true
        });
        addCopyButtonsToTables();
    }
});

window.addTableCopyButtons = addCopyButtonsToTables;

console.log('✅ 表格复制功能已加载（Word和Excel按钮保留）');
