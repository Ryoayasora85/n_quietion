"""
このスクリプトは、MAC環境下での使用想定です。（This script assumes to be used for MAC-PC.）
Argsは、一旦「-s」でfile_pathのみ受けます。-v はverboseです。
TessaractOCR(20210328地点)の精度が問題なく高そうだったので、特別な前処理等は行ってません。画像ファイルにconvertするくらいです。
工数は0.4人日程でした。
"""

import glob
import logging
import os
import pathlib
import sys
from pathlib import Path

import click
import pyocr
import pyocr.builders
from pdf2image import convert_from_path
from PIL import Image

logging.basicConfig(level=logging.DEBUG)


class MakeOcrPdf:
    def __init__(self):

        self._image_dir = pathlib.Path('./images')
        self._txt_dir = pathlib.Path('./txt_file')
        self._pdf_dir = pathlib.Path('./pdfs')

    def self_logger(self, status_code, message, verbose):
        '''
        logging関数
        ログの整形とロギングを行う。
        '''
        def config_info_logging(verbose, log_mes):
            if verbose:
                logging.info(log_mes)
            else:
                pass

        log_mes = str(message)
        if status_code != 0:
            logging.error(log_mes)
            sys.exit()
        else:
            config_info_logging(verbose, log_mes)

    def cleanup(self, verbose):
        """
        output用のディレクトリにファイルがあるときに削除する
        """

        try:
            # リストにファイルが残ってたら削除、空なら何もしない
            def remove_file(file_path):
                if file_path == []:
                    pass
                else:
                    for i in file_path:
                        os.remove(i)

            image_file_path = list(self._image_dir.glob('**/*.*'))
            remove_file(image_file_path)
            # 削除対象のtxtファイルがあるディレクトリ
            txt_dir = pathlib.Path('./txt_file')
            # globでディレクトリ内のtxtファイルをリストで取得
            txt_path = list(txt_dir.glob('**/*.txt'))
            remove_file(txt_path)
            self.self_logger(0, " + cleanup function conplete.", verbose)
        except Exception as e:
            self.self_logger(
                -1, " - Fail to execute cleanup functions : %s" % str(e),
                verbose)

    def pdf_to_image(self, verbose):
        """
        pdfsのディレクトリ内のPDFファイルをJPGに変換する。
        """
        try:
            # poppler/binを環境変数Pathに追加する
            # Path("__file__").parent.resolve()で.pyファイルの親フォルダ絶対パスを返す
            poppler_dir = pathlib.Path(
                "__file__").parent.resolve() / "poppler/bin"
            # pathsepは環境変数に追加するときの区切り；
            os.environ["PATH"] += os.pathsep + str(poppler_dir)

            # globでディレクトリ内のpdfファイルをリストで取得
            pdf_path = list(self._pdf_dir.glob('**/*.pdf'))
            # PDFからimageに
            pages = convert_from_path(str(pdf_path[0]))

            for i, page in enumerate(pages):  # enumerate関数でpagesのpage数を取得
                # .stemでpathの末尾を表示（pathlib)
                file_name = pdf_path[0].stem + "_{:02d}".format(i +
                                                                1) + ".jpeg"
                image_path = self._image_dir / file_name
                # JPEGで保存
                page.save(str(image_path), "JPEG")

            self.self_logger(0, " + pdf_to_image function conplete.", verbose)

        except Exception as e:
            self.self_logger(
                -1, " - Fail to execute pdf_to_image functions : %s" % str(e),
                verbose)

    def ocr_scan(self, local_input_path, verbose):
        """
        JPGに変換されたファイルをOCRスキャンする。
        スキャン結果をtxt_fileに保存する。
        """

        # 拡張子によって分岐（大文字、小文字、入力可）
        file_extension = os.path.splitext(
            os.path.basename(local_input_path))[1]
        file_extension = file_extension.lower()
        if '.pdf' == file_extension:
            self.cleanup(verbose)
            self.pdf_to_image(verbose)
            image_path = list(self._image_dir.glob('**/*.*'))
            self.self_logger(0, image_path, verbose)
        elif '.jpeg' == file_extension or '.jpg' == file_extension or '.jpe' == file_extension or '.png' == file_extension:
            image_path = self._image_dir.glob('**/' + local_input_path)
        else:
            self.self_logger(
                -1,
                " - File Extension is except for PDF, JPG, PNG. Received %s" %
                str(file_extension), verbose)

        # TessaractOCRとPyOCRつかう
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            self.self_logger(-1, " - TessaractOCR is not found", verbose)

        tool = tools[0]
        self.self_logger(0, " + Will use tool '%s'" % (tool.get_name()),
                         verbose)

        try:
            for i in image_path:
                txt = tool.image_to_string(
                    Image.open('./' + str(i)),
                    lang="eng",
                    builder=pyocr.builders.TextBuilder(tesseract_layout=6))
                self.self_logger(0, " + output result : " + str(i), verbose)
                self.self_logger(0, txt, verbose)
                with open('./txt_file/' + str(i.stem) + '.txt',
                          mode='wt') as t:
                    t.write(txt)
            return 0, ' + OK : ocr_scan function complete'
        except Exception as e:
            return -1, " - Ocr Process Faild! : %s" % str(e)


@click.command(help='make ocr pdf')
@click.option('-s',
              '--src-path',
              type=str,
              required=True,
              help='source file path')
@click.option('-v', '--verbose', is_flag=True, help='verbose mode')
def main(src_path, verbose):
    """
    メイン関数
    """
    make_ocr_pdf = MakeOcrPdf()
    local_input_path = src_path
    return_code, return_message = make_ocr_pdf.ocr_scan(
        local_input_path, verbose)
    make_ocr_pdf.self_logger(return_code, return_message, verbose)
    logging.info(
        ' + Successfully Finished! Please check result files in txt_file directory.'
    )


if __name__ == "__main__":
    main()
