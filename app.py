from re import DEBUG, sub
from flask import Flask, render_template, request, redirect, send_file, url_for
from flask_ngrok import run_with_ngrok
from werkzeug.utils import secure_filename, send_from_directory
import os
import subprocess

app = Flask(__name__)
run_with_ngrok(app) 

env = os.environ.copy()

uploads_dir = os.path.join(app.instance_path, 'uploads')

os.makedirs(uploads_dir, exist_ok=True)

@app.route("/")
def hello_world():
    return render_template('index.html')


@app.route("/detect", methods=['POST'])
def detect():
    if not request.method == "POST":
        return
    video = request.files['video']
    video.filename = video.filename[:-4] + '_trash' + video.filename[-4:]
    video.save(os.path.join(uploads_dir, secure_filename(video.filename)))
    #print(video)
    # Trash Detection
    result = subprocess.Popen(['python3', 'detect_track.py', '--weights', '/content/gdrive/Shareddrives/DATA 298A/Trash Detection/weights/best.pt', '--save-txt', '--name', 'trash', '--source', os.path.join(uploads_dir, secure_filename(video.filename))], env=env) #'--img', '1920',

    request.files['video'].seek(0)
    video.filename = video.filename.replace("trash", "pplcar")
    video.save(os.path.join(uploads_dir, secure_filename(video.filename)))
    print(video)
    # Car & Person Detection
    result2 = subprocess.Popen(['python3', 'detect_track.py', '--weights', '/content/gdrive/Shareddrives/DATA 298A/People & Car Detection/weights/best.pt', '--save-txt', '--name', 'c&p', '--source', os.path.join(uploads_dir, secure_filename(video.filename))], env=env) #, '--img', '1920'
    # return os.path.join(uploads_dir, secure_filename(video.filename))
    
    std_out, std_err = result.communicate()
    std_out2, std_err2 = result2.communicate()
    
    # Run md_run
    subprocess.run(['python3', 'md_run.py', '--trash_file', 'static/trash/labels/uploads.txt', '--people_file', 'static/c&p/labels/uploads.txt', '--save_path', 'static'], , env=env)
    obj = secure_filename('dumping.csv') # Save dumping output for download
    return obj

@app.route('/return-files', methods=['GET'])
def return_file():
    obj = request.args.get('obj')
    loc = os.path.join("runs/detect", obj)
    print(loc)
    try:
        return send_file(os.path.join("runs/detect", obj), attachment_filename=obj)
        # return send_from_directory(loc, obj)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run()

# @app.route('/display/<filename>')
# def display_video(filename):
# 	#print('display_video filename: ' + filename)
# 	return redirect(url_for('static/video_1.mp4', code=200))
