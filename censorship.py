#!/usr/bin/env python3
"""
Data Censorship Module - Optimized Version

This module provides high-performance functionality to censor sensitive data from text content,
particularly focusing on phone numbers while preserving location information
that is useful for zone identification.

Author: RoomRadar Bot System
"""

import re
from typing import Optional


class DataCensor:
    """
    A high-performance class to handle censoring of sensitive data from text content.
    
    Focuses primarily on phone numbers to protect privacy while maintaining
    addresses that are useful for identifying zones.
    """
    
    def __init__(self):
        """Initialize the DataCensor with pre-compiled patterns for maximum performance."""
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Set up pre-compiled regex patterns for different types of sensitive data."""
        
        # Pre-compile all patterns for maximum performance
        
        # WhatsApp/Telegram patterns (applied first to avoid conflicts)
        # Enhanced to catch more variations
        self.messaging_patterns = [
            # Italian messaging patterns
            re.compile(r'\b(?:whatsapp|telegram|wa|tg|w\.a|t\.g)\s*:?\s*(?:\+?39\s*)?(?:3\d{2}\s*[-.\s]+\d{3}\s*[-.\s]+\d{4}|3\d{8,9})\b', re.IGNORECASE),
            # Spanish messaging patterns  
            re.compile(r'\b(?:whatsapp|telegram|wa|tg|w\.a|t\.g)\s*:?\s*(?:\+?34\s*)?(?:[67]\d{2}\s*[-.\s]+\d{3}\s*[-.\s]+\d{3}|[67]\d{8})\b', re.IGNORECASE),
            # Generic messaging patterns
            re.compile(r'\b(?:whatsapp|telegram|wa|tg|w\.a|t\.g)\s*:?\s*(?:\+?\d{1,3}\s*)?(?:[67]\d{2}\s*[-.\s]+\d{3}\s*[-.\s]+\d{3}|[67]\d{8})\b', re.IGNORECASE),
        ]
        
        # Comprehensive phone number patterns - Enhanced to catch ALL variations
        # IMPORTANT: Only numbers with 8+ digits are considered phone numbers (to preserve prices)
        self.phone_patterns = [
            # Italian numbers with all possible formats (8-10 digits only)
            re.compile(r'(?:\+39\s*)?(?:39\s*)?3\d{2}\s*[-.\s]+\d{3}\s*[-.\s]+\d{4}\b', re.IGNORECASE),
            re.compile(r'(?:\+39\s*)?(?:39\s*)?3\d{8,9}\b', re.IGNORECASE),
            re.compile(r'(?:\+39\s*)?(?:39\s*)?\(?3\d{2}\)?\s*[-.\s]*\d{3}\s*[-.\s]*\d{4}\b', re.IGNORECASE),
            
            # Spanish numbers with all possible formats (8-9 digits only)
            re.compile(r'(?:\+34\s*)?(?:34\s*)?[67]\d{2}\s*[-.\s]+\d{3}\s*[-.\s]+\d{3}\b', re.IGNORECASE),
            re.compile(r'(?:\+34\s*)?(?:34\s*)?[67]\d{8}\b', re.IGNORECASE),
            re.compile(r'(?:\+34\s*)?(?:34\s*)?\(?[67]\d{2}\)?\s*[-.\s]*\d{3}\s*[-.\s]*\d{3}\b', re.IGNORECASE),
            
            # Generic patterns for numbers starting with 6 or 7 (common in Spain) - 8+ digits only
            re.compile(r'\b[67]\d{2}\s*[-.\s]+\d{3}\s*[-.\s]+\d{3}\b', re.IGNORECASE),
            re.compile(r'\b[67]\d{8}\b', re.IGNORECASE),
            re.compile(r'\b\(?[67]\d{2}\)?\s*[-.\s]*\d{3}\s*[-.\s]*\d{3}\b', re.IGNORECASE),
            
            # Italian numbers without prefix - all formats (9+ digits only)
            re.compile(r'\b3\d{2}\s*[-.\s]+\d{3}\s*[-.\s]+\d{4}\b', re.IGNORECASE),
            re.compile(r'\b3\d{9}\b', re.IGNORECASE),
            re.compile(r'\b\(?3\d{2}\)?\s*[-.\s]*\d{3}\s*[-.\s]*\d{4}\b', re.IGNORECASE),
            
            # Additional patterns for edge cases (8+ digits only)
            # Numbers with multiple spaces
            re.compile(r'\b[67]\d{2}\s{2,}\d{3}\s{2,}\d{3}\b', re.IGNORECASE),
            re.compile(r'\b3\d{2}\s{2,}\d{3}\s{2,}\d{4}\b', re.IGNORECASE),
            
            # Numbers with mixed separators (8+ digits only)
            re.compile(r'\b[67]\d{2}[-.\s]+\d{3}[-.\s]+\d{3}\b', re.IGNORECASE),
            re.compile(r'\b3\d{2}[-.\s]+\d{3}[-.\s]+\d{4}\b', re.IGNORECASE),
            
            # Numbers with parentheses and spaces (8+ digits only)
            re.compile(r'\b\([67]\d{2}\)\s*[-.\s]*\d{3}\s*[-.\s]*\d{3}\b', re.IGNORECASE),
            re.compile(r'\b\(3\d{2}\)\s*[-.\s]*\d{3}\s*[-.\s]*\d{4}\b', re.IGNORECASE),
            
            # Numbers with country codes in various formats (8+ digits only)
            re.compile(r'\+\d{1,3}\s*[67]\d{2}\s*[-.\s]*\d{3}\s*[-.\s]*\d{3}\b', re.IGNORECASE),
            re.compile(r'\+\d{1,3}\s*3\d{2}\s*[-.\s]*\d{3}\s*[-.\s]*\d{4}\b', re.IGNORECASE),
            
            # Numbers with dots as separators (8+ digits only)
            re.compile(r'\b[67]\d{2}\.\d{3}\.\d{3}\b', re.IGNORECASE),
            re.compile(r'\b3\d{2}\.\d{3}\.\d{4}\b', re.IGNORECASE),
            
            # Numbers with hyphens as separators (8+ digits only)
            re.compile(r'\b[67]\d{2}-\d{3}-\d{3}\b', re.IGNORECASE),
            re.compile(r'\b3\d{2}-\d{3}-\d{4}\b', re.IGNORECASE),
            
            # CRITICAL: Numbers with single spaces (most common format that was escaping)
            # Only 8+ digits to avoid censoring prices
            re.compile(r'\b[67]\d{1}\s\d{2}\s\d{2}\s\d{2}\s\d{2}\b', re.IGNORECASE),
            re.compile(r'\b3\d{2}\s\d{3}\s\d{4}\b', re.IGNORECASE),
            
            # Numbers with double or multiple spaces (8+ digits only)
            re.compile(r'\b[67]\d{1}\s{2,}\d{2}\s{2,}\d{2}\s{2,}\d{2}\s{2,}\d{2}\b', re.IGNORECASE),
            re.compile(r'\b3\d{2}\s{2,}\d{3}\s{2,}\d{4}\b', re.IGNORECASE),
            
            # ULTIMATE FALLBACK: Generic patterns for any phone number format (8+ digits only)
            # This catches the remaining edge cases
            re.compile(r'\b[67]\d{1}\s+\d{2}\s+\d{2}\s+\d{2}\s+\d{2}\b', re.IGNORECASE),
            re.compile(r'\b3\d{2}\s+\d{3}\s+\d{4}\b', re.IGNORECASE),
            
            # Final catch-all for Spanish numbers with any spacing (8+ digits only)
            re.compile(r'\b[67]\d{1}\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{2}\b', re.IGNORECASE),
            re.compile(r'\b3\d{2}\s*\d{3}\s*\d{4}\b', re.IGNORECASE),
            
            # SPECIFIC PATTERNS for the escaping formats (8+ digits only)
            # Pattern for "6 12 34 56 78" format (single digit + groups of 2)
            re.compile(r'\b[67]\s\d{2}\s\d{2}\s\d{2}\s\d{2}\b', re.IGNORECASE),
            re.compile(r'\b[67]\s{2,}\d{2}\s{2,}\d{2}\s{2,}\d{2}\s{2,}\d{2}\b', re.IGNORECASE),
            
            # Pattern for "614 25 98 71" format (3-2-2-2 digits)
            re.compile(r'\b[67]\d{2}\s\d{2}\s\d{2}\s\d{2}\b', re.IGNORECASE),
            re.compile(r'\b[67]\d{2}\s{2,}\d{2}\s{2,}\d{2}\s{2,}\d{2}\b', re.IGNORECASE),
            
            # Generic pattern for any 9-digit Spanish number with spaces (ultimate fallback)
            re.compile(r'\b[67]\d{1,3}\s+\d{1,3}\s+\d{1,3}\s+\d{1,3}\b', re.IGNORECASE),
        ]
        
        # Pre-compile other patterns
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.fiscal_code_pattern = re.compile(r'\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b')
        self.vat_pattern = re.compile(r'\b(?!3\d{10})(?!6\d{10})(?!7\d{10})\d{11}\b')
    
    def censor_text(self, text: Optional[str]) -> str:
        """
        High-performance censoring of sensitive data from the given text.
        
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
            censored_text = pattern.sub('[MESSAGING CONTACT CENSORED]', censored_text)
        
        # 2. Censor email addresses
        censored_text = self.email_pattern.sub('[EMAIL CENSORED]', censored_text)
        
        # 3. Censor Italian fiscal codes
        censored_text = self.fiscal_code_pattern.sub('[FISCAL CODE CENSORED]', censored_text)
        
        # 4. Censor VAT numbers (excluding phone numbers)
        censored_text = self.vat_pattern.sub('[VAT NUMBER CENSORED]', censored_text)
        
        # 5. Censor phone numbers (after handling messaging apps)
        for pattern in self.phone_patterns:
            censored_text = pattern.sub('[PHONE NUMBER CENSORED]', censored_text)
        
        return censored_text
    
    def has_sensitive_data(self, text: Optional[str]) -> bool:
        """
        Fast check if the text contains sensitive data that would be censored.
        
        Args:
            text: The text to check
            
        Returns:
            True if sensitive data is found, False otherwise
        """
        if not text:
            return False
        
        # Check all patterns (using pre-compiled patterns for speed)
        all_patterns = (
            self.messaging_patterns + 
            self.phone_patterns + 
            [self.email_pattern, self.fiscal_code_pattern, self.vat_pattern]
        )
        
        for pattern in all_patterns:
            if pattern.search(text):
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
            stats['messaging_contacts'] += len(pattern.findall(text))
        
        # Count phone numbers (excluding those already counted as messaging)
        temp_text = text
        for pattern in self.messaging_patterns:
            temp_text = pattern.sub('', temp_text)
        
        for pattern in self.phone_patterns:
            stats['phone_numbers'] += len(pattern.findall(temp_text))
        
        # Count other types
        stats['emails'] = len(self.email_pattern.findall(text))
        stats['fiscal_codes'] = len(self.fiscal_code_pattern.findall(text))
        stats['vat_numbers'] = len(self.vat_pattern.findall(text))
        
        return stats


# Global instance for easy importing (singleton pattern for performance)
censor = DataCensor()


def censor_sensitive_data(text: Optional[str]) -> str:
    """
    High-performance convenience function to censor sensitive data from text.
    
    Args:
        text: The text to censor
        
    Returns:
        The censored text
    """
    return censor.censor_text(text)


def has_sensitive_data(text: Optional[str]) -> bool:
    """
    Fast convenience function to check if text contains sensitive data.
    
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


# For testing, run: python3 -c "from censorship import censor_sensitive_data; print(censor_sensitive_data('Test: 612345678'))"
