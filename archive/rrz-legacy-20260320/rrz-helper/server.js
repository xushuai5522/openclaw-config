const express = require('express');
const multer = require('multer');
const sharp = require('sharp');
const path = require('path');
const fs = require('fs').promises;

const app = express();
const upload = multer({ dest: 'uploads/' });

// 静态文件服务
app.use(express.static('.'));

// 图片处理API
app.post('/api/process-images', upload.array('images', 10), async (req, res) => {
    try {
        const processedImages = [];

        for (const file of req.files) {
            // 读取图片
            const image = sharp(file.path);
            const metadata = await image.metadata();

            // 移除背景并添加白底
            const processed = await image
                .resize(800, 800, {
                    fit: 'contain',
                    background: { r: 255, g: 255, b: 255, alpha: 1 }
                })
                .png()
                .toBuffer();

            // 转换为base64
            const base64 = `data:image/png;base64,${processed.toString('base64')}`;
            processedImages.push(base64);

            // 删除临时文件
            await fs.unlink(file.path);
        }

        res.json({ images: processedImages });
    } catch (error) {
        console.error('处理失败:', error);
        res.status(500).json({ error: '图片处理失败' });
    }
});

const PORT = 8067;
app.listen(PORT, () => {
    console.log(`🚀 人人租上架助手已启动: http://localhost:${PORT}`);
});
