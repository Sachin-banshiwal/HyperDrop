from flask import Flask, request, send_file, render_template_string
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quick File Sharing</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 flex items-center justify-center min-h-screen">
    <div class="w-full max-w-lg bg-white shadow-md rounded-lg p-6">
        <h1 class="text-2xl font-bold text-center mb-4">Quick File Sharing</h1>
        
        <div class="mb-6">
            <h2 class="text-lg font-semibold mb-2">Upload File</h2>
            <form action="/upload" method="post" enctype="multipart/form-data" class="flex flex-col gap-3">
                <input type="file" name="file" required class="border p-2 rounded">
                <input type="submit" value="Upload" class="bg-blue-500 text-white py-2 rounded hover:bg-blue-600 cursor-pointer">
            </form>
        </div>
        
        <div>
            <h2 class="text-lg font-semibold mb-2">Available Files</h2>
            <ul class="list-disc pl-5 space-y-1">
                {% for file in files %}
                    <li>
                        <a href="/download/{{ file }}" class="text-blue-500 hover:underline">{{ file }}</a>
                    </li>
                {% endfor %}
            </ul>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template_string(HTML_TEMPLATE, files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return 'No file selected', 400
        file = request.files['file']
        if file.filename == '':
            return 'No file selected', 400
            
        filename = os.path.basename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(file_path)
        
        download_url = request.host_url + 'download/' + filename
        return f'''File uploaded successfully!<br>
                  Public URL: <a href="{download_url}">{download_url}</a>
                  <br><br><a href="/">Back to home</a>''', 200
    except Exception as e:
        app.logger.error(f"Upload error: {str(e)}")
        return "Error uploading file", 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        safe_filename = os.path.basename(filename)
        file_path = os.path.join(os.path.abspath(UPLOAD_FOLDER), safe_filename)
        
        if not os.path.exists(file_path) or not file_path.startswith(os.path.abspath(UPLOAD_FOLDER)):
            return "File not found", 404
        
        return send_file(file_path, as_attachment=True, download_name=safe_filename)
    except Exception as e:
        app.logger.error(f"Download error: {str(e)}")
        return "Error downloading file", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
