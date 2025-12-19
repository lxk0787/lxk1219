# 项目部署指南

## 1. 本地运行

### 环境要求
- Python 3.7+ 
- Flask 3.0+ 
- requests库

### 安装依赖
```bash
pip install flask requests
```

### 启动应用
```bash
python app.py
```

### 访问应用
打开浏览器访问：http://127.0.0.1:5000

## 2. 临时公网访问（推荐）

使用ngrok工具可以将本地应用临时发布到公网，方便他人访问。

### 步骤1：下载ngrok
- 访问 https://ngrok.com/download
- 下载适合您操作系统的版本
- 解压到本地目录

### 步骤2：启动ngrok
```bash
# 替换为您的ngrok路径
./ngrok http 5000
```

### 步骤3：获取公网URL
启动后，ngrok会显示类似如下信息：
```
Forwarding https://xxxx-xx-xx-xx-xx.ngrok-free.app -> http://localhost:5000
```

将 `https://xxxx-xx-xx-xx-xx.ngrok-free.app` 分享给他人即可访问。

## 3. GitHub Pages部署

### 步骤1：创建GitHub仓库
1. 登录GitHub，创建一个新仓库
2. 仓库名称建议：`luojia-explorer`
3. 选择"Public"（公开）

### 步骤2：安装依赖
```bash
pip install flask requests gunicorn
```

### 步骤3：创建Procfile
在项目根目录创建 `Procfile` 文件：
```
web: gunicorn app:app
```

### 步骤4：创建requirements.txt
```bash
pip freeze > requirements.txt
```

### 步骤5：部署到Vercel或Render

#### 选项A：Vercel部署
1. 访问 https://vercel.com
2. 登录并点击"New Project"
3. 选择"Import from Git"
4. 连接GitHub并选择您的仓库
5. 配置部署设置：
   - Framework Preset: `Flask`
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: 留空
6. 点击"Deploy"
7. 等待部署完成，获取公网URL

#### 选项B：Render部署
1. 访问 https://render.com
2. 登录并点击"New Web Service"
3. 选择"GitHub"
4. 连接GitHub并选择您的仓库
5. 配置部署设置：
   - Runtime: `Python 3.7`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
6. 点击"Create Web Service"
7. 等待部署完成，获取公网URL

## 4. 云服务器部署

### 步骤1：购买云服务器
推荐使用：
- 阿里云ECS
- 腾讯云CVM
- 华为云ECS

### 步骤2：安装环境
```bash
# 更新系统
apt update && apt upgrade -y

# 安装Python
apt install python3 python3-pip python3-venv -y

# 创建虚拟环境
mkdir -p /opt/luojia-explorer
cd /opt/luojia-explorer
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install flask requests gunicorn
```

### 步骤3：上传代码
使用scp或git clone上传代码到服务器。

### 步骤4：启动服务
```bash
# 激活虚拟环境
source venv/bin/activate

# 使用gunicorn启动
cd /opt/luojia-explorer
gunicorn -w 4 -b 0.0.0.0:80 app:app
```

### 步骤5：配置域名（可选）
1. 在域名服务商处添加A记录，指向服务器IP
2. 安装Nginx并配置反向代理

## 5. 访问地址示例

- 本地访问：http://127.0.0.1:5000
- ngrok临时访问：https://xxxx-xx-xx-xx-xx.ngrok-free.app
- Vercel部署：https://luojia-explorer.vercel.app
- Render部署：https://luojia-explorer.onrender.com
- 云服务器：http://your-server-ip

## 6. 安全建议

- 生产环境建议使用HTTPS
- 配置防火墙，只开放必要端口
- 定期更新依赖包
- 使用环境变量管理敏感信息
- 配置日志记录

## 7. 故障排查

### 常见问题
- **端口被占用**：使用 `lsof -i :5000` 查看占用进程，使用 `kill -9 <PID>` 终止
- **依赖错误**：确保已激活虚拟环境，重新安装依赖
- **权限问题**：确保应用目录有正确的读写权限
- **防火墙问题**：检查云服务器安全组配置，确保端口已开放

### 查看日志
```bash
# gunicorn日志
gunicorn -w 4 -b 0.0.0.0:80 app:app --access-logfile - --error-logfile - 

# 或查看Flask日志
python app.py
```

## 8. 联系方式

如有部署问题，请联系：
- Email: example@whu.edu.cn
- GitHub Issues: https://github.com/yourusername/luojia-explorer/issues
