from flask import Flask, request, render_template, send_file
from rembg import remove, new_session
from PIL import Image
import io
import os
import gc
import numpy as np

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 初始化 rembg session，使用較小的模型
session = new_session(model_name="u2net_human_seg")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/remove-bg', methods=['POST'])
def remove_background():
    if 'image' not in request.files:
        return 'No image uploaded', 400
    
    file = request.files['image']
    if file.filename == '':
        return 'No selected file', 400

    try:
        # 讀取並調整圖片大小
        input_image = Image.open(file.stream)
        
        # 轉換為 RGB 模式
        if input_image.mode != 'RGB':
            input_image = input_image.convert('RGB')
        
        # 限制圖片大小
        max_size = 800
        if input_image.size[0] > max_size or input_image.size[1] > max_size:
            ratio = max_size / max(input_image.size)
            new_size = tuple(int(dim * ratio) for dim in input_image.size)
            input_image = input_image.resize(new_size, Image.Resampling.LANCZOS)
        
        # 強制進行垃圾回收
        gc.collect()
        
        # 移除背景
        output_image = remove(input_image, session=session, alpha_matting=False, alpha_matting_foreground_threshold=0, alpha_matting_background_threshold=0)
        
        # 釋放原始圖片內存
        input_image.close()
        del input_image
        gc.collect()
        
        # 將處理後的圖片轉換為bytes，使用最大壓縮
        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format='PNG', optimize=True, quality=95)
        img_byte_arr.seek(0)
        
        # 釋放處理後圖片的內存
        output_image.close()
        del output_image
        gc.collect()
        
        return send_file(img_byte_arr, mimetype='image/png')
        
    except Exception as e:
        return str(e), 500
    finally:
        gc.collect()
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
