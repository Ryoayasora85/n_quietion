# Cording Question

OCRスクリプト
以下に説明するpreparationのディレクトリに、PDFファイルもしくは、画像ファイルを配置する事で使用できる。

## preparation

n_quietion/cording_question/pdfs/*.pdf ---------- OCR解析したいPDFファイルを配置してください。
n_quietion/cording_question/images/*..jpeg ------ 解析したい画像ファイルを配置してください。（ただし、PNG, JPGに限る）

## Requirement
 
必要とするライブラリ
 
* click 7.1.2
* pdf2image 1.14.0
* Pillow 8.1.2
* pyocr 0.8

## Argument

```bash
Options:
  -s, --src-path TEXT  source file path  [required]
  -v, --verbose        verbose mode
  --help               Show this message and exit.
```

## Requirementで列挙したライブラリなどのインストール方法と実行方法
 
```bash
git clone https://github.com/Ryoayasora85/n_quietion.git
cd n_quietion/cording_question

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python make_ocr_pdf.py -s sample_image_english_agreement_pdf_01.pd -v

deactivate
```

## OutPut先

n_quietion/cording_question/txt_file/*.txt
 
## Note
 
使用想定環境
macOS Big Sur バージョン 11.2.3

言語
Python 3.8.6

PIPバージョン
pip 20.2.4
 
