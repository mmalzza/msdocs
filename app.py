from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from pdf_filler import fill_pdf
import json

app = Flask(__name__)
CORS(app)

# PDF 파일 경로
INPUT_PDF = "외국인등록신청서.pdf"
OUTPUT_PDF = "외국인등록신청서_작성완료.pdf"

# 현재 상태를 저장할 변수
current_data = {}

@app.route('/api/update', methods=['POST'])
def update_pdf():
    try:
        data = request.json
        field = data.get('field')
        value = data.get('value')
        
        # 데이터 업데이트
        current_data[field] = value
        
        # PDF 생성
        if os.path.exists(INPUT_PDF):
            fill_pdf(INPUT_PDF, OUTPUT_PDF, current_data)
            return jsonify({
                'success': True,
                'message': 'PDF가 업데이트되었습니다.',
                'pdf_url': f'/api/pdf?t={os.path.getmtime(OUTPUT_PDF)}'
            })
        else:
            return jsonify({
                'success': False,
                'message': '입력 PDF 파일을 찾을 수 없습니다.'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/pdf')
def get_pdf():
    try:
        return send_file(OUTPUT_PDF, mimetype='application/pdf')
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_data():
    global current_data
    current_data = {}
    return jsonify({
        'success': True,
        'message': '데이터가 초기화되었습니다.'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
