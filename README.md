## Cài đặt môi trường 

- Python 3.6.9
- Java 1.8
- Neo4j 3.5.14

- Cài đặt các thư viện pip:
```bash
pip install -r requirements.txt
```

- Download tokenizer:
```python
python
import nltk
nltk.download('punkt')
exit()
```

- Clone OpenNRE từ github:
```
git clone https://github.com/thunlp/OpenNRE.git --depth 1
```
- Copy file sentence_re.py vào OpenNRE/opennre/framework/:
```bash
cp sentence_re.py OpenNRE/opennre/framework/sentence_re.py
```

- Download Pretrained file:
```bash
cd pretrain
bash download_bert.sh
cd ..
mkdir ckpt
cd ckpt
wget -c https://www.dropbox.com/s/7f70dy2vatmmly4/tacred_bert_softmax.pth.tar
cd ..
```

- Download and upzip Stanfordcore:
```
wget -c http://nlp.stanford.edu/software/stanford-corenlp-full-2018-02-27.zip
upzip stanford-corenlp-full-2018-02-27.zip
rm stanford-corenlp-full-2018-02-27.zip
mv stanford-corenlp-full-2018-02-27 stanford-corenlp
```

## Sử dụng 

- Chạy neo4f service:
```bash
sudo service neo4j start
```

- Chạy service trích xuất các triple:
```bash
python server.py --port 12345
```
- Sử dụng GET request đến server để lấy kết quả trích xuất:
```
localhost:12345?content=Mr. Scheider played the police chief of a resort town menaced by a shark.
```

- Chạy dữ liệu DBpedia:
```bash
python run_dbpedia.py
```

- Chạy dữ liệu Wikipedia:
```bash
python run_wiki.py
```
