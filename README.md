# dare
�Q�l

���Y�p�C+OpenCV+Streamlit�Ŋ�F�؃A�v���������Ă݂�
https://zenn.dev/ncdc/articles/665eeefb1205ac

OpenCV�̐V������F���������Ă݂�
https://qiita.com/UnaNancyOwen/items/8c65a976b0da2a558f06


DB
| �J������ | �f�[�^�^ | ���e |
| ---- | ---- | ---- |
| id | nchar(36) | uuid |
| name | nvarchar(20) | ���O/�\�z�� |
| face | image | ��摜 |
| feature | varbinary | �����f�[�^ |
| score | int | �m��(���O������100) |


CREATE TABLE facetable (
  id nchar(36) PRIMARY KEY,
  name nvarchar(20),
  face image,
  feature varbinary(800),
  score int
);

DROP TABLE facetable;
