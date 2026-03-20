// 定价规则
const PRICING_RULES = {
    // 租金 = 闲鱼价 × 系数
    rent_ratio: {
        '1月': 0.12,
        '3月': 0.10,
        '6月': 0.08,
        '12月': 0.06
    },
    // 押金 = 闲鱼价 × 0.3
    deposit_ratio: 0.3,
    // 买断价 = 闲鱼价 × 0.95
    buyout_ratio: 0.95
};

// 生成内容
function generateContent() {
    const brand = document.getElementById('brand').value.trim();
    const model = document.getElementById('model').value.trim();
    const condition = document.getElementById('condition').value;
    const xianyuPrice = parseFloat(document.getElementById('xianyu_price').value);
    const features = document.getElementById('features').value.trim();

    if (!brand || !model || !xianyuPrice) {
        alert('请填写品牌、型号和闲鱼参考价');
        return;
    }

    // 生成标题
    const title = `${brand} ${model} ${condition} 租赁`;
    
    // 生成描述
    let description = `【品牌型号】${brand} ${model}\n`;
    description += `【成色】${condition}\n`;
    if (features) {
        description += `【商品特点】${features}\n`;
    }
    description += `\n【租赁说明】\n`;
    description += `✓ 正品保障，支持验机\n`;
    description += `✓ 顺丰包邮，安全送达\n`;
    description += `✓ 7天无理由退换\n`;
    description += `✓ 到期可续租、买断或退还\n`;

    // 计算定价
    const deposit = Math.round(xianyuPrice * PRICING_RULES.deposit_ratio);
    const buyout = Math.round(xianyuPrice * PRICING_RULES.buyout_ratio);
    const rent1m = Math.round(xianyuPrice * PRICING_RULES.rent_ratio['1月']);
    const rent3m = Math.round(xianyuPrice * PRICING_RULES.rent_ratio['3月']);
    const rent6m = Math.round(xianyuPrice * PRICING_RULES.rent_ratio['6月']);
    const rent12m = Math.round(xianyuPrice * PRICING_RULES.rent_ratio['12月']);

    // 生成套餐
    let packages = `【租赁套餐】\n\n`;
    packages += `📦 1个月租：${rent1m}元/月\n`;
    packages += `📦 3个月租：${rent3m}元/月（总计${rent3m * 3}元）\n`;
    packages += `📦 6个月租：${rent6m}元/月（总计${rent6m * 6}元）\n`;
    packages += `📦 12个月租：${rent12m}元/月（总计${rent12m * 12}元）\n\n`;
    packages += `💰 押金：${deposit}元（到期退还）\n`;
    packages += `💰 买断价：${buyout}元\n`;

    // 定价信息
    let pricing = `闲鱼参考价：${xianyuPrice}元\n\n`;
    pricing += `押金：${deposit}元（${PRICING_RULES.deposit_ratio * 100}%）\n`;
    pricing += `买断价：${buyout}元（${PRICING_RULES.buyout_ratio * 100}%）\n\n`;
    pricing += `月租金：\n`;
    pricing += `  1月：${rent1m}元（${PRICING_RULES.rent_ratio['1月'] * 100}%）\n`;
    pricing += `  3月：${rent3m}元（${PRICING_RULES.rent_ratio['3月'] * 100}%）\n`;
    pricing += `  6月：${rent6m}元（${PRICING_RULES.rent_ratio['6月'] * 100}%）\n`;
    pricing += `  12月：${rent12m}元（${PRICING_RULES.rent_ratio['12月'] * 100}%）\n`;

    // 显示结果
    document.getElementById('title').textContent = title;
    document.getElementById('description').textContent = description;
    document.getElementById('packages').textContent = packages;
    document.getElementById('pricing').textContent = pricing;
    document.getElementById('resultSection').style.display = 'block';

    // 滚动到结果
    document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// 复制文本
function copyText(elementId) {
    const text = document.getElementById(elementId).textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✓ 已复制';
        btn.classList.add('copied');
        setTimeout(() => {
            btn.textContent = originalText;
            btn.classList.remove('copied');
        }, 2000);
    }).catch(err => {
        alert('复制失败，请手动复制');
    });
}

// 图片上传处理
let uploadedImages = [];

const uploadArea = document.getElementById('uploadArea');
const imageInput = document.getElementById('imageInput');
const imagePreview = document.getElementById('imagePreview');
const processBtn = document.getElementById('processBtn');

// 点击上传区域
uploadArea.addEventListener('click', () => {
    imageInput.click();
});

// 文件选择
imageInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

// 拖拽上传
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
});

// 处理文件
function handleFiles(files) {
    for (let file of files) {
        if (file.type.startsWith('image/')) {
            uploadedImages.push(file);
            displayImage(file);
        }
    }
    if (uploadedImages.length > 0) {
        processBtn.style.display = 'block';
    }
}

// 显示图片预览
function displayImage(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const div = document.createElement('div');
        div.className = 'preview-item';
        div.innerHTML = `
            <img src="${e.target.result}" alt="预览">
            <button class="remove-btn" onclick="removeImage(${uploadedImages.length - 1})">×</button>
        `;
        imagePreview.appendChild(div);
    };
    reader.readAsDataURL(file);
}

// 移除图片
function removeImage(index) {
    uploadedImages.splice(index, 1);
    imagePreview.children[index].remove();
    if (uploadedImages.length === 0) {
        processBtn.style.display = 'none';
    }
}

// 处理图片（白底化）
async function processImages() {
    if (uploadedImages.length === 0) {
        alert('请先上传图片');
        return;
    }

    processBtn.textContent = '⏳ 处理中...';
    processBtn.disabled = true;

    try {
        // 调用图片处理API
        const formData = new FormData();
        uploadedImages.forEach((file, index) => {
            formData.append('images', file);
        });

        const response = await fetch('http://localhost:8067/api/process-images', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('图片处理失败');
        }

        const result = await response.json();
        
        // 下载处理后的图片
        result.images.forEach((imageData, index) => {
            const link = document.createElement('a');
            link.href = imageData;
            link.download = `processed_${index + 1}.png`;
            link.click();
        });

        alert(`✓ 成功处理 ${result.images.length} 张图片`);
        
    } catch (error) {
        console.error('处理失败:', error);
        alert('图片处理失败，请检查服务是否启动\n\n提示：需要运行本地图片处理服务');
    } finally {
        processBtn.textContent = '🎨 处理图片';
        processBtn.disabled = false;
    }
}
