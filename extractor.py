from docx import Document
import pymupdf
import pandas as pd
from rag import file_analysis
from logger import get_logger

logger = get_logger(__name__)
logger.info("Extractor module loaded")

def extract_pdf(file):
    """
    Extracts text from a PDF file and returns a structured summary.
    """

    logger.info(f"extract_pdf() called for file: {getattr(file, 'filename', 'unknown')}")
    try:
        pdf = pymupdf.open(stream = file.read())
        text=''
        for page in pdf:
            text += page.get_text() + '\n'
        logger.info(f"Pdf Content Extracted")
        result = file_analysis.summarize(text)

        logger.info(f"Pdf Summarization Completed")
        return result
    except Exception as e:
        logger.error(f"Extract_pdf() failed: {e}", exc_info=True)
        raise

    
    
def extract_docx(file):
    """
    Extracts text from a Docx file and returns a structured summary.
    """

    logger.info(f"extract_docx() called for file: {getattr(file, 'filename', 'Unknown')}")
    try:
        doc = Document(file)
        text = ''
        for paragraph in doc.paragraphs:
            text += paragraph.text + '\n'
        logger.info("Docx Content Extracted")
        result = file_analysis.summarize(text)

        logger.info("Docx Summarization Completed")
        return result
    except Exception as e:
        logger.error(f"extract_docx() failed: {e}", exc_info=True)


def extract_csv(file):
    """
    Extracts text from a CSV file and returns a structured summary.
    """

    logger.info(f"extract_csv() called for file: {getattr(file, 'filename', 'Unknown')}")
    try:
        df  =  pd.read_csv(file)
        text = f"""
            Rows: {df.shape[0]}
            Columns: {df.shape[1]}
            Columns_Names: {list(df.columns)}
            Data types: {df.dtypes.to_dict()}
            First Five rows: {df.head().to_string()}
            Basic Statistics: {df.describe().to_string()}
        """
        logger.info("CSV Content Extracted")
        result = file_analysis.summarize(text)

        logger.info("CSV Summarization Completed")
        return result
    except Exception as e:
        logger.error(f"extract_csv failed: {e}", exc_info=True)

    
    
def extract_markdown(file):
    """
    Extracts text from a PDF file and returns a structured summary.
    """

    logger.info(f"extract_markdown() called for file: {getattr(file,'filename', 'Unknown')}")
    try:
        text = file.read().decode('utf-8')
        logger.info("MD Content Extracted")

        result = file_analysis.summarize(text)
        logger.info("Md Summarization Completed")

        return result
    except Exception as e:
        logger.error(f"extract_markdown() failed: {e}", exc_info=True)



Extractor = {
    '.docx': extract_docx,
    '.pdf': extract_pdf,
    '.csv': extract_csv,
    '.md': extract_markdown,
}
logger.debug(f"Extractor registry built for types: {list(Extractor.keys())}")


def document_classifier(file_type, file):
    """
    Routes the file to the correct extractor based on its extension and returns the summary.
    """
    
    logger.info(f"document_classifier() called | file_type='{file_type}'")

    extract = Extractor.get(file_type)

    if extract is None:
        logger.warning("Unsupported file type")
        return "The File Is not supported Currently"
    
    logger.debug(f"Dispatching to extractor: {extract.__name__}")
    text = extract(file)
    logger.info(f"document_classifier() completed for type '{file_type}'")
    return text


 
    