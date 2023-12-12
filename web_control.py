
# —*-coding:utf-8 一*一
"""
作者:LegendLeo
日期:2023年12月10日
"""
from flask import Flask, jsonify, request, make_response
import os
from flask_cors import CORS

app = Flask(__name__, static_url_path="")
CORS(app, resources={r"/position/*": {"origins": "*"}})

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route('/position',methods=['POST'])
def send_button_position():  # put application's code here
    args = request.json
    try:
        print(f'angle = {args["angle"]}')
        return jsonify({"passed": True, "message": "成功发送位置", "data": f'angle={args["angle"]}'})
    except:
        return jsonify({"passed": False, "message": "错误", "data": None})

if __name__ == '__main__':
    # app.run()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))