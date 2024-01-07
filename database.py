# -*- coding: utf-8 -*-

import os
import base64
import pymssql
import time
import pickle

'''
a = ["abc", 123]
ba = pickle.dumps(a)
_a = pickle.loads(ba)
print(_a)
'''

DB_SERVER = os.environ['DB_SERVER']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_DATABASE = os.environ['DB_DATABASE']

# DBに接続
def connect():
  while True:
    try:
      conn = pymssql.connect(
        server = DB_SERVER,
        user = DB_USER,
        password = DB_PASSWORD,
        database = DB_DATABASE,
        as_dict = True
      )
      break
    except Exception as e:
      print(e)
      time.sleep(1)
  return conn

# レコード追加
def insert_all(id, name, jpg, npy, score):
  print("DB insert_all", id, name, score)
  pic_jpg = pickle.dumps(jpg)
  pic_npy = pickle.dumps(npy)
  with connect() as conn:
    with conn.cursor() as cur:
      cur.execute('INSERT INTO facetable (id, name, face, feature, score) VALUES (%s, %s, %s, %s, %s)',
        (id, name, pic_jpg, pic_npy, score)
      )
      #cur.execute('INSERT INTO facetable (id, name, face, odds) VALUES (%s, %s, %s, %s)',
      #  (id, name, pic_jpg, odds)
      #)
      #cur.execute('INSERT INTO facetable (id, name, odds) VALUES (%s, %s, %s)',
      #  (id, name, odds)
      #)
    conn.commit()

# キャッシュテーブル作成
def make_dictionary():
  print("DB make_dictionary")
  with connect() as conn:
    with conn.cursor() as cur:
      cur.execute("SELECT id, name, feature FROM facetable")
      rows = cur.fetchall()
  dictionary = []
  for row in rows:
    if row['name'] and row['feature']:
      dictionary.append([row['id'], row['name'], pickle.loads(row['feature'])])
  return dictionary

# 全データ列挙
def get_all():
  print("DB get_all")
  with connect() as conn:
    with conn.cursor() as cur:
      cur.execute("SELECT id, name FROM facetable")
      rows = cur.fetchall()
  return rows

# 未確定のデータ列挙
def get_notconfirmed():
  print("DB get_notconfirmed")
  with connect() as conn:
    with conn.cursor() as cur:
      cur.execute("SELECT id, name, score FROM facetable WHERE score IS NOT NULL")
      rows = cur.fetchall()
  return rows

# 指定IDの画像を取得
def get_image(id):
  print("DB get_image", id)
  with connect() as conn:
    with conn.cursor() as cur:
      cur.execute("SELECT face FROM facetable WHERE id=%s",(id,))
      row = cur.fetchone()
  return pickle.loads(row['face'])

# 指定IDのデータ変更
def update_data(id, name, score):
  print("DB update_data", id, name, score)
  with connect() as conn:
    with conn.cursor() as cur:
      cur.execute("UPDATE facetable SET name=%s, score=%s WHERE id=%s",(name, score, id,))
    conn.commit()

# 指定IDのデータ変更
def delete(id):
  print("DB delete", id)
  with connect() as conn:
    with conn.cursor() as cur:
      cur.execute("DELETE FROM facetable WHERE id=%s",(id,))
    conn.commit()


'''
def get_studio():
  print("DB get_studio")
  with connect() as conn:
    with conn.cursor() as cur:
      cur.execute("SELECT * FROM facetable")
      #rows = cur.fetchone()
      rows = cur.fetchall()
  return rows


def insert_staff(id, name, odds):
  print("DB insert_staff")
  with connect() as conn:
    with conn.cursor() as cur:
      #cur.execute('INSERT INTO facetable (id, name, odds) VALUES (%s, %s, %d)',
      cur.execute('INSERT INTO facetable (id, name, odds) VALUES (?, ?, ?)',
        (id, name, odds)
      )
    conn.commit()

def insert(id, name, jpgf, npyf, odds):
  print("DB insert_staff")
  with open(jpgf, mode='rb') as f:
    jpg = f.read()
  with open(npyf, mode='rb') as f:
    npy = f.read()
  with connect() as conn:
    with conn.cursor() as cur:
      cur.execute('INSERT INTO facetable (id, name, face, feature, odds) VALUES (%s, %s, %s, %s, %s)',
        (id, name, jpg, npy, odds)
      )
    conn.commit()


#insert('hhhh', 'koto', 'temp/ed69e13b-7630-416f-80f3-3a21377c2d29_001.jpg', 'temp/ed69e13b-7630-416f-80f3-3a21377c2d29_001.npy', 10)
#get_studio()
ret = get_s('kouto')
with open('./temp/tmp.jpg', mode='wb') as f:
  f.write(ret['face'])
with open('./temp/tmp.npy', mode='wb') as f:
  f.write(ret['feature'])


import numpy as np

a = np.load('temp/ed69e13b-7630-416f-80f3-3a21377c2d29_001.npy')
print(a)
'''
