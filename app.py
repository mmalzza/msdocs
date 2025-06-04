from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from pdf_filler import fill_pdf
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# PDF 파일 경로
INPUT_PDF = "외국인등록신청서.pdf"
OUTPUT_PDF = "외국인등록신청서_작성완료.pdf"
UPLOAD_FOLDER = "./uploads"

OUTPUT_PDF_NAME = "외국인등록신청서_작성완료.pdf"
OUTPUT_PDF_PATH = os.path.join(UPLOAD_FOLDER, OUTPUT_PDF_NAME)

ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 현재 상태를 저장할 변수
current_data = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# PDF 업데이트
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
            fill_pdf(INPUT_PDF, OUTPUT_PDF_PATH, current_data)

            return jsonify({
                'success': True,
                'message': f'PDF 파일이 성공적으로 생성되었습니다: {OUTPUT_PDF_NAME}',
                'pdf_url': f'/uploads/{OUTPUT_PDF_NAME}?t={os.path.getmtime(OUTPUT_PDF_PATH)}'
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

# @app.route('/api/pdf')
# def get_pdf():
#     try:
#         return send_file(OUTPUT_PDF, mimetype='application/pdf')
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': str(e)
#         }), 500

@app.route('/api/reset', methods=['POST'])
def reset_data():
    global current_data
    current_data = {}
    return jsonify({
        'success': True,
        'message': '데이터가 초기화되었습니다.'
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '파일이 없습니다.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '파일 이름이 없습니다.'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        file_url = request.host_url + 'uploads/' + filename  # 앱에서 이 URL로 열기
        return jsonify({'success': True, 'file_url': file_url})

    return jsonify({'success': False, 'message': '허용되지 않는 파일 형식입니다.'}), 400
    
# @app.route('/api/get_pdf_url')
# def get_pdf_url():
#     try:
#         if os.path.exists(OUTPUT_PDF):
#             pdf_url = request.host_url + 'api/pdf?t=' + str(os.path.getmtime(OUTPUT_PDF))
#             return jsonify({'success': True, 'pdfUrl': pdf_url})
#         else:
#             return jsonify({'success': False, 'message': 'PDF 파일이 없습니다.'}), 404
#     except Exception as e:
#         return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), mimetype='application/pdf')
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/get_pdf_url')
def get_pdf_url():
    try:
        if os.path.exists(OUTPUT_PDF_PATH):
            pdf_url = request.host_url + 'uploads/' + OUTPUT_PDF_NAME + '?t=' + str(os.path.getmtime(OUTPUT_PDF_PATH))
            return jsonify({'success': True, 'pdfUrl': pdf_url})
        else:
            return jsonify({'success': False, 'message': 'PDF 파일이 없습니다.'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
