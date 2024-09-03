#!/usr/bin/python3

import os
from ultralytics import YOLO
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from pprint import pprint
import cv2, os, shutil, json
import numpy as np
import asyncio

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/outs"

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

model_name="best_sl_ds01_seg02-1.pt"
########### detect part ##########

model = YOLO(model_name)

async def img_predict(filename, n):
    results = []
    results.append(model.predict(filename, verbose=False, conf=n/10, classes=[0])[0])
    return results

async def run_tasks(filenames, model=model, api=False, tasks=10, indent=4):
    list( map( os.unlink, (os.path.join( app.config['UPLOAD_FOLDER'],f) for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.png')) ) )
    res_list = [{"model" : [
        {"model_name" : model_name},
        {"task" : model.task},
        {"classes" : model.names},
        {"yolo_version" : model.__dict__['ckpt']['version']},
        {"train_date" : model.__dict__['ckpt']['date']},
        {"train_args" : model.__dict__['ckpt']['train_args']}, {"train_metrics" : model.__dict__['ckpt']['train_metrics']}
        ]}]
    res_dict = {}
    for filename in filenames:
        try:
            shutil.copy(filename, f"{app.config['UPLOAD_FOLDER']}/orig.jpg")
        except:
            pass
        tasks = [asyncio.create_task(img_predict(filename, n)) for n in range(tasks)]
        await asyncio.sleep(0)
        async_result = await asyncio.gather(*tasks, return_exceptions=False)
        for rn, result in enumerate(async_result, 1):
            for res in result:
                blank_image = np.zeros(res.orig_shape+(4,), np.uint8)
                try:
##                    ## sum(..., []) is trick for flatten the nested list: from [[x, y]] to [x, y]
##                    res_dict = {'image' : {'name' : filename, 'predictions' : {rn/10 : {'xy' : sum(res.masks.xy.pop().astype(np.int32).reshape(-1, 1, 2).tolist(), [])}}}}
                    res_dict = {'image' : {'name' : filename, 'predictions' : json.loads(res.tojson()) }}
                    res_list.append(res_dict.copy())
                    for im in res.masks.xy:
                        cv2.fillPoly(blank_image, pts=[im.astype(int)], color=(255, 0, 0, 50))
                        cv2.imwrite(f"{app.config['UPLOAD_FOLDER']}/transp_{rn}.png", blank_image)

                except:
                    cv2.imwrite(f"{app.config['UPLOAD_FOLDER']}/transp_{rn}.png", blank_image)
#    print('Final: ', res_list)
#    print('Final (json): \n', json.dumps(res_list, indent=4))
    if api == True:
        return json.dumps(res_list, indent=indent)

########### /detect part ##########


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=['GET', 'POST'])
def root():
    context = {}
    res_list='empty'
    file = ''
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Cannot read the file')
            return redirect(request.url)
        file = request.files['file']
        context['file'] = str(request.files['file'].filename)
        if file.filename == '':
            flash('No selected file!!')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            res_list = asyncio.run(run_tasks([f"{app.config['UPLOAD_FOLDER']}/{filename}"], api=True))
    return render_template("index.html", files=file, values=res_list)

## Example of request:
## curl -s -X POST -F filedata=@code557.jpg http://127.0.0.1:4455/api
## or with beautifing:
## curl -s -X POST -F filedata=@code706.jpg -F indent=4 http://127.0.0.1:4455/api
## or wwth full pathname and via external addrrss:
## curl -s -X POST -F filedata=@S:\tmpp\cvat_export\uploads\code5129.jpg -F indent=4 https://cvat.sphynkx.org.ua/api
@app.route("/api", methods=['GET', 'POST'])
def api():
    file = request.files['filedata']
    try:
        indent = int(request.form['indent'])
    except:
        indent = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(f"{app.config['UPLOAD_FOLDER']}/{filename}")
        res = asyncio.run(run_tasks([f"{app.config['UPLOAD_FOLDER']}/{filename}"], api=True, tasks=10, indent=indent))
    else:
        return json.dumps({"message" : "ERRORA!!"}, indent=indent)
    return res

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4455, debug=True)
