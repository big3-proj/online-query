## Requirement
### ptt-data
[download ptt-data](https://drive.google.com/drive/u/2/folders/1D5woLo1_WAI5fVaslqi-pDmnICrhVvr6)  
put users folder & posts.json at the root of the project  
### tagger
[ckipdata](https://github.com/ckiplab/ckiptagger)

## Run
```shell
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

## parse data to database
run
```python
python dataToDB.py 檔案名稱
```