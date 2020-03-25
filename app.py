#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response
from flask import Flask, redirect, url_for

import subprocess
from subprocess import Popen, PIPE
from subprocess import check_output
from flask import Flask
from flask import request

def get_shell_script_output_using_communicate():
    session = subprocess.Popen(['/home/pi/OPENCV_EXAMPLE/flask-video-streaming/some.sh'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = session.communicate()
    if stderr:
        raise Exception("Error "+str(stderr))
    return stdout.decode('utf-8')

def get_shell_script_output_using_check_output():
    stdout = check_output(['/home/pi/OPENCV_EXAMPLE/flask-video-streaming/some.sh']).decode('utf-8')
    return stdout

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

# Raspberry Pi camera module (requires picamera package)
from camera_pi import Camera

app = Flask(__name__)


BIRD_FOLDER = os.path.join('images', 'photos')
app.config['UPLOAD_FOLDER'] = BIRD_FOLDER

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/playfm/', methods=['GET', 'POST'])
def playfm():
    return '<pre>'+get_shell_script_output_using_check_output()+'</pre>'

@app.route('/say/')
def say():
    return render_template('say.html')
    
@app.route('/say/', methods=['POST'])
def say_post():
    text = request.form['text']
    processed_text = text.upper()
    stdout = check_output(['/home/pi/OPENCV_EXAMPLE/flask-video-streaming/say.sh', processed_text ]).decode('utf-8')
    return redirect(url_for('say'))
  

@app.route('/photos/')
def photos():
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], '1.jpg')
    return render_template("photos.html", user_image = full_filename)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=8082, threaded=True)
