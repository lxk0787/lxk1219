from flask import Flask, render_template, request, jsonify
from campus_orientation import LuojiaExplorer

app = Flask(__name__)

# 初始化珞珈探秘助手
assistant = LuojiaExplorer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_request', methods=['POST'])
def process_request():
    user_input = request.form['user_input']
    response = assistant.process_request(user_input)
    return jsonify({'response': response})

if __name__ == '__main__':
    print(f"\n🚀 珞珈探秘·校园团建定向助手")
    print(f"🌐 本地访问地址: http://localhost:5000")
    print(f"� 详细部署指南: DEPLOYMENT.md")
    print(f"\n请参考DEPLOYMENT.md文件进行公网部署！\n")
    
    # 启动Flask应用
    app.run(debug=True, host='0.0.0.0', port=5000)
