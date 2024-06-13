"""Este é um fork do projeto nfe_utils (https://github.com/edsonbernar/nfe_utils), 
originalmente criado por Edson Bernardino (https://github.com/edsonbernar)."""

import os
from pdf_docs import Danfe
from tqdm import tqdm
import warnings

def printpdf(fullpath, filename, destfolder):
    xmls = [open(fullpath, "r", encoding="utf8").read()]
    pdf = Danfe(xmls=xmls, image=None, cfg_layout='ICMS_IPI', receipt_pos='top')
    pdf.output(f"{destfolder}{str(filename).replace('.xml','.pdf')}")

def ler_paths_xml(pasta):
    arquivos = os.listdir(pasta)
    arquivos_xml = [arquivo for arquivo in arquivos if arquivo.endswith(".xml")]
    return arquivos_xml

if __name__ == "__main__":
    warnings.simplefilter("ignore")
    pastaXML = "XML/"
    paths_xml = ler_paths_xml(pastaXML)
    PastaPDF = "PDF/"

    for path_xml in tqdm(paths_xml, desc="Imprimindo XML to PDF", unit="file"):
        printpdf(f"{pastaXML}{path_xml}", path_xml, PastaPDF)