from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
import PyPDF2
import io
import zipfile
import shutil

app = Flask(__name__)
app.secret_key = 'pdf_splitter_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB限制

# 确保上传和输出文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # 检查是否有文件
    if 'pdf_file' not in request.files:
        flash('没有选择文件')
        return redirect(request.url)
    
    file = request.files['pdf_file']
    
    # 如果用户没有选择文件
    if file.filename == '':
        flash('没有选择文件')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 重定向到拆分页面
        return redirect(url_for('split_options', filename=filename))
    else:
        flash('只允许上传PDF文件!')
        return redirect(request.url)

@app.route('/split-options/<filename>')
def split_options(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # 获取PDF页数
    with open(filepath, 'rb') as f:
        pdf = PyPDF2.PdfReader(f)
        num_pages = len(pdf.pages)
    
    return render_template('split_options.html', filename=filename, num_pages=num_pages)

@app.route('/split', methods=['POST'])
def split_pdf():
    filename = request.form['filename']
    split_type = request.form['split_type']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # 创建输出文件夹
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], os.path.splitext(filename)[0])
    os.makedirs(output_dir, exist_ok=True)
    
    # 打开PDF文件
    with open(filepath, 'rb') as f:
        pdf = PyPDF2.PdfReader(f)
        
        if split_type == 'single':
            # 每页一个PDF
            for i in range(len(pdf.pages)):
                output = PyPDF2.PdfWriter()
                output.add_page(pdf.pages[i])
                
                with open(os.path.join(output_dir, f'page_{i+1}.pdf'), 'wb') as output_file:
                    output.write(output_file)
                    
        elif split_type == 'custom':
            # 自定义页面范围
            ranges = request.form['page_ranges'].split(',')
            for i, page_range in enumerate(ranges):
                output = PyPDF2.PdfWriter()
                
                if '-' in page_range:
                    start, end = map(int, page_range.split('-'))
                    for j in range(start-1, end):
                        output.add_page(pdf.pages[j])
                else:
                    page_num = int(page_range) - 1
                    output.add_page(pdf.pages[page_num])
                
                with open(os.path.join(output_dir, f'range_{i+1}.pdf'), 'wb') as output_file:
                    output.write(output_file)
                    
        elif split_type == 'interval':
            # 按间隔拆分
            interval = int(request.form['interval'])
            num_pages = len(pdf.pages)
            
            for i in range(0, num_pages, interval):
                output = PyPDF2.PdfWriter()
                
                for j in range(i, min(i + interval, num_pages)):
                    output.add_page(pdf.pages[j])
                
                with open(os.path.join(output_dir, f'part_{i//interval+1}.pdf'), 'wb') as output_file:
                    output.write(output_file)
    
    # 创建ZIP文件
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            zf.write(file_path, os.path.basename(file_path))
    
    memory_file.seek(0)
    
    # 清理临时文件
    shutil.rmtree(output_dir)
    os.remove(filepath)
    
    return send_file(
        memory_file,
        download_name=f'{os.path.splitext(filename)[0]}_split.zip',
        as_attachment=True,
        mimetype='application/zip'
    )

if __name__ == '__main__':
    app.run(debug=True) 