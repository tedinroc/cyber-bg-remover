from flask import Flask, request, render_template, send_file, jsonify
from rembg import remove, new_session
from PIL import Image
import io
import os
import gc
import numpy as np
import logging

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/uploads' if os.environ.get('VERCEL_ENV') else 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 rembg session
try:
    session = new_session(model_name="u2net")
except Exception as e:
    logger.error(f"Error initializing model: {e}")
    session = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/remove-bg', methods=['POST'])
def remove_background():
    if session is None:
        return jsonify({'error': 'Model not initialized'}), 500

    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # 讀取圖片
        input_image = Image.open(file.stream)
        logger.info(f"Processing image: {file.filename}, size: {input_image.size}")
        
        # 轉換為 RGB 模式
        if input_image.mode != 'RGB':
            input_image = input_image.convert('RGB')
        
        # 限制圖片大小
        max_size = 2000
        if input_image.size[0] > max_size or input_image.size[1] > max_size:
            ratio = max_size / max(input_image.size)
            new_size = tuple(int(dim * ratio) for dim in input_image.size)
            input_image = input_image.resize(new_size, Image.Resampling.LANCZOS)
            logger.info(f"Resized to: {new_size}")
        
        # 強制進行垃圾回收
        gc.collect()
        
        # 移除背景
        output_image = remove(
            input_image,
            session=session,
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=10
        )
        
        # 釋放原始圖片內存
        input_image.close()
        del input_image
        gc.collect()
        
        # 將輸出圖片轉換為 bytes
        img_byte_arr = io.BytesIO()
        output_image.save(
            img_byte_arr,
            format='PNG',
            optimize=True,
            quality=95
        )
        img_byte_arr.seek(0)
        
        # 釋放處理後圖片的內存
        output_image.close()
        del output_image
        gc.collect()
        
        return send_file(
            img_byte_arr,
            mimetype='image/png',
            as_attachment=True,
            download_name='removed_bg.png'
        )
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        gc.collect()
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
