"""
TTS Preprocessing - Single-file module
Converts various number patterns in text to words for TTS (English & Hindi).
Import: from num2words_tts import TTSPreprocessor
"""

import re
from typing import Dict, List, Any, Tuple

try:
    from num2words import num2words
    NUM2WORDS_AVAILABLE = True
except ImportError:
    NUM2WORDS_AVAILABLE = False
    def num2words(number, **kwargs):
        return str(number)


# ---------------------------------------------------------------------------
# Pattern Detector
# ---------------------------------------------------------------------------

class PatternDetector:
    """Detects various numeric patterns in text using regex. Priority-based."""

    def __init__(self):
        self.patterns = {
            'EMAIL': {
                'priority': 15,
                'regex': [
                    # Whole email: convert digits inside to words (e.g. sajalmadan09@gmail.com -> sajalmadan zero nine at gmail dot com)
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
                ]
            },
            'DATE': {
                'priority': 10,
                'regex': [
                    # ddMon,yyyy first so it wins over NUMBER matching "2025" (e.g. 13Nov,2025)
                    r'(?i)\b(\d{1,2})\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z.]*\s*,\s*(\d{4})\b',
                    # dd-mm-yyyy or dd/mm/yyyy
                    r'\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})\b',
                    # dd-mm-yy (Indian short year: day-month-year)
                    r'\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2})\b',
                    r'\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b',
                    r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(st|nd|rd|th)?\s+(\d{4})\b',
                    r'\b(\d{1,2})(st|nd|rd|th)\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b',
                    r'[०-९]{1,2}[/-][०-९]{1,2}[/-][०-९]{4}',
                ]
            },
            'DURATION': {
                # Match "X.XX hours" / "1.30 hours" so it's NOT treated as clock time (no AM/PM)
                'priority': 10,
                'regex': [
                    r'\b\d+(?:\.\d+)?\s*(?:hour|hours|hr|hrs)\b',
                ]
            },
            'TIME': {
                'priority': 9,
                'regex': [
                    r'\b(\d{1,2}):(\d{2})\s*(am|pm|AM|PM)?\b',
                    # Do NOT match X.XX when followed by hour/hours (duration, not clock time)
                    r'\b(\d{1,2})\.(\d{2})\s*(am|pm|AM|PM)?(?!\s*(?:hour|hours|hr|hrs)\b)\b',
                    r'[०-९]{1,2}:[०-९]{2}',
                    # Hinglish "N baj kar M min" / "N baj kar Mmin" = N o'clock M minutes (match before "N baj" alone)
                    r'\b(\d{1,2})\s*baj\s+kar\s+(\d{1,2})\s*(?:min|mins|minute|minutes)\b',
                    # Hinglish "N baj" / "Nbaj" = N o'clock (e.g. 5baj = पांच बजे)
                    r'\b(\d{1,2})\s*baj\b',
                ]
            },
            'PHONE': {
                'priority': 8,
                'regex': [
                    r'\+\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{6,10}',
                    r'\(?\d{3,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}',
                    r'\b\d{10}\b',
                ]
            },
            'PINCODE': {
                'priority': 8,
                'regex': [
                    # Indian-style pincodes with explicit label in English or Hindi
                    r'\b(?:PIN\s*code|Pincode|PIN|pin|पिन\s*कोड|पिनकोड)\b[^\d]{0,10}\d{6}\b',
                ]
            },
            'ID': {
                'priority': 8,
                'regex': [
                    # Aadhaar-style IDs
                    r'\b(?:Aadhaar|Aadhar|आधार)\b[^\d]{0,20}[\d\s]{4,}',
                    # OTP / PIN codes (allow small filler like "is", "का", "=")
                    r'\b(?:OTP|ओटीपी|PIN|पिन)\b[^\d]{0,10}\d{3,8}\b',
                ]
            },
            'CURRENCY': {
                'priority': 7,
                'regex': [
                    # Symbol/code before number: $150, Rs 150, ₹150, €90, £50
                    r'(?<![A-Za-z0-9])(?:Rs\.?|₹|\$|USD|EUR|GBP|€|£)\s*[\d,]+(?:\.\d{1,2})?',
                    # Number then word: 150 dollars, 150 rupees
                    r'\b[\d,]+(?:\.\d{1,2})?\s*(?:dollars?|rupees?|euros?|pounds?)\b',
                    # Number then symbol: 150$, 150 ₹, 90€ (suffix; no \b after symbol so end-of-string matches)
                    r'\b[\d,]+(?:\.\d{1,2})?\s*[$₹€](?=\s|$|[.,;!?])',
                    # Number then Rs/rs: 150 rs, 150 Rs
                    r'\b[\d,]+(?:\.\d{1,2})?\s+[Rr]s\.?\b',
                    r'₹\s*[०-९]+(?:[.,][०-९]+)?',
                ]
            },
            'PERCENTAGE': {
                'priority': 6,
                'regex': [
                    r'\b\d+(?:\.\d+)?%',
                    r'\b\d+(?:\.\d+)?\s*percent\b',
                ]
            },
            'RATIO': {
                'priority': 6,
                'regex': [
                    # Ratios like 3:1, 16:9, 2:3:5 (spoken as "three is to one")
                    r'\b\d+(?:\s*:\s*\d+)+\b',
                ]
            },
            'RANGE': {
                'priority': 6,
                'regex': [
                    # Numeric ranges like 125-140 (with optional spaces around hyphen)
                    r'\b\d+(?:\.\d+)?\s*-\s*\d+(?:\.\d+)?\b',
                ]
            },
            'MEASUREMENT': {
                'priority': 6,
                'regex': [
                    r'\b\d+(?:\.\d+)?\s*(?:kg|g|mg|km|m|cm|mm|l|ml|°C|°F|mph|kmph|h|hr|hrs|hour|hours|min|mins|minute|minutes|sec|secs|second|seconds)\b',
                ]
            },
            'ALPHANUMERIC': {
                'priority': 5,
                'regex': [
                    r'\b(?:Room|Section|Gate|Floor|Block|Unit|Flat|Plot)\s+\d+[A-Za-z]?\b',
                ]
            },
            'VEHICLE': {
                'priority': 5,
                'regex': [
                    # Indian vehicle registration: state code (2 letters) + RTO (2 digits) + series (1-2 letters) + number (1-4 digits)
                    r'\b[A-Za-z]{2}\d{2}[A-Za-z]{1,2}\d{1,4}\b',
                ]
            },
            'ALPHANUMERIC_ID': {
                'priority': 4,
                'regex': [
                    # Compact IDs where letters and digits are stuck together, e.g. bfrs12345
                    # Require at least one digit and at least one leading letter.
                    r'\b[A-Za-z]+[A-Za-z0-9]*\d+[A-Za-z0-9]*\b',
                ]
            },
            'DECIMAL': {
                'priority': 4,
                'regex': [
                    r'[०-९]+[.,][०-९]+',
                    r'\b\d+[.,]\d+\b',
                ]
            },
            'ORDINAL': {
                'priority': 3,
                'regex': [
                    r'\b\d+(st|nd|rd|th)\b',
                ]
            },
            'NUMBER': {
                'priority': 1,
                'regex': [
                    r'[०-९]+',
                    r'\b\d{1,3}(?:,\d{3})*\b',
                    r'\b\d+\b',
                ]
            }
        }

    def detect_pattern(self, text: str, pattern_type: str) -> List[Dict]:
        if pattern_type not in self.patterns:
            return []
        matches = []
        pattern_config = self.patterns[pattern_type]
        for regex_pattern in pattern_config['regex']:
            for match in re.finditer(regex_pattern, text, re.IGNORECASE):
                matches.append({
                    'type': pattern_type,
                    'text': match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                    'priority': pattern_config['priority']
                })
        return matches

    def detect_all_patterns(self, text: str) -> List[Dict]:
        all_matches = []
        for pattern_type in self.patterns.keys():
            matches = self.detect_pattern(text, pattern_type)
            all_matches.extend(matches)
        resolved_matches = self._resolve_overlaps(all_matches)
        resolved_matches.sort(key=lambda x: x['start'])
        return resolved_matches

    def _resolve_overlaps(self, matches: List[Dict]) -> List[Dict]:
        if not matches:
            return []
        # Prefer longer spans when start and priority are equal (e.g. "5 baj kar 30 min" over "5 baj")
        matches.sort(key=lambda x: (x['start'], -x['priority'], -(x['end'] - x['start'])))
        resolved = []
        occupied_ranges = []
        for match in matches:
            start, end = match['start'], match['end']
            overlaps = False
            for occ_start, occ_end in occupied_ranges:
                if not (end <= occ_start or start >= occ_end):
                    overlaps = True
                    break
            if not overlaps:
                resolved.append(match)
                occupied_ranges.append((start, end))
        return resolved

    def detect_language(self, text: str) -> str:
        if re.search(r'[\u0900-\u097F]', text):
            return 'hi'
        # Hinglish (Roman script Hindi): common words so time/money output in Hindi
        text_lower = text.lower()
        hinglish_markers = [
            'maine', 'ko', 'par', 'rupaye', 'paise', 'pay', 'kiye', 'kiya',
            'hai', 'baj', 'num', 'ki', 'ka', 'ke', 'me', 'ne', 'se', 'liye', 'bhut',
            'ye', 'mera', 'apna', 'kya', 'bahut'
        ]
        if any(w in text_lower for w in hinglish_markers):
            return 'hi'
        return 'en'


# ---------------------------------------------------------------------------
# Pattern Normalizer
# ---------------------------------------------------------------------------

class PatternNormalizer:
    """Normalizes detected patterns to num2words-compatible format."""

    def __init__(self):
        self.devanagari_to_arabic = {
            '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
            '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
        }
        self.month_names = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        # Abbreviations for formats like 13Nov,2025
        self.month_abbrev = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }

    def normalize(self, text: str, pattern_type: str) -> Dict[str, Any]:
        normalizer_map = {
            'EMAIL': self._normalize_email,
            'DATE': self._normalize_date,
            'TIME': self._normalize_time,
            'PHONE': self._normalize_phone,
            'ID': self._normalize_id,
            'PINCODE': self._normalize_pincode,
            'CURRENCY': self._normalize_currency,
            'PERCENTAGE': self._normalize_percentage,
            'RATIO': self._normalize_ratio,
            'RANGE': self._normalize_range,
            'DURATION': self._normalize_measurement,
            'MEASUREMENT': self._normalize_measurement,
            'ALPHANUMERIC': self._normalize_alphanumeric,
            'VEHICLE': self._normalize_vehicle,
            'ALPHANUMERIC_ID': self._normalize_alphanumeric_id,
            'DECIMAL': self._normalize_decimal,
            'ORDINAL': self._normalize_ordinal,
            'NUMBER': self._normalize_number,
        }
        normalizer_func = normalizer_map.get(pattern_type, self._normalize_number)
        return normalizer_func(text)

    def _devanagari_to_arabic(self, text: str) -> str:
        result = text
        for dev, arab in self.devanagari_to_arabic.items():
            result = result.replace(dev, arab)
        return result

    def _normalize_email(self, text: str) -> Dict[str, Any]:
        """Normalize email: extract parts and identify numbers for conversion."""
        email_text = text.strip()
        # Split email into local part (before @) and domain part (after @)
        if '@' in email_text:
            local_part, domain_part = email_text.split('@', 1)
            return {
                'type': 'email',
                'local_part': local_part,
                'domain_part': domain_part,
                'text': email_text
            }
        return {'type': 'email', 'text': email_text}

    def _normalize_date(self, text: str) -> Dict[str, Any]:
        text = self._devanagari_to_arabic(text)
        match = re.match(r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})', text)
        if match:
            day, month, year = match.groups()
            return {'type': 'date', 'day': int(day), 'month': int(month), 'year': int(year), 'format': 'numeric'}
        # dd-mm-yy (Indian format: day-month-year); 2-digit year -> 20xx for 00-30, 19xx for 31-99
        match = re.match(r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2})', text)
        if match:
            day, month, yy = match.groups()
            yy_int = int(yy)
            full_year = 2000 + yy_int if yy_int <= 30 else 1900 + yy_int
            return {'type': 'date', 'day': int(day), 'month': int(month), 'year': full_year, 'format': 'numeric'}
        match = re.match(r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})', text, re.IGNORECASE)
        if match:
            day, month_name, year = match.groups()
            month = self.month_names[month_name.lower()]
            return {'type': 'date', 'day': int(day), 'month': month, 'year': int(year), 'format': 'text'}
        match = re.match(r'(\d{1,2})(st|nd|rd|th)\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})', text, re.IGNORECASE)
        if match:
            day, suffix, month_name, year = match.groups()
            month = self.month_names[month_name.lower()]
            return {'type': 'date', 'day': int(day), 'month': month, 'year': int(year), 'format': 'ordinal'}
        # Month day(th) year e.g. May 3rd 2022 (output as "May third twenty twenty-two")
        match = re.match(r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(st|nd|rd|th)?\s+(\d{4})', text, re.IGNORECASE)
        if match:
            month_name, day, suffix, year = match.groups()
            month = self.month_names[month_name.lower()]
            return {'type': 'date', 'day': int(day), 'month': month, 'year': int(year), 'format': 'month_day_ordinal' if suffix else 'month_day'}
        # ddMon,yyyy e.g. 13Nov,2025 (year spoken as "twenty twenty-five")
        match = re.match(r'(?i)^(\d{1,2})\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z.]*\s*,\s*(\d{4})$', text.strip())
        if match:
            day, month_abbr, year = match.groups()
            month = self.month_abbrev.get(month_abbr.lower()[:3])
            if month is not None:
                return {'type': 'date', 'day': int(day), 'month': month, 'year': int(year), 'format': 'text'}
        return {'type': 'date', 'text': text}

    def _normalize_time(self, text: str) -> Dict[str, Any]:
        text = self._devanagari_to_arabic(text)
        match = re.match(r'(\d{1,2})[:.](\d{2})\s*(am|pm)?', text, re.IGNORECASE)
        if match:
            hour, minute, meridiem = match.groups()
            return {
                'type': 'time',
                'hour': int(hour),
                'minute': int(minute),
                'meridiem': meridiem
            }
        # Hinglish "5 baj kar 30 min" or "5 baj kar 30min" = 5 o'clock 30 minutes
        match = re.match(r'(?i)(\d{1,2})\s*baj\s+kar\s+(\d{1,2})\s*(?:min|mins|minute|minutes)', text)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            return {'type': 'time', 'hour': hour, 'minute': minute, 'meridiem': None, 'baj': True, 'baj_kar': True}
        # Hinglish "5baj" / "5 baj" = 5 o'clock (no default AM/PM)
        match = re.match(r'(\d{1,2})\s*baj', text, re.IGNORECASE)
        if match:
            hour = int(match.group(1))
            return {'type': 'time', 'hour': hour, 'minute': 0, 'meridiem': None, 'baj': True}
        return {'type': 'time', 'text': text}

    def _normalize_phone(self, text: str) -> Dict[str, Any]:
        digits = re.sub(r'[^\d+]', '', text)
        if digits.startswith('+'):
            country_code = digits[1:3] if len(digits) > 10 else ''
            remaining = digits[3:] if country_code else digits[1:]
        else:
            country_code = ''
            remaining = digits
        # Keep full normalized number; digit-by-digit reading will be handled in converter
        return {
            'type': 'phone',
            'full_number': digits,
            'has_country_code': bool(country_code)
        }

    def _normalize_id(self, text: str) -> Dict[str, Any]:
        # Extract trailing digit sequence and its textual prefix, so we can
        # preserve labels like "Aadhaar number is", "OTP is", "PIN is".
        stripped = text.strip()
        # Split into prefix (non-digit tail) and digit chunk
        m = re.match(r'^(.*?)([\d\s]+)$', stripped)
        if m:
            prefix_text, digit_part = m.groups()
        else:
            prefix_text, digit_part = stripped, ''
        digits = re.sub(r'\D', '', digit_part)
        return {
            'type': 'id',
            'digits': digits,
            'prefix': prefix_text.strip()
        }

    def _normalize_pincode(self, text: str) -> Dict[str, Any]:
        """
        Normalize labeled pincodes like 'PIN code 110001' or 'पिनकोड ११०००१'
        to digit sequences for digit-by-digit reading.
        """
        # Preserve everything up to the first digit as prefix
        stripped = text.strip()
        m = re.match(r'^(.*?)([\d\s०-९]+)$', stripped)
        if m:
            prefix_text, digit_part = m.groups()
        else:
            prefix_text, digit_part = stripped, ''
        # Normalize Devanagari digits to ASCII
        digit_part = self._devanagari_to_arabic(digit_part)
        digits = re.sub(r'\D', '', digit_part)
        return {
            'type': 'pincode',
            'digits': digits,
            'prefix': prefix_text.strip(),
            'text': text,
        }

    def _normalize_ratio(self, text: str) -> Dict[str, Any]:
        """Normalize ratio like '3:1' or '16:9' into list of numbers."""
        text = self._devanagari_to_arabic(text)
        parts = re.split(r'\s*:\s*', text)
        values = []
        for p in parts:
            p = p.strip()
            if p.isdigit():
                values.append(int(p))
            else:
                return {'type': 'ratio', 'text': text}
        return {'type': 'ratio', 'values': values}

    def _normalize_range(self, text: str) -> Dict[str, Any]:
        """
        Normalize numeric ranges like '125-140' into start/end values.
        """
        text = self._devanagari_to_arabic(text)
        m = re.match(r'\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*', text)
        if not m:
            return {'type': 'range', 'text': text}
        start_str, end_str = m.groups()
        start_val = float(start_str)
        end_val = float(end_str)
        return {
            'type': 'range',
            'start': start_val,
            'end': end_val,
        }

    def _normalize_currency(self, text: str) -> Dict[str, Any]:
        text = self._devanagari_to_arabic(text)
        currency_map = {
            '₹': ('rupees', 'paise'), 'rs.': ('rupees', 'paise'), 'rs': ('rupees', 'paise'),
            '$': ('dollars', 'cents'), 'usd': ('dollars', 'cents'), 'eur': ('euros', 'cents'),
            '€': ('euros', 'cents'), 'gbp': ('pounds', 'pence'), '£': ('pounds', 'pence'),
        }
        # Prefer "number + word" (e.g. 50 rupees) so we don't default to dollars
        match = re.match(r'(\d+(?:\.\d+)?)\s*(dollars?|rupees?|euros?|pounds?)', text, re.IGNORECASE)
        if match:
            amount_str, unit = match.groups()
            amount = float(amount_str)
            major = int(amount)
            minor = int((amount - major) * 100)
            unit_map = {'dollar': ('dollars', 'cents'), 'rupee': ('rupees', 'paise'), 'euro': ('euros', 'cents'), 'pound': ('pounds', 'pence')}
            currency = unit_map.get(unit.lower().rstrip('s'), ('dollars', 'cents'))
            indian_rupee = currency == ('rupees', 'paise')
            return {'type': 'currency', 'amount': amount, 'major': major, 'minor': minor, 'currency': currency, 'indian_rupee': indian_rupee}
        currency_symbol = None
        text_lower = text.lower().strip()
        for symbol, names in currency_map.items():
            if symbol in text_lower:
                currency_symbol = names
                break
        # Explicitly detect Rs/₹ so we always use lakh/crore (even if symbol order varies)
        if not currency_symbol and re.search(r'\b(rs\.?|₹|rupees?)\b', text_lower):
            currency_symbol = ('rupees', 'paise')
        amount_match = re.search(r'[\d,]+(?:\.\d+)?', text)
        if amount_match:
            amount_str = amount_match.group(0).replace(',', '')
            amount = float(amount_str)
            major = int(amount)
            minor = int(round((amount - major) * 100))
            indian_rupee = currency_symbol == ('rupees', 'paise')
            return {'type': 'currency', 'amount': amount, 'major': major, 'minor': minor, 'currency': currency_symbol or ('dollars', 'cents'), 'indian_rupee': indian_rupee}
        return {'type': 'currency', 'text': text}

    def _normalize_percentage(self, text: str) -> Dict[str, Any]:
        amount = re.search(r'\d+(?:\.\d+)?', text)
        if amount:
            return {'type': 'percentage', 'value': float(amount.group(0))}
        return {'type': 'percentage', 'text': text}

    def _normalize_measurement(self, text: str) -> Dict[str, Any]:
        match = re.match(r'(\d+(?:\.\d+)?)\s*([a-zA-Z°]+)', text)
        if match:
            value, unit = match.groups()
            return {'type': 'measurement', 'value': float(value), 'unit': unit}
        return {'type': 'measurement', 'text': text}

    def _normalize_vehicle(self, text: str) -> Dict[str, Any]:
        """Normalize vehicle registration (e.g. DL01CA1234) for character/digit reading."""
        return {'type': 'vehicle', 'text': text.strip()}

    def _normalize_alphanumeric(self, text: str) -> Dict[str, Any]:
        match = re.match(r'(\w+)\s+(\d+)([A-Za-z]?)', text)
        if match:
            prefix, number, suffix = match.groups()
            return {'type': 'alphanumeric', 'prefix': prefix, 'number': int(number), 'suffix': suffix}
        return {'type': 'alphanumeric', 'text': text}

    def _normalize_alphanumeric_id(self, text: str) -> Dict[str, Any]:
        """
        Normalize compact alphanumeric IDs like 'bfrs12345' so that letters are kept
        as prefix and digits can be read digit-by-digit by the converter.
        """
        digits = ''.join(ch for ch in text if ch.isdigit())
        prefix = ''.join(ch for ch in text if not ch.isdigit()).strip()
        return {
            'type': 'alphanumeric_id',
            'digits': digits,
            'prefix': prefix,
            'text': text,
        }

    def _normalize_decimal(self, text: str) -> Dict[str, Any]:
        text = self._devanagari_to_arabic(text)
        number_str = text.replace(',', '')
        return {'type': 'decimal', 'value': float(number_str), 'original': text}

    def _normalize_ordinal(self, text: str) -> Dict[str, Any]:
        match = re.match(r'(\d+)(st|nd|rd|th)', text)
        if match:
            number, suffix = match.groups()
            return {'type': 'ordinal', 'value': int(number), 'suffix': suffix}
        return {'type': 'ordinal', 'text': text}

    def _normalize_number(self, text: str) -> Dict[str, Any]:
        text = self._devanagari_to_arabic(text)
        number_str = text.replace(',', '')
        return {'type': 'number', 'value': int(number_str)}


# ---------------------------------------------------------------------------
# Hindi Number Converter (fallback when num2words Hindi is limited)
# ---------------------------------------------------------------------------

class HindiNumberConverter:
    """Simple Hindi number to words converter."""

    def __init__(self):
        self.ones = ['', 'एक', 'दो', 'तीन', 'चार', 'पांच', 'छह', 'सात', 'आठ', 'नौ']
        self.tens = ['', '', 'बीस', 'तीस', 'चालीस', 'पचास', 'साठ', 'सत्तर', 'अस्सी', 'नब्बे']
        self.teens = ['दस', 'ग्यारह', 'बारह', 'तेरह', 'चौदह', 'पंद्रह', 'सोलह', 'सत्रह', 'अठारह', 'उन्नीस']
        self.hundreds = ['', 'एक सौ', 'दो सौ', 'तीन सौ', 'चार सौ', 'पाँच सौ', 'छह सौ', 'सात सौ', 'आठ सौ', 'नौ सौ']
        self.special = {
            21: 'इक्कीस', 22: 'बाईस', 23: 'तेईस', 24: 'चौबीस', 25: 'पच्चीस',
            26: 'छब्बीस', 27: 'सत्ताईस', 28: 'अट्ठाईस', 29: 'उनतीस',
            31: 'इकतीस', 32: 'बत्तीस', 33: 'तैंतीस', 34: 'चौंतीस', 35: 'पैंतीस',
            36: 'छत्तीस', 37: 'सैंतीस', 38: 'अड़तीस', 39: 'उनतालीस',
            41: 'इकतालीस', 42: 'बयालीस', 43: 'तैंतालीस', 44: 'चवालीस', 45: 'पैंतालीस',
            46: 'छियालीस', 47: 'सैंतालीस', 48: 'अड़तालीस', 49: 'उनचास',
            51: 'इक्यावन', 52: 'बावन', 53: 'तिरपन', 54: 'चौवन', 55: 'पचपन',
            56: 'छप्पन', 57: 'सत्तावन', 58: 'अट्ठावन', 59: 'उनसठ',
            61: 'इकसठ', 62: 'बासठ', 63: 'तिरसठ', 64: 'चौंसठ', 65: 'पैंसठ',
            66: 'छियासठ', 67: 'सड़सठ', 68: 'अड़सठ', 69: 'उनहत्तर',
            71: 'इकहत्तर', 72: 'बहत्तर', 73: 'तिहत्तर', 74: 'चौहत्तर', 75: 'पचहत्तर',
            76: 'छिहत्तर', 77: 'सतहत्तर', 78: 'अठहत्तर', 79: 'उनासी',
            81: 'इक्यासी', 82: 'बयासी', 83: 'तिरासी', 84: 'चौरासी', 85: 'पचासी',
            86: 'छियासी', 87: 'सतासी', 88: 'अट्ठासी', 89: 'नवासी',
            91: 'इक्यानवे', 92: 'बानवे', 93: 'तिरानवे', 94: 'चौरानवे', 95: 'पचानवे',
            96: 'छियानवे', 97: 'सत्तानवे', 98: 'अट्ठानवे', 99: 'निन्यानवे'
        }

    def convert(self, number: int) -> str:
        if number == 0:
            return 'शून्य'
        if number < 0:
            return 'ऋण ' + self.convert(abs(number))
        if number < 10:
            return self.ones[number]
        if 10 <= number < 20:
            return self.teens[number - 10]
        if 20 <= number < 100:
            if number in self.special:
                return self.special[number]
            tens_digit = number // 10
            ones_digit = number % 10
            if ones_digit == 0:
                return self.tens[tens_digit]
            return self.special.get(number, self.tens[tens_digit] + ' ' + self.ones[ones_digit])
        if 100 <= number < 1000:
            hundreds_digit = number // 100
            remainder = number % 100
            result = self.hundreds[hundreds_digit]
            if remainder > 0:
                result += ' ' + self.convert(remainder)
            return result
        if 1000 <= number < 100000:
            thousands = number // 1000
            remainder = number % 1000
            result = self.convert(thousands) + ' हज़ार'
            if remainder > 0:
                result += ' ' + self.convert(remainder)
            return result
        if 100000 <= number < 10000000:
            lakhs = number // 100000
            remainder = number % 100000
            result = self.convert(lakhs) + ' लाख'
            if remainder > 0:
                result += ' ' + self.convert(remainder)
            return result
        if 10000000 <= number < 1000000000:
            crores = number // 10000000
            remainder = number % 10000000
            result = self.convert(crores) + ' करोड़'
            if remainder > 0:
                result += ' ' + self.convert(remainder)
            return result
        return ' '.join([self.ones[int(d)] if int(d) < 10 else str(d) for d in str(number)])


# ---------------------------------------------------------------------------
# Num2Words wrapper and converter
# ---------------------------------------------------------------------------

HINDI_CONVERTER = HindiNumberConverter()


def safe_num2words(number, lang='en', **kwargs):
    """Safe wrapper for num2words; uses HindiNumberConverter for Hindi."""
    if lang == 'hi' and HINDI_CONVERTER:
        if isinstance(number, (int, float)):
            if isinstance(number, float) and number != int(number):
                int_part = int(number)
                dec_part = str(number).split('.')[1] if '.' in str(number) else ''
                result = HINDI_CONVERTER.convert(int_part)
                if dec_part:
                    result += ' दशमलव ' + ' '.join([HINDI_CONVERTER.convert(int(d)) for d in dec_part])
                return result
            else:
                return HINDI_CONVERTER.convert(int(number))
        return str(number)
    try:
        return num2words(number, lang=lang, **kwargs)
    except (NotImplementedError, Exception):
        if lang != 'en':
            try:
                return num2words(number, lang='en', **kwargs)
            except Exception:
                return str(number)
        return str(number)


class Num2WordsConverter:
    """Converts normalized patterns to words using num2words (and Hindi fallback)."""

    def __init__(self, default_language: str = 'en'):
        self.default_language = default_language
        self.month_names = {
            'en': ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December'],
            'hi': ['जनवरी', 'फ़रवरी', 'मार्च', 'अप्रैल', 'मई', 'जून',
                   'जुलाई', 'अगस्त', 'सितंबर', 'अक्टूबर', 'नवंबर', 'दिसंबर']
        }

    def convert_to_words(self, normalized_data: Dict[str, Any], pattern_type: str, language: str = None) -> str:
        lang = language or self.default_language
        converter_map = {
            'EMAIL': self._convert_email,
            'DATE': self._convert_date,
            'TIME': self._convert_time,
            'PHONE': self._convert_phone,
            'ID': self._convert_id,
            'PINCODE': self._convert_pincode,
            'CURRENCY': self._convert_currency,
            'PERCENTAGE': self._convert_percentage,
            'RATIO': self._convert_ratio,
            'RANGE': self._convert_range,
            'DURATION': self._convert_measurement,
            'MEASUREMENT': self._convert_measurement,
            'ALPHANUMERIC': self._convert_alphanumeric,
            'VEHICLE': self._convert_vehicle,
            'ALPHANUMERIC_ID': self._convert_alphanumeric_id,
            'DECIMAL': self._convert_decimal,
            'ORDINAL': self._convert_ordinal,
            'NUMBER': self._convert_number,
        }
        converter_func = converter_map.get(pattern_type, self._convert_number)
        return converter_func(normalized_data, lang)

    def _tens_ones_en(self, n: int) -> str:
        """English words for 1-99 without num2words (for year phrasing)."""
        if n < 0 or n > 99:
            return safe_num2words(n, lang='en')
        ones = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
        teens = ['ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen']
        tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
        if n < 10:
            return ones[n]
        if n < 20:
            return teens[n - 10]
        t, o = divmod(n, 10)
        return tens[t] + (' ' + ones[o] if o else '')

    def _year_to_words(self, year: int, lang: str) -> str:
        """Speak 4-digit year naturally: 2022 → 'twenty twenty-two' (not 'two thousand and twenty-two')."""
        if year < 1000 or year > 9999:
            return safe_num2words(year, lang=lang)
        a, b = divmod(year, 100)  # 2022 → 20, 22
        if lang == 'en':
            if year == 2000:
                return "two thousand"
            # Use inline English for 20-99 so year is always "twenty twenty-five" even without num2words
            first = self._tens_ones_en(a)  # 20 → twenty
            if b == 0:
                return first + " hundred"
            if b < 10:
                second = "oh " + self._tens_ones_en(b)
            else:
                second = self._tens_ones_en(b)  # 25 → twenty-five
            return f"{first} {second}"
        # Hindi: 2022 → बीस बाईस; 2001 → बीस शून्य एक
        first_hi = safe_num2words(a, lang=lang)
        if b == 0:
            return first_hi + " सौ"
        second_hi = safe_num2words(b, lang=lang) if b >= 10 else ("शून्य " + safe_num2words(b, lang=lang))
        return f"{first_hi} {second_hi}"

    def _convert_email(self, data: Dict, lang: str) -> str:
        """Convert email: convert numbers to words and special chars for TTS."""
        if 'local_part' in data and 'domain_part' in data:
            local_part = data['local_part']
            domain_part = data['domain_part']
            
            # Convert numbers in local part to words (digit-by-digit)
            # Also convert dots to "dot" for TTS
            local_converted = self._convert_numbers_in_text(local_part, lang)
            local_converted = local_converted.replace('.', ' dot ')
            
            # Convert numbers in domain part to words (digit-by-digit)
            # Also convert dots to "dot" for TTS
            domain_converted = self._convert_numbers_in_text(domain_part, lang)
            domain_converted = domain_converted.replace('.', ' dot ')
            
            # Use "at" instead of "@" for TTS
            return f"{local_converted} at {domain_converted}"
        # Fallback: convert numbers and special chars in the whole email string
        email_text = data.get('text', '')
        converted = self._convert_numbers_in_text(email_text, lang)
        converted = converted.replace('@', ' at ')
        converted = converted.replace('.', ' dot ')
        # Clean up multiple spaces
        import re
        converted = re.sub(r'\s+', ' ', converted).strip()
        return converted
    
    def _convert_numbers_in_text(self, text: str, lang: str) -> str:
        """Helper: convert all digits in a string to words while preserving other characters."""
        result = []
        current_number = ''
        
        for char in text:
            if char.isdigit():
                current_number += char
            else:
                if current_number:
                    # Convert accumulated number to words (digit by digit for multi-digit numbers)
                    # For emails, we want digit-by-digit reading: 09 -> "zero nine"
                    digit_words = []
                    for digit in current_number:
                        digit_words.append(safe_num2words(int(digit), lang=lang))
                    result.append(' '.join(digit_words))
                    current_number = ''
                result.append(char)
        
        # Handle trailing number
        if current_number:
            digit_words = []
            for digit in current_number:
                digit_words.append(safe_num2words(int(digit), lang=lang))
            result.append(' '.join(digit_words))
        
        return ''.join(result)

    def _convert_date(self, data: Dict, lang: str) -> str:
        if 'day' in data and 'month' in data and 'year' in data:
            day, month, year = data['day'], data['month'], data['year']
            month_name = self.month_names[lang][month - 1]
            use_ordinal = data.get('format') in ('ordinal', 'month_day_ordinal')
            if use_ordinal and lang == 'en':
                day_words = safe_num2words(day, lang=lang, to='ordinal')
            elif use_ordinal and lang == 'hi':
                day_words = safe_num2words(day, lang=lang) + " वां"
            elif lang == 'en' and 1 <= day <= 31:
                day_words = self._tens_ones_en(day)  # e.g. 13 → thirteen (no num2words needed)
            else:
                day_words = safe_num2words(day, lang=lang)
            year_words = self._year_to_words(year, lang)
            # Month-first e.g. "May third twenty twenty-two"
            if data.get('format') in ('month_day', 'month_day_ordinal'):
                return f"{month_name} {day_words} {year_words}"
            return f"{day_words} {month_name} {year_words}"
        return data.get('text', '')

    def _convert_time(self, data: Dict, lang: str) -> str:
        if 'hour' in data and 'minute' in data:
            hour, minute = data['hour'], data['minute']
            meridiem = data.get('meridiem')
            from_baj = data.get('baj', False) or data.get('baj_kar', False)  # Hinglish "5baj" / "5 baj kar 30 min" - don't add default AM/PM
            display_hour = hour
            if not meridiem and not from_baj:
                if hour == 0:
                    display_hour, meridiem = 12, 'am'
                elif hour < 12:
                    display_hour, meridiem = hour, 'am'
                elif hour == 12:
                    display_hour, meridiem = 12, 'pm'
                else:
                    display_hour, meridiem = hour - 12, 'pm'
            else:
                display_hour = hour
            hour_words = safe_num2words(display_hour, lang=lang)
            if lang == 'hi':
                if minute == 0:
                    result = f"{hour_words} बजे"
                else:
                    minute_words = safe_num2words(minute, lang=lang)
                    result = f"{hour_words} बजकर {minute_words} मिनट"
                if meridiem:
                    meridiem_hi = "सुबह" if meridiem.lower() == 'am' else "शाम"
                    result = f"{meridiem_hi} {result}"
                return result
            else:
                if minute == 0:
                    result = f"{hour_words} o'clock"
                else:
                    minute_words = safe_num2words(minute, lang=lang)
                    result = f"{hour_words} {minute_words}"
                if meridiem:
                    result = f"{result} {meridiem.upper()}"
                return result
        return data.get('text', '')

    def _convert_phone(self, data: Dict, lang: str) -> str:
        # Read phone/contact numbers digit-by-digit (matches prompt spec for IDs/contact numbers)
        full = data.get('full_number', '')
        if not full:
            return data.get('text', '')
        # Strip leading '+' if present, then speak each remaining digit separately
        number_part = full.lstrip('+')
        digits = [ch for ch in number_part if ch.isdigit()]
        if not digits:
            return data.get('text', '')
        digit_words = [safe_num2words(int(d), lang=lang) for d in digits]
        return ' '.join(digit_words)

    def _convert_id(self, data: Dict, lang: str) -> str:
        digits = data.get('digits', '')
        if not digits:
            return data.get('text', '')
        digit_words = [safe_num2words(int(d), lang=lang) for d in digits]
        prefix = data.get('prefix', '').strip()
        core = ' '.join(digit_words)
        if prefix:
            return f"{prefix} {core}"
        return core

    def _convert_pincode(self, data: Dict, lang: str) -> str:
        """
        Convert pincodes digit-by-digit, preserving any 'PIN code'/'पिनकोड' prefix.
        """
        digits = data.get('digits', '')
        if not digits:
            return data.get('text', '')
        digit_words = [safe_num2words(int(d), lang=lang) for d in digits]
        prefix = data.get('prefix', '').strip()
        core = ' '.join(digit_words)
        if prefix:
            return f"{prefix} {core}"
        return core

    def _convert_ratio(self, data: Dict, lang: str) -> str:
        """Convert ratio like 3:1 to 'three is to one' (EN) or 'तीन है एक' (HI)."""
        values = data.get('values', [])
        if not values:
            return data.get('text', '')
        word_list = [safe_num2words(int(v), lang=lang) for v in values]
        if lang == 'en':
            return ' is to '.join(word_list)
        # Hindi: "तीन है एक" (three is one / three to one)
        return ' है '.join(word_list)

    def _convert_range(self, data: Dict, lang: str) -> str:
        """
        Convert numeric range (start/end) into natural speech:
        - English: 'one hundred and twenty-five to one hundred and forty'
        - Hindi:   'एक सौ पच्चीस से एक सौ चालीस'
        """
        if 'start' not in data or 'end' not in data:
            return data.get('text', '')
        start_val = data['start']
        end_val = data['end']

        def num_words(v):
            if isinstance(v, float) and v != int(v):
                return safe_num2words(v, lang=lang)
            return safe_num2words(int(v), lang=lang)

        start_words = num_words(start_val)
        end_words = num_words(end_val)
        connector = "to" if lang == 'en' else "से"
        return f"{start_words} {connector} {end_words}"

    def _amount_to_words_indian_en(self, n: int) -> str:
        """Convert amount to English words using Indian scale (lakh, crore) for rupees."""
        if n < 0:
            return "minus " + self._amount_to_words_indian_en(-n)
        if n == 0:
            return "zero"
        if n < 1000:
            return self._tens_ones_en(n) if n <= 99 else safe_num2words(n, lang='en')
        if n < 100000:  # 1,000 to 99,999
            thousands = n // 1000
            rest = n % 1000
            th = self._tens_ones_en(thousands) if thousands <= 99 else safe_num2words(thousands, lang='en')
            if rest == 0:
                return th + " thousand"
            return th + " thousand " + self._amount_to_words_indian_en(rest)
        if n < 10000000:  # 1,00,000 to 99,99,999
            lakhs = n // 100000
            rest = n % 100000
            lw = self._tens_ones_en(lakhs) if lakhs <= 99 else safe_num2words(lakhs, lang='en')
            if rest == 0:
                return lw + " lakh"
            return lw + " lakh " + self._amount_to_words_indian_en(rest)
        crores = n // 10000000
        rest = n % 10000000
        if rest == 0:
            return self._amount_to_words_indian_en(crores) + " crore"
        return self._amount_to_words_indian_en(crores) + " crore " + self._amount_to_words_indian_en(rest)

    def _convert_currency(self, data: Dict, lang: str) -> str:
        if 'major' in data and 'currency' in data:
            major, minor = data['major'], data['minor']
            currency_names = data['currency']
            # Indian Rupees: use lakh/crore (never million/thousand for Rs/₹)
            is_rupees = data.get('indian_rupee', False) or (currency_names[0] in ('rupees', 'रुपये'))
            if is_rupees and lang == 'en':
                major_words = self._amount_to_words_indian_en(major)
            else:
                major_words = safe_num2words(major, lang=lang)
            if lang == 'hi':
                currency_unit_map = {'dollars': 'डॉलर', 'rupees': 'रुपये', 'euros': 'यूरो', 'pounds': 'पाउंड'}
                currency_subunit_map = {'cents': 'सेंट', 'paise': 'पैसे', 'pence': 'पेंस'}
                currency_unit = currency_unit_map.get(currency_names[0], currency_names[0])
                currency_subunit = currency_subunit_map.get(currency_names[1], currency_names[1])
            else:
                currency_unit = currency_names[0]
                currency_subunit = currency_names[1]
            result = f"{major_words} {currency_unit}"
            if minor > 0:
                minor_words = safe_num2words(minor, lang=lang)
                connector = "and" if lang == 'en' else "और"
                result += f" {connector} {minor_words} {currency_subunit}"
            return result
        return data.get('text', '')

    def _convert_percentage(self, data: Dict, lang: str) -> str:
        if 'value' in data:
            value = data['value']
            value_words = safe_num2words(value, lang=lang) if isinstance(value, float) and value != int(value) else safe_num2words(int(value), lang=lang)
            percent_word = "percent" if lang == 'en' else "प्रतिशत"
            return f"{value_words} {percent_word}"
        return data.get('text', '')

    def _convert_measurement(self, data: Dict, lang: str) -> str:
        if 'value' in data and 'unit' in data:
            value, unit = data['value'], data['unit']
            value_words = safe_num2words(value, lang=lang) if isinstance(value, float) and value != int(value) else safe_num2words(int(value), lang=lang)
            if lang == 'hi':
                unit_map_hi = {
                    'kg': 'किलोग्राम',
                    'g': 'ग्राम',
                    'm': 'मीटर',
                    'km': 'किलोमीटर',
                    'l': 'लीटर',
                    '°C': 'डिग्री सेल्सियस',
                    '°F': 'डिग्री फारेनहाइट',
                    'hour': 'घंटे',
                    'hours': 'घंटे',
                    'hr': 'घंटे',
                    'hrs': 'घंटे',
                    'h': 'घंटे',
                    'minute': 'मिनट',
                    'minutes': 'मिनट',
                    'min': 'मिनट',
                    'mins': 'मिनट',
                    'second': 'सेकंड',
                    'seconds': 'सेकंड',
                    'sec': 'सेकंड',
                    'secs': 'सेकंड',
                }
                unit = unit_map_hi.get(unit, unit)
            elif lang == 'en':
                unit_map_en = {
                    'kg': 'kilograms',
                    'g': 'grams',
                    'mg': 'milligrams',
                    'm': 'meters',
                    'cm': 'centimeters',
                    'mm': 'millimeters',
                    'km': 'kilometers',
                    'l': 'liters',
                    'ml': 'milliliters',
                    '°C': 'degrees Celsius',
                    '°F': 'degrees Fahrenheit',
                    'hour': 'hours',
                    'hours': 'hours',
                    'hr': 'hours',
                    'hrs': 'hours',
                    'h': 'hours',
                    'minute': 'minutes',
                    'minutes': 'minutes',
                    'min': 'minutes',
                    'mins': 'minutes',
                    'second': 'seconds',
                    'seconds': 'seconds',
                    'sec': 'seconds',
                    'secs': 'seconds',
                }
                unit = unit_map_en.get(unit, unit)
            return f"{value_words} {unit}"
        return data.get('text', '')

    def _convert_vehicle(self, data: Dict, lang: str) -> str:
        """Convert vehicle number to TTS form: letters as-is, digits as words."""
        text = data.get('text', '')
        if not text:
            return ''
        parts = []
        for ch in text:
            if ch.isdigit():
                parts.append(safe_num2words(int(ch), lang=lang))
            else:
                parts.append(ch.upper() if ch.isalpha() else ch)
        return ' '.join(parts)

    def _convert_alphanumeric(self, data: Dict, lang: str) -> str:
        if 'prefix' in data and 'number' in data:
            prefix, number = data['prefix'], data['number']
            suffix = data.get('suffix', '')
            number_words = safe_num2words(number, lang=lang)
            if lang == 'hi':
                prefix_map = {'Room': 'कमरा', 'Floor': 'मंजिल', 'Gate': 'गेट', 'Section': 'सेक्शन', 'Block': 'ब्लॉक'}
                prefix = prefix_map.get(prefix, prefix)
            result = f"{prefix} {number_words}"
            if suffix:
                result += f" {suffix}"
            return result
        return data.get('text', '')

    def _convert_alphanumeric_id(self, data: Dict, lang: str) -> str:
        """
        Convert compact alphanumeric IDs like 'bfrs12345' so that:
        - Prefix letters remain as-is (TTS can usually spell them),
        - Digits are spoken digit-by-digit.
        """
        digits = data.get('digits', '')
        if not digits:
            return data.get('text', '')
        digit_words = [safe_num2words(int(d), lang=lang) for d in digits]
        prefix = data.get('prefix', '').strip()
        core = ' '.join(digit_words)
        if prefix:
            return f"{prefix} {core}"
        return core

    def _convert_decimal(self, data: Dict, lang: str) -> str:
        if 'value' in data:
            value = data['value']
            integer_part = int(value)
            decimal_str = str(value)
            decimal_part = decimal_str.split('.')[1] if '.' in decimal_str else '0'
            integer_words = safe_num2words(integer_part, lang=lang)
            decimal_words = [safe_num2words(int(d), lang=lang) for d in decimal_part]
            point_word = "point" if lang == 'en' else "दशमलव"
            return f"{integer_words} {point_word} {' '.join(decimal_words)}"
        return data.get('text', '')

    def _convert_ordinal(self, data: Dict, lang: str) -> str:
        if 'value' in data:
            value = data['value']
            if lang == 'en':
                return safe_num2words(value, to='ordinal', lang=lang)
            cardinal = safe_num2words(value, lang=lang)
            return f"{cardinal} वां"
        return data.get('text', '')

    def _convert_number(self, data: Dict, lang: str) -> str:
        if 'value' in data:
            return safe_num2words(data['value'], lang=lang)
        return data.get('text', '')


# ---------------------------------------------------------------------------
# TTS Preprocessor (main public API)
# ---------------------------------------------------------------------------

class TTSPreprocessor:
    """
    Main preprocessing hook for TTS systems.
    Detects, normalizes, and converts number patterns to words.
    """

    def __init__(self, default_language: str = 'en'):
        self.detector = PatternDetector()
        self.normalizer = PatternNormalizer()
        self.converter = Num2WordsConverter(default_language=default_language)
        self.default_language = default_language

    def preprocess(self, text: str, language: str = None) -> str:
        if not text or not text.strip():
            return text
        lang = language or self.default_language
        if lang == 'auto':
            lang = self.detector.detect_language(text)
        detected_patterns = self.detector.detect_all_patterns(text)
        if not detected_patterns:
            return text
        detected_patterns.sort(key=lambda x: x['start'], reverse=True)
        processed_text = text
        for pattern in detected_patterns:
            try:
                normalized_data = self.normalizer.normalize(pattern['text'].strip(), pattern['type'])
                words = self.converter.convert_to_words(normalized_data, pattern['type'], lang)
                original_text = pattern['text']
                if original_text.endswith(' '):
                    words = words + ' '
                if original_text.startswith(' '):
                    words = ' ' + words
                start, end = pattern['start'], pattern['end']
                processed_text = processed_text[:start] + words + processed_text[end:]
            except Exception as e:
                continue
        return processed_text

    def preprocess_batch(self, texts: List[str], language: str = None) -> List[str]:
        return [self.preprocess(text, language) for text in texts]

    def get_detected_patterns(self, text: str) -> List[Dict]:
        return self.detector.detect_all_patterns(text)


# Public API
__all__ = [
    'TTSPreprocessor',
    'PatternDetector',
    'PatternNormalizer',
    'Num2WordsConverter',
    'HindiNumberConverter',
    'safe_num2words',
]
