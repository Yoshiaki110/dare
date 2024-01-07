# -*- coding: utf-8 -*-

import os
import time
from flask import Flask, redirect, render_template, request, jsonify, make_response, send_file, Response
import base64
import uuid
from PIL import Image
#import socket
from io import BytesIO
#import datetime
#import requests
import json
import numpy as np
import cv2
import database

weights_detector = "onnx/yunet_n_640_640.onnx"
weights_recognizer = "onnx/face_recognizer_fast.onnx"
TEMP_DIR = './temp/'

app = Flask(__name__)

# モデルを読み込む
face_detector = cv2.FaceDetectorYN_create(weights_detector, "", (0, 0))
face_recognizer = cv2.FaceRecognizerSF_create(weights_recognizer, "")

# データベースから特徴をキャッシュに読み込む
dictionary = database.make_dictionary()

# 特徴を辞書と比較してマッチしたユーザーとスコアを返す関数
def match(feature1):
    global dictionary
    ret = ('不明', 0.0)
    for element in dictionary:
        id, name, feature2 = element
        score = face_recognizer.match(feature1, feature2, cv2.FaceRecognizerSF_FR_COSINE)
        if score > ret[1]:
            ret = (name, score)
    return ret

# 顔を抽出
def fase_detect(path):
    global dictionary
    ret = []
    directory = os.path.dirname(path)

    # 画像を開く
    image = cv2.imread(path)

    # 画像が3チャンネル以外の場合は3チャンネルに変換する
    channels = 1 if len(image.shape) == 2 else image.shape[2]
    if channels == 1:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if channels == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

    # 入力サイズを指定する
    height, width, _ = image.shape
    face_detector.setInputSize((width, height))

    # 顔を検出する
    try:
        _, faces = face_detector.detect(image)
    except Exception as e:
        print(e)
        faces = None

    # 検出された顔を切り抜く
    if faces is None:
        return 0
    for face in faces:
        aligned_face = face_recognizer.alignCrop(image, face)
        # 顔画像を保存する
        id = str(uuid.uuid4())
        aligned_face_fname = os.path.join(directory, id + ".jpg")
        cv2.imwrite(aligned_face_fname, aligned_face)

        # 特徴を抽出する
        face_feature = face_recognizer.feature(aligned_face)
        # 特徴を保存する
        #feature_fname = os.path.join(directory, filename)
        #np.save(feature_fname, face_feature)

        name, score = match(face_feature)
        score = int(score * 100)
        # データベースに追加
        database.insert_all(id, name, aligned_face, face_feature, score)
        print('inserted', id, name, score)
        # キャッシュに追加
        dictionary.append([id, name, face_feature])
        ret.append({'id': id, 'name': name, 'score': score})
    return ret

@app.route('/')
def root():
    print("** / " + request.method)
    resp = make_response(render_template("prof.html"))
    return resp

@app.route('/paste')
def paste():
    print("** /paste " + request.method)
    resp = make_response(render_template("paste.html"))
    return resp

@app.route('/all')
def all():
    print("** /all " + request.method)
    ar = database.get_all()
    resp = make_response(render_template("all.html", array=ar))
    return resp

@app.route('/modify', methods=['GET', 'POST', 'DELETE'])
def modify():
    global dictionary
    print("** /modify " + request.method)
    if request.method == 'GET':
        #ar = []
        #ar.append({'id': 'd1767d29-7ac3-4e49-835f-a9f53c2e1178', 'name': 'いとう', 'score': 12})
        #ar.append({'id': 'eb77ab08-321d-49fd-a011-3a323b09be6f', 'name': 'さとう', 'score': 34})
        ar = database.get_notconfirmed()
        resp = make_response(render_template("modify.html", array=ar))
        return resp
    if request.method == 'POST':
        id = request.json['id']
        name = request.json['name']
        print(id, name)
        database.update_data(id, name, None)
        for element in dictionary:
            if element[0] == id:
                element[1] = name
                break
        return make_response(jsonify({'result': 0}))
    if request.method == 'DELETE':
        ids = request.json['ids']
        for id in ids:
            database.delete(id)
        dictionary = [i for i in dictionary if i[0] not in ids]
        return make_response(jsonify({'result': 0}))

@app.route('/axios', methods=['POST'])
def axios():
    print('/axios')
    base64_png = request.form['image']
    code = base64.b64decode(base64_png.split(',')[1])  # remove header
    try:
        image_decoded = Image.open(BytesIO(code))
    except:
        return make_response(jsonify({'result': 0}))
    tmpFileName = TEMP_DIR + str(uuid.uuid4()) + '_all.jpg'
    image_decoded.save(tmpFileName)

    ret = fase_detect(tmpFileName)
    #return make_response(jsonify({'result': len(ret)}))
    return make_response(jsonify({'result': ret}))

@app.route('/test', methods=['GET', 'POST'])
def test():
    print("** /test " + request.method)
    if request.method == 'GET':
        resp = make_response(render_template("test.html"))
        return resp
    if request.method == 'POST':
        if 'uploadFile' not in request.files or '' == request.files['uploadFile'].filename:
            return make_response(jsonify('no image'))
        file = request.files['uploadFile']
        tmpFileName = TEMP_DIR + str(uuid.uuid4()) + '_all.jpg'
        file.save(tmpFileName)
        ret = fase_detect(tmpFileName)
        return make_response(jsonify('found ' + str(len(ret)) + ' pictures'))

# 指定のimg_idの非公開画像を返す
@app.route("/image")
def iamge():
    if not ('QUERY_STRING' in request.headers.environ):
        return Response(response=json.dumps({'message': 'no query string'}), status=400)
    qs = request.headers.environ['QUERY_STRING'].split('&')
    id = '' if len(qs) == 0 else qs[0]
    print('/image?' + str(id))
    if id == '':
        return Response(response=json.dumps({'message': 'no id'}), status=400)
    image = database.get_image(id)
    if image is None:
        return Response(response=json.dumps({'message': 'not found'}), status=400)
    tmpFileName = TEMP_DIR + str(uuid.uuid4()) + '.jpg'
    #with open(tmpFileName, mode='wb') as f:
    #    f.write(image)
    cv2.imwrite(tmpFileName, image)
    # サイズを200ピクセルに縮小
    img = Image.open(tmpFileName)
    if 200 < img.width:            # 200ピクセル以上の場合のみ縮小
        ratio = 200 / img.width
        width = img.width * ratio
        height = img.height * ratio
        img_resize = img.resize((int(width), int(height)))
        img_resize.save(tmpFileName)

    #return '200'
    return send_file(tmpFileName, mimetype='image/jpg')

if __name__ == '__main__':
    app.run(debug=True)

