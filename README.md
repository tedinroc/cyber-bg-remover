# Cyber BG Remover

一個具有賽博龐克風格的圖片背景移除網站。

## 功能特點

- 快速移除圖片背景
- 現代化賽博龐克UI設計
- 即時預覽
- 支援PNG格式下載

## 安裝說明

1. 安裝必要的套件：
```bash
pip install -r requirements.txt
```

2. 執行應用程式：
```bash
python app.py
```

3. 開啟瀏覽器訪問：
```
http://localhost:5000
```

## 使用方法

1. 點擊"選擇圖片"按鈕上傳圖片
2. 點擊"移除背景"按鈕處理圖片
3. 等待處理完成後，可以預覽結果
4. 點擊"下載圖片"保存處理後的圖片

## 技術堆疊

- Flask (後端框架)
- rembg (圖片背景移除)
- Pillow (圖片處理)
- TailwindCSS (前端樣式)
