#!/bin/bash

# 更新系統
sudo apt-get update
sudo apt-get upgrade -y

# 安裝必要的包
sudo apt-get install -y python3-pip python3-venv nginx

# 創建專案目錄
sudo mkdir -p /var/www/cyber-bg-remover
sudo chown -R $USER:$USER /var/www/cyber-bg-remover

# 創建並激活虛擬環境
python3 -m venv /var/www/cyber-bg-remover/venv
source /var/www/cyber-bg-remover/venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
pip install gunicorn

# 複製專案文件
cp -r * /var/www/cyber-bg-remover/
cp cyber-bg-remover.service /etc/systemd/system/

# 創建上傳目錄並設置權限
mkdir -p /var/www/cyber-bg-remover/uploads
sudo chown -R www-data:www-data /var/www/cyber-bg-remover/uploads

# 配置 Nginx
sudo tee /etc/nginx/sites-available/cyber-bg-remover << EOF
server {
    listen 80;
    server_name \$server_name;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 上傳文件大小限制
        client_max_body_size 10M;
    }
}
EOF

# 啟用網站配置
sudo ln -sf /etc/nginx/sites-available/cyber-bg-remover /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 重啟 Nginx
sudo systemctl restart nginx

# 啟動服務
sudo systemctl daemon-reload
sudo systemctl enable cyber-bg-remover
sudo systemctl start cyber-bg-remover

# 檢查服務狀態
sudo systemctl status cyber-bg-remover
