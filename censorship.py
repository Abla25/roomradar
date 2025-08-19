#!/usr/bin/env python3
"""
Data Censorship Module

This module provides functionality to censor sensitive data from text content,
particularly focusing on phone numbers while preserving location information
that is useful for zone identification.

Author: RoomRadar Bot System
"""

import re
from typing import Optional


class DataCensor:
    """
    A class to handle censoring of sensitive data from text content.
    
    Focuses primarily on phone numbers to protect privacy while maintaining
    addresses that are useful for identifying zones.
    """
    
    def __init__(self):
        """Initialize the DataCensor with predefined patterns."""
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Set up regex patterns for different types of sensitive data."""
        
        # WhatsApp/Telegram patterns (applied first to avoid conflicts)
        self.messaging_patterns = [
            r'\b(?:whatsapp|telegram|wa|tg)\s*:?\s*(?:\+?39\s*)?(?:3\d{2}\s*[-.\s]?\d{3}\s*[-.\s]?\d{4}|3\d{8})\b',  # Italian
            r'\b(?:whatsapp|telegram|wa|tg)\s*:?\s*(?:\+?34\s*)?(?:6\d{2}\s*[-.\s]?\d{3}\s*[-.\s]?\d{3}|6\d{8})\b',  # Spanish
            r'\b(?:whatsapp|telegram|wa|tg)\s*:?\s*(?:7\d{2}\s*[-.\s]?\d{3}\s*[-.\s]?\d{3}|7\d{8})\b',  # Other formats
            r'\b(?:whatsapp|telegram|wa|tg)\s*:?\s*(?:\+?34\s*)?(?:7\d{2}\s*[-.\s]?\d{3}\s*[-.\s]?\d{3}|7\d{8})\b',  # Spanish 7xx
        ]
        
        # Phone number patterns (comprehensive coverage)
        self.phone_patterns = [
            # Italian numbers with international prefix
            r'(?:\+39\s*)?(?:39\s*)?3\d{2}\s*[-.\s]?\d{3}\s*[-.\s]?\d{4}\b',
            r'(?:\+39\s*)?(?:39\s*)?3\d{8}\b',
            
            # Spanish numbers with international prefix  
            r'(?:\+34\s*)?(?:34\s*)?6\d{2}\s*[-.\s]?\d{3}\s*[-.\s]?\d{3}\b',
            r'(?:\+34\s*)?(?:34\s*)?6\d{8}\b',
            r'(?:\+34\s*)?(?:34\s*)?7\d{2}\s*[-.\s]?\d{3}\s*[-.\s]?\d{3}\b',
            r'(?:\+34\s*)?(?:34\s*)?7\d{8}\b',
            
            # Generic patterns for numbers starting with 6 or 7 (common in Spain)
            r'\b[67]\d{2}\s*[-.\s]?\d{3}\s*[-.\s]?\d{3}\b',
            r'\b[67]\d{8}\b',
            
            # Italian numbers without prefix
            r'\b3\d{2}\s*[-.\s]?\d{3}\s*[-.\s]?\d{4}\b',
            r'\b3\d{9}\b',
        ]
        
        # Email pattern
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Italian fiscal code pattern (16 alphanumeric characters)
        self.fiscal_code_pattern = r'\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b'
        
        # Italian VAT number pattern (11 digits) - excludes phone numbers
        self.vat_pattern = r'\b(?!3\d{10})(?!6\d{10})(?!7\d{10})\d{11}\b'
    
    def censor_text(self, text: Optional[str]) -> str:
        """
        Censor sensitive data from the given text.
        
        Args:
            text: The text to censor
            
        Returns:
            The censored text with sensitive data replaced by placeholders
        """
        if not text:
            return text
        
        censored_text = text
        
        # 1. Censor messaging apps with phone numbers first (most specific)
        for pattern in self.messaging_patterns:
            censored_text = re.sub(pattern, '[MESSAGING CONTACT CENSORED]', censored_text, flags=re.IGNORECASE)
        
        # 2. Censor email addresses
        censored_text = re.sub(self.email_pattern, '[EMAIL CENSORED]', censored_text)
        
        # 3. Censor Italian fiscal codes
        censored_text = re.sub(self.fiscal_code_pattern, '[FISCAL CODE CENSORED]', censored_text)
        
        # 4. Censor VAT numbers (excluding phone numbers)
        censored_text = re.sub(self.vat_pattern, '[VAT NUMBER CENSORED]', censored_text)
        
        # 5. Censor phone numbers (after handling messaging apps)
        for pattern in self.phone_patterns:
            censored_text = re.sub(pattern, '[PHONE NUMBER CENSORED]', censored_text, flags=re.IGNORECASE)
        
        return censored_text
    
    def has_sensitive_data(self, text: Optional[str]) -> bool:
        """
        Check if the text contains sensitive data that would be censored.
        
        Args:
            text: The text to check
            
        Returns:
            True if sensitive data is found, False otherwise
        """
        if not text:
            return False
        
        # Check all patterns
        all_patterns = (
            self.messaging_patterns + 
            self.phone_patterns + 
            [self.email_pattern, self.fiscal_code_pattern, self.vat_pattern]
        )
        
        for pattern in all_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def get_censorship_stats(self, text: Optional[str]) -> dict:
        """
        Get statistics about what types of sensitive data were found.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary with counts of different types of sensitive data
        """
        if not text:
            return {}
        
        stats = {
            'messaging_contacts': 0,
            'phone_numbers': 0,
            'emails': 0,
            'fiscal_codes': 0,
            'vat_numbers': 0
        }
        
        # Count messaging contacts
        for pattern in self.messaging_patterns:
            stats['messaging_contacts'] += len(re.findall(pattern, text, re.IGNORECASE))
        
        # Count phone numbers (excluding those already counted as messaging)
        temp_text = text
        for pattern in self.messaging_patterns:
            temp_text = re.sub(pattern, '', temp_text, flags=re.IGNORECASE)
        
        for pattern in self.phone_patterns:
            stats['phone_numbers'] += len(re.findall(pattern, temp_text, re.IGNORECASE))
        
        # Count other types
        stats['emails'] = len(re.findall(self.email_pattern, text))
        stats['fiscal_codes'] = len(re.findall(self.fiscal_code_pattern, text))
        stats['vat_numbers'] = len(re.findall(self.vat_pattern, text))
        
        return stats


# Global instance for easy importing
censor = DataCensor()


def censor_sensitive_data(text: Optional[str]) -> str:
    """
    Convenience function to censor sensitive data from text.
    
    Args:
        text: The text to censor
        
    Returns:
        The censored text
    """
    return censor.censor_text(text)


def has_sensitive_data(text: Optional[str]) -> bool:
    """
    Convenience function to check if text contains sensitive data.
    
    Args:
        text: The text to check
        
    Returns:
        True if sensitive data is found
    """
    return censor.has_sensitive_data(text)


def get_censorship_stats(text: Optional[str]) -> dict:
    """
    Convenience function to get censorship statistics.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dictionary with statistics
    """
    return censor.get_censorship_stats(text)


if __name__ == "__main__":
    # Test the censorship functionality
    test_texts = [
        "Alquilo habitación en igualada ver ubicación en apartamento dúplex parejas asepto nenes para alquilar ya quién Page se la queda! Sitio amplio y tranquilo empadronó los nenes para el cole 603597082",
        "Hola buenas tengo una habitacion disponible para el mes de septiembre precio 400 todo incluido , para una persona, ubicada por el metro fondo Santa coloma de gramanet para mas informcion escriba solo al whatsApp 632338093",
        "Se alquila habitación individual a chica, en Badalona línea L2 del metro. Cerca de Mercadona, Lidel, Condi, Farmacias y líneas de Bus. 400€ con todos los gastos incluidos. 641919781 solo llamadas.",
        "Contact me at mario.rossi@gmail.com or call +39 333 123 4567"
    ]
    
    print("🔒 DATA CENSORSHIP MODULE TEST")
    print("=" * 60)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 TEST {i}:")
        print(f"Original: {text}")
        
        censored = censor_sensitive_data(text)
        print(f"Censored: {censored}")
        
        stats = get_censorship_stats(text)
        if any(stats.values()):
            print(f"Stats: {stats}")
        
        print("-" * 60)
