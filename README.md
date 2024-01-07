# dare
参考

ラズパイ+OpenCV+Streamlitで顔認証アプリをつくってみた
https://zenn.dev/ncdc/articles/665eeefb1205ac

OpenCVの新しい顔認識を試してみる
https://qiita.com/UnaNancyOwen/items/8c65a976b0da2a558f06


DB
| カラム名 | データ型 | 内容 |
| ---- | ---- | ---- |
| id | nchar(36) | uuid |
| name | nvarchar(20) | 名前/予想名 |
| face | image | 顔画像 |
| feature | varbinary | 特徴データ |
| score | int | 確率(名前決定後は100) |


CREATE TABLE facetable (
  id nchar(36) PRIMARY KEY,
  name nvarchar(20),
  face image,
  feature varbinary(800),
  score int
);

DROP TABLE facetable;
