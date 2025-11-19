# -Educational-Counselor-Assistant-
# 后端在云服务器安装指南
## 初始化
### GIT ssh配置
ssh-keygen -t ed25519 -C "laolei02@gmail.com", 然后一路回车即可
cd ~/.ssh/
cat id_ed25519.pub
到github中新增一个ssh key（https://github.com/settings/ssh/new）。把对应内容拷贝到里面即可


# 后台运行环境配置
1. python版本，推荐使用3.12
2. 新建目录/data/home, 然后执行sudo apt install python3.12-venv -y
3. 执行python3 -m venv venv
4. 执行source venv/bin/activate
5. 执行sudo apt-get update
6. 执行sudo apt-get install -y pkg-config python3-dev default-libmysqlclient-dev build-essential
7. cd /data/home/Educational-Counselor-Assistant/backend && python3 -m pip install -r requirements.txt

# 前端运行环境
cd /data/home/Educational-Counselor-Assistant/frontend
sudo apt install npm -y
npm install
npm run build
mkdir -p /app/dist
cp -r ./dist/* /app/dist/

# nginx配置
sudo apt install -y nginx
cp /data/home/Educational-Counselor-Assistant/nginx.conf /etc/nginx/conf.d/nginx.conf 
systemctl restart nginx