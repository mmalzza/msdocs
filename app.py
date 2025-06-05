from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from pdf_filler import fill_pdf
from complaint_filler import fill_pdf as fill_complaint_pdf
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# 공통 설정
UPLOAD_FOLDER = "./uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'pdf'}

# 외국인등록신청서 설정
INPUT_PDF_FOREIGNER = "외국인등록신청서.pdf"
OUTPUT_PDF_FOREIGNER_NAME = "외국인등록신청서_작성완료.pdf"
OUTPUT_PDF_FOREIGNER_PATH = os.path.join(UPLOAD_FOLDER, OUTPUT_PDF_FOREIGNER_NAME)

# 진정서 설정
INPUT_PDF_COMPLAINT = "진정서.pdf"
OUTPUT_PDF_COMPLAINT_NAME = "진정서_작성완료.pdf"
OUTPUT_PDF_COMPLAINT_PATH = os.path.join(UPLOAD_FOLDER, OUTPUT_PDF_COMPLAINT_NAME)

# 현재 상태 저장
current_data_foreigner = {}
current_data_complaint = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 외국인등록신청서 관련 라우터
@app.route('/api/update_foreigner', methods=['POST'])
def update_foreigner_pdf():
    try:
        data = request.json
        field = data.get('field')
        value = data.get('value')

        current_data_foreigner[field] = value

        if os.path.exists(INPUT_PDF_FOREIGNER):
            fill_pdf(INPUT_PDF_FOREIGNER, OUTPUT_PDF_FOREIGNER_PATH, current_data_foreigner)
            return jsonify({
                'success': True,
                'message': f'PDF 파일이 성공적으로 생성되었습니다: {OUTPUT_PDF_FOREIGNER_NAME}',
                'pdf_url': f'/uploads/{OUTPUT_PDF_FOREIGNER_NAME}?t={os.path.getmtime(OUTPUT_PDF_FOREIGNER_PATH)}'
            })
        else:
            return jsonify({'success': False, 'message': '외국인등록신청서 원본 파일이 없습니다.'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/get_foreigner_pdf_url')
def get_foreigner_pdf_url():
    try:
        if os.path.exists(OUTPUT_PDF_FOREIGNER_PATH):
            pdf_url = request.host_url + 'uploads/' + OUTPUT_PDF_FOREIGNER_NAME + '?t=' + str(os.path.getmtime(OUTPUT_PDF_FOREIGNER_PATH))
            return jsonify({'success': True, 'pdfUrl': pdf_url})
        else:
            return jsonify({'success': False, 'message': 'PDF 파일이 없습니다.'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/reset_foreigner', methods=['POST'])
def reset_foreigner_data():
    global current_data_foreigner
    current_data_foreigner = {}
    return jsonify({'success': True, 'message': '외국인등록신청서 데이터 초기화 완료'})


# 진정서 관련 라우터
@app.route('/api/update_complaint', methods=['POST'])
def update_complaint_pdf():
    try:
        data = request.json
        field = data.get('field')
        value = data.get('value')

        current_data_complaint[field] = value

        if os.path.exists(INPUT_PDF_COMPLAINT):
            fill_complaint_pdf(INPUT_PDF_COMPLAINT, OUTPUT_PDF_COMPLAINT_PATH, current_data_complaint)
            return jsonify({
                'success': True,
                'message': f'진정서 PDF가 성공적으로 생성되었습니다: {OUTPUT_PDF_COMPLAINT_NAME}',
                'pdf_url': f'/uploads/{OUTPUT_PDF_COMPLAINT_NAME}?t={os.path.getmtime(OUTPUT_PDF_COMPLAINT_PATH)}'
            })
        else:
            return jsonify({'success': False, 'message': '진정서 원본 파일이 없습니다.'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/get_complaint_pdf_url')
def get_complaint_pdf_url():
    try:
        if os.path.exists(OUTPUT_PDF_COMPLAINT_PATH):
            pdf_url = request.host_url + 'uploads/' + OUTPUT_PDF_COMPLAINT_NAME + '?t=' + str(os.path.getmtime(OUTPUT_PDF_COMPLAINT_PATH))
            return jsonify({'success': True, 'pdfUrl': pdf_url})
        else:
            return jsonify({'success': False, 'message': 'PDF 파일이 없습니다.'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/reset_complaint', methods=['POST'])
def reset_complaint_data():
    global current_data_complaint
    current_data_complaint = {}
    return jsonify({'success': True, 'message': '진정서 데이터 초기화 완료'})

# 파일 업로드 및 제공
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), mimetype='application/pdf')
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

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
        file_url = request.host_url + 'uploads/' + filename
        return jsonify({'success': True, 'file_url': file_url})

    return jsonify({'success': False, 'message': '허용되지 않는 파일 형식입니다.'}), 400
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
