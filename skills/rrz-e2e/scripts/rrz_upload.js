/**
 * rrz_upload.js — 人人租图片上传工具函数
 * 
 * 在 iframe[name=rrzuji] 内执行。
 * 依赖页面已加载的 createUploader SDK。
 * 
 * 用法（浏览器 evaluate）：
 *   1. 注入此脚本
 *   2. 调用 window.rrzUpload(base64Array, fileType) 
 *      返回 {done, urls: string[]}
 */

(function() {
  /**
   * 上传图片到人人租 OSS
   * @param {string[]} base64Images - base64 编码的图片数组（不含 data: 前缀）
   * @param {string} fileType - 'image' (默认)
   * @param {string} suffix - 文件后缀，默认 'jpg'
   * @returns {Promise<{done: boolean, urls: string[], paths: string[]}>}
   */
  window.rrzUpload = async function(base64Images, fileType = 'image', suffix = 'jpg') {
    if (!window.createUploader) {
      throw new Error('createUploader SDK 未加载');
    }

    const goToken = document.cookie.match(/Go-Token=([^;]+)/)?.[1] || '';
    if (!goToken) {
      throw new Error('Go-Token 未找到，请先登录');
    }

    const uploader = window.createUploader({
      project: () => 'shop-admin',
      getGoToken: () => goToken,
      goMicroBaseURL: 'https://go-micro.rrzu.com'
    });

    // base64 转 File 对象
    const files = base64Images.map((b64, i) => {
      const binary = atob(b64);
      const bytes = new Uint8Array(binary.length);
      for (let j = 0; j < binary.length; j++) bytes[j] = binary.charCodeAt(j);
      const mimeType = suffix === 'png' ? 'image/png' : 'image/jpeg';
      return new File([bytes], `upload_${i}.${suffix}`, { type: mimeType });
    });

    const result = await uploader.uploadToOss({
      files,
      file_type: fileType,
      upload_path: ''
    });

    return {
      done: result.done,
      urls: result.pathWithOssServer || [],
      paths: result.path || []
    };
  };

  /**
   * 上传单张图片（便捷方法）
   * @param {string} base64 - base64 编码
   * @param {string} suffix - 'jpg' | 'png'
   * @returns {Promise<{done: boolean, url: string, path: string}>}
   */
  window.rrzUploadOne = async function(base64, suffix = 'jpg') {
    const result = await window.rrzUpload([base64], 'image', suffix);
    return {
      done: result.done,
      url: result.urls[0] || '',
      path: result.paths[0] || ''
    };
  };

  console.log('✅ rrzUpload / rrzUploadOne 已注入');
})();
