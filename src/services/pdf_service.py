"""
PDF extraction service.
Single Responsibility: Handle PDF file reading and text extraction.
"""

import fitz  # PyMuPDF
import logging
from typing import Tuple
from pathlib import Path

from src.core.exceptions import (
    InvalidPDFException,
    EmptyPDFException,
    PDFSizeException,
    PDFExtractionException
)
from src.core.config import get_settings

logger = logging.getLogger(__name__)


class PDFService:
    """
    Service for extracting text from PDF files.
    
    Responsibilities:
    - Read PDF file
    - Extract text using PyMuPDF
    - Validate PDF integrity
    - Handle errors gracefully
    """
    
    def __init__(self):
        """Initialize PDF service with configuration."""
        self.settings = get_settings()
        self.max_size_bytes = self.settings.MAX_PDF_SIZE_MB * 1024 * 1024
    
    def extract_text(self, pdf_bytes: bytes) -> str:
        """
        Extract text from PDF file.
        
        Args:
            pdf_bytes: PDF file contents as bytes
            
        Returns:
            str: Extracted text from PDF
            
        Raises:
            PDFSizeException: If PDF exceeds size limit
            InvalidPDFException: If PDF is corrupted
            EmptyPDFException: If PDF contains no text
            PDFExtractionException: For other PDF errors
        """
        # Validate file size
        file_size = len(pdf_bytes)
        logger.info(f"Processing PDF of size: {file_size} bytes")
        
        if file_size > self.max_size_bytes:
            logger.error(f"PDF size {file_size} exceeds limit {self.max_size_bytes}")
            raise PDFSizeException(
                message=f"PDF file exceeds maximum size of {self.settings.MAX_PDF_SIZE_MB}MB",
                details=f"File size: {file_size / (1024*1024):.2f}MB"
            )
        
        pdf_document = None
        try:
            # Open PDF from bytes
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            logger.info(f"PDF opened successfully, pages: {pdf_document.page_count}")
            
            # Validate that PDF is not empty
            if pdf_document.page_count == 0:
                logger.error("PDF file contains no pages")
                raise EmptyPDFException(
                    message="PDF file is empty",
                    details="PDF contains no pages"
                )
            
            # Extract text from all pages
            extracted_text = self._extract_text_from_pages(pdf_document)
            
            # Validate extracted text
            if not extracted_text or not extracted_text.strip():
                logger.warning("No text could be extracted from PDF")
                raise EmptyPDFException(
                    message="PDF contains no extractable text",
                    details="All pages are empty or image-only"
                )
            
            logger.info(f"Text extracted successfully, length: {len(extracted_text)} characters")
            return extracted_text.strip()
        
        except fitz.FileDataError as e:
            logger.error(f"Invalid PDF file: {str(e)}")
            raise InvalidPDFException(
                message="PDF file is corrupted or invalid",
                details=str(e)
            )
        except EmptyPDFException:
            raise
        except PDFSizeException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during PDF extraction: {str(e)}")
            raise PDFExtractionException(
                message="An error occurred while extracting text from PDF",
                details=str(e)
            )
        finally:
            if pdf_document:
                pdf_document.close()
    
    def _extract_text_from_pages(self, pdf_document: fitz.Document) -> str:
        """
        Extract text from all pages in PDF document.
        
        Args:
            pdf_document: Opened PyMuPDF document
            
        Returns:
            str: Concatenated text from all pages
        """
        text_parts = []
        
        for page_num in range(pdf_document.page_count):
            try:
                page = pdf_document[page_num]
                page_text = page.get_text()
                
                if page_text.strip():
                    text_parts.append(page_text)
                    logger.debug(f"Page {page_num + 1} extracted, length: {len(page_text)}")
            except Exception as e:
                logger.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
                # Continue with next page instead of failing
                continue
        
        return "\\n\\n".join(text_parts)
