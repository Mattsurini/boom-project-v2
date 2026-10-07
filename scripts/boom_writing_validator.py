#!/usr/bin/env python3
"""
BooM Writing Style Validator
Validates drafts against BooM writing rules from banned-words.md and boom-writing-style skill.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from pathlib import Path


@dataclass
class ValidationIssue:
    """Single validation issue found in draft."""
    rule_id: str
    severity: str  # "error" | "warning" | "info"
    message: str
    matched_text: str
    position: int
    suggestion: str
    context_allowed: bool = False


@dataclass
class ValidationResult:
    """Complete validation result for a draft."""
    is_valid: bool
    issues: List[ValidationIssue]
    stats: Dict[str, int]
    paragraph_count: int
    avg_paragraph_length: float


class BooMWritingValidator:
    """
    Validates Thai writing against BooM style rules.
    
    Rules source: banned-words.md + boom-writing-style skill
    """
    
    def __init__(self):
        self._init_rules()
    
    def _init_rules(self):
        """Initialize all validation rules."""
        
        # 1. Em dash - always banned
        self.em_dash_pattern = re.compile(r'—')
        
        # 2. Card naming - literal translations banned
        self.card_naming_violations = {
            'Ace of Cups': '1 ถ้วย',
            'Green Ace of Cups': '1 ถ้วย',
            'เอซถ้วย': '1 ถ้วย',
            'Ace of Wands': '1 ไม้',
            'Ace of Swords': '1 ดาบ',
            'Ace of Pentacles': '1 เหรียญ',
            'Ten of Cups': '10 ถ้วย',
            'Ten of Wands': '10 ไม้',
            'Ten of Swords': '10 ดาบ',
            'Ten of Pentacles': '10 เหรียญ',
        }
        
        # 3. Action words - banned → required
        self.action_word_violations = {
            'ขยับ': 'Action',
            'ก้าวหน้า': 'เข้าหา / Action',
            'เริ่มต้น': 'เข้าหา / Action',
            'เปิดทาง': 'ส่งสัญญาณ',
            'เปิดรับ': 'ส่งสัญญาณ',
            'ประตูไม่ได้ปิด': 'เส้นทางไม่ได้ปิด',
            'กำแพง': 'เส้นทางไม่ได้ปิด',
            'ดึงดูดกลับมา': 'ส่งสัญญาณ / เข้าหา',
        }
        
        # 4. Certainty language - banned → required
        self.certainty_violations = {
            'แน่นอน': 'มีแนวโน้ม / อาจจะ',
            'แน่ใจว่า': 'พี่หมอมองว่า / อาจจะ',
            'ไม่มีข้อยกเว้น': 'ขึ้นอยู่กับสถานการณ์',
            'รับประกัน': 'สำหรับบางคน / ในกรณีส่วนใหญ่',
            'รับรอง': 'สำหรับบางคน / ในกรณีส่วนใหญ่',
            'ยืนยัน': 'พี่หมอมองว่า / มีแนวโน้ม',
            'จะต้อง': 'ควร / อาจจะช่วยถ้า',
            'ต้อง(?!การ)': 'ควร / อาจจะ',  # negative lookahead to avoid matching in "ต้องการ"
            'เปลี่ยนชีวิต': 'ช่วยให้... / ทำให้...ง่ายขึ้น',
            'จำเป็นต้อง': 'ควร / อาจจะช่วยถ้า',
        }
        
        # 5. Formal connectors - banned → required
        self.formal_connector_violations = {
            'นอกจากนี้': 'และ / ก็ / จากนั้น',
            'ดังนั้น': 'เพราะฉะนั้น / ดังนั้น (วางแค่จุดเปลี่ยนสำคัญ)',
            'เพราะฉะนั้น': 'เพราะฉะนั้น / ดังนั้น (วางแค่จุดเปลี่ยนสำคัญ)',
            'สรุปได้ว่า': 'สรุปคือ / แปลว่า',
            'จึงสรุปว่า': 'สรุปคือ / แปลว่า',
            'จากการวิเคราะห์': 'วิเคราะห์แล้ว / ดูแล้ว',
            'สะท้อนให้เห็นถึง': 'บอกว่า / สะท้อนว่า',
            'มีความสำคัญ': 'สำคัญ / โดดเด่น',
            'ในขณะที่': 'ในขณะเดียวกัน / แต่',
            'อาทิ': '(ตัดทิ้ง — ให้ตัวอย่างจริงแทน)',
            'เช่น': '(ตัดทิ้ง — ให้ตัวอย่างจริงแทน)',
            'เป็นต้น': '(ตัดทิ้ง — ให้ตัวอย่างจริงแทน)',
        }
        
        # 6. Stock openings - banned → required
        self.opening_violations = {
            'จากที่เห็น': 'ในมุมมุมของพี่หมอ / พี่หมอมองว่า / พี่หมอสัมผัสได้',
            'ตามที่ไพ่บอก': 'ไพ่บอกว่า / ไพ่สะท้อน',
            'สิ่งที่พบคือ': 'สิ่งที่โดดเด่นที่สุดคือ / จุดสำคัญคือ',
            'ขอเริ่มต้นด้วย': '(ตัดทิ้ง เริ่มเนื้อหาเลย)',
        }
        
        # 7. Abstract nouns - context dependent
        self.abstract_nouns = {
            'พลังงาน': ('ความรู้สึก / อารมณ์ / แรงจูงใจ', 'source_cards_allowed'),
            'การเชื่อมต่อ': ('ความสัมพันธ์ / การติดต่อ / ความผูกพัน', 'source_cards_allowed'),
            'โครงสร้าง': ('สถานะ / รูปแบบความสัมพันธ์ / ฐานะ', 'source_cards_allowed'),
            'ฐาน': ('ความเชื่อมั่น / ความเข้าใจ / พื้นฐานความสัมพันธ์', 'source_cards_allowed'),
            'พื้นฐาน': ('ความเชื่อมั่น / ความเข้าใจ / พื้นฐานความสัมพันธ์', 'source_cards_allowed'),
        }
        
        # 8. Metaphors - context dependent
        self.metaphor_violations = {
            'ซ่อมแซม': ('เริ่มใหม่ / กลับมาเป็นคู่ / แก้ไข / ปรับปรุง', 'source_cards: Death/World/10Wands'),
            'ค่อมคืน': ('เริ่มใหม่ / กลับมาเป็นคู่ / แก้ไข / ปรับปรุง', 'source_cards: Death/World/10Wands'),
            'สร้างใหม่': ('เริ่มใหม่ / กลับมาเป็นคู่ / แก้ไข / ปรับปรุง', 'source_cards: Death/World/10Wands'),
            'รักษา': ('เริ่มใหม่ / กลับมาเป็นคู่ / แก้ไข / ปรับปรุง', 'source_cards: Death/World/10Wands'),
            'ปลื้มใจ': ('ไม่ยอมรับได้เลยว่าจบไปแล้ว / ยังคิดถึง', 'source_cards: Lovers/Death'),
            'ไม่มีประตูกลับ': ('เขาไม่ได้เปิดโอกาสให้กลับมา / ไม่ได้ให้โอกาสเราเข้าไปในชีวิตเขา', 'source_cards: Lovers/Death'),
            'ไม่มีช่องว่างให้เขาเข้ามา': ('เขาไม่ได้เปิดโอกาสให้กลับมา / ไม่ได้ให้โอกาสเราเข้าไปในชีวิตเขา', 'source_cards: Lovers/Death'),
            'ดึงดูดเขากลับมา': ('ขอให้เขากลับมา', 'source_cards: Lovers/Death'),
            'ปล่อยให้จบสิ้นสุด': ('ปล่อยให้มันจบสิ้นสุดอย่างสมบูรณ์ รับสถานการณ์ว่าสิ้นสุดไปแล้ว', 'source_cards: Lovers/Death'),
        }
        
        # 9. Signature metaphors - allowed ONLY with source cards
        self.signature_metaphors = {
            'มรสุม': ['Death', 'Tower', '5 Wands'],
            'พายเรือออกจากมรสุม': ['Death', 'Tower', '5 Wands'],
            'กงล้อแห่งโชคชะตา': ['Wheel of Fortune'],
            'อัศวินควบม้า': ['Knight of Swords', '10 Wands', 'Chariot'],
            'ภาระบนหลังม้า': ['Knight of Swords', '10 Wands', 'Chariot'],
            'ประตูแห่งความรัก': ['The Lovers', 'Death'],
            'ท่าเรือพักพิงใจ': ['King of Wands', '6 Cups'],
            'จิ๊กซอว์ชิ้นที่หายไป': ['6 Cups', 'The Lovers'],
            'แสงสว่างวันใหม่': ['The Sun', 'The Star', 'King of Wands'],
            'ปล่อยมือจากภาระ': ['Death', 'The World', '10 Wands'],
            'รีเซ็ตตัวเอง': ['Death', 'The World', '10 Wands'],
            'เส้นทางไม่ได้ปิด': ['Death', 'The Lovers'],
            'แบกภาระ': ['10 Wands', 'Knight of Swords'],
            'แบกหนัก': ['10 Wands', 'Knight of Swords'],
        }
        
        # 10. Timeframe frames - required patterns
        self.timeframe_patterns = [
            r'ช่วง\s*1[–-]\s*3\s*เดือนข้างหน้า',
            r'ประมาณ\s*3\s*เดือน',
            r'ราว\s*10\s*เดือน',
        ]
        self.timeframe_banned = [
            r'ในอีก\s*\d+\s*เดือน',
            r'วันที่\s*\d+',
            r'เดือน\s*(?:มกราคม|กุมภาพันธ์|มีนาคม|เมษายน|พฤษภาคม|มิถุนายน|กรกฎาคม|สิงหาคม|กันยายน|ตุลาคม|พฤศจิกายน|ธันวาคม)',
            r'ปี\s*20\d{2}',
        ]
        
        # 11. Required opening phrases (one must be present)
        self.required_openings = [
            'ในมุมมุมของพี่หมอ',
            'พี่หมอมองว่า',
            'พี่หมอสัมผัสได้',
        ]
        
        # 12. Addressing pronouns - must be consistent
        self.addressing_pronouns = {
            'เรา': 'default_warm',
            'คุณ': 'other_party',
            'ลูกดวง': 'protective_closing',
        }
        
        # 13. Transition headings for multi-heading pieces
        self.transition_headings = [
            'ในขณะเดียวกัน ค่ะ',
            'จุดที่สองคือ ค่ะ',
            'อีกมุมหนึ่ง ค่ะ',
        ]
        
        # 14. ค่ะ placement patterns
        self.ka_placement_patterns = {
            'after_opening': r'(ในมุมมุมของพี่หมอ|พี่หมอมองว่า|พี่หมอสัมผัสได้)\s*ค่ะ',
            'before_pivot': r'(แต่|อย่างไรก็ตาม)\s*ค่ะ',
            'before_action_closing': r'(เข้าหา|ส่งสัญญาณ|ลอง)\s*.*?นะคะ',
            'end_paragraph': r'ค่ะ\s*$',
        }
        
        # 15. Disclaimer pattern for timeframes
        self.disclaimer_pattern = r'ขึ้นอยู่กับ(?:การตัดสินใจ|สถานการณ์|การกระทำของคุณ)'
        
        # Compile all regex patterns
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile all regex patterns for performance."""
        # Regex patterns for more complex matching
        self.compiled_em_dash = re.compile(r'—')
        self.compiled_timeframe_banned = [re.compile(p) for p in self.timeframe_banned]
        self.compiled_timeframe_required = [re.compile(p) for p in self.timeframe_patterns]
        self.compiled_disclaimer = re.compile(self.disclaimer_pattern)
        
        # Keep signature metaphors as compiled regex for context checking
        self.compiled_signature = {re.compile(re.escape(k)): v for k, v in self.signature_metaphors.items()}
        
        # Card reference patterns for context checking
        self.compiled_card_refs = {}
        for card in ['Death', 'The Lovers', 'The World', '10 Wands', '10 Cups', 'The Chariot', 'Knight of Swords', '6 Cups', 'Wheel of Fortune', 'The Sun', 'The Star', 'King of Wands', '5 Wands', 'Tower']:
            self.compiled_card_refs[card] = re.compile(re.escape(card))
        
        # Pre-compile metaphor patterns for context checking
        self.compiled_metaphors = {re.compile(re.escape(k)): v for k, v in self.metaphor_violations.items()}
        self.compiled_abstract = {re.compile(re.escape(k)): v for k, v in self.abstract_nouns.items()}
    
    def validate(self, text: str, source_cards: Optional[List[str]] = None) -> ValidationResult:
        """
        Validate a draft text against BooM writing rules.
        
        Args:
            text: The draft text to validate
            source_cards: List of card names referenced in the text (for context-allowed checks)
        
        Returns:
            ValidationResult with issues and stats
        """
        issues = []
        source_cards = source_cards or []
        
        # Split into paragraphs (by double newline)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Run all validation checks
        issues.extend(self._check_em_dash(text))
        issues.extend(self._check_card_naming(text))
        issues.extend(self._check_action_words(text))
        issues.extend(self._check_certainty_language(text))
        issues.extend(self._check_formal_connectors(text))
        issues.extend(self._check_stock_openings(text, paragraphs))
        issues.extend(self._check_abstract_nouns(text, source_cards))
        issues.extend(self._check_metaphors(text, source_cards))
        issues.extend(self._check_signature_metaphors(text, source_cards))
        issues.extend(self._check_timeframes(text))
        issues.extend(self._check_opening_phrase(text))
        issues.extend(self._check_addressing_consistency(text))
        issues.extend(self._check_paragraph_structure(paragraphs))
        issues.extend(self._check_ka_placement(text))
        issues.extend(self._check_transition_headings(text, paragraphs))
        issues.extend(self._check_disclaimer(text))
        
        # Count stats
        error_count = sum(1 for i in issues if i.severity == 'error')
        warning_count = sum(1 for i in issues if i.severity == 'warning')
        info_count = sum(1 for i in issues if i.severity == 'info')
        
        # Calculate paragraph stats
        para_lengths = [len(p) for p in paragraphs]
        avg_length = sum(para_lengths) / len(para_lengths) if para_lengths else 0
        
        stats = {
            'total_issues': len(issues),
            'errors': error_count,
            'warnings': warning_count,
            'info': info_count,
            'paragraphs': len(paragraphs),
            'total_chars': len(text),
            'avg_paragraph_length': round(avg_length, 1),
        }
        
        return ValidationResult(
            is_valid=(error_count == 0),
            issues=issues,
            stats=stats,
            paragraph_count=len(paragraphs),
            avg_paragraph_length=avg_length,
        )
    
    def _check_em_dash(self, text: str) -> List[ValidationIssue]:
        issues = []
        for match in self.compiled_em_dash.finditer(text):
            issues.append(ValidationIssue(
                rule_id='EM_DASH',
                severity='error',
                message='Em dash (—) ห้ามใช้ — ใช้เว้นวรรคหรือขึ้นบรรทัดใหม่แทน',
                matched_text='—',
                position=match.start(),
                suggestion='แทนที่ด้วยช่องว่างหรือบรรทัดใหม่',
            ))
        return issues
    
    def _check_card_naming(self, text: str) -> List[ValidationIssue]:
        issues = []
        for violation, replacement in self.card_naming_violations.items():
            # Simple substring search (case insensitive)
            pos = 0
            while True:
                pos = text.lower().find(violation.lower(), pos)
                if pos == -1:
                    break
                issues.append(ValidationIssue(
                    rule_id='CARD_NAMING',
                    severity='error',
                    message=f'Card naming ผิด: ใช้ "{replacement}" แทน',
                    matched_text=text[pos:pos+len(violation)],
                    position=pos,
                    suggestion=f'เปลี่ยนเป็น "{replacement}"',
                ))
                pos += 1
        return issues
    
    def _check_action_words(self, text: str) -> List[ValidationIssue]:
        issues = []
        for violation, replacement in self.action_word_violations.items():
            # Simple substring search
            pos = 0
            while True:
                pos = text.find(violation, pos)
                if pos == -1:
                    break
                issues.append(ValidationIssue(
                    rule_id='ACTION_WORDS',
                    severity='error',
                    message=f'Action word ผิด: ใช้ "{replacement}" แทน',
                    matched_text=violation,
                    position=pos,
                    suggestion=f'เปลี่ยนเป็น "{replacement}"',
                ))
                pos += 1
        return issues
    
    def _check_certainty_language(self, text: str) -> List[ValidationIssue]:
        issues = []
        for violation, replacement in self.certainty_violations.items():
            pos = 0
            while True:
                pos = text.find(violation, pos)
                if pos == -1:
                    break
                issues.append(ValidationIssue(
                    rule_id='CERTAINTY',
                    severity='error',
                    message=f'ภาษา over-certain: ใช้ "{replacement}" แทน',
                    matched_text=violation,
                    position=pos,
                    suggestion=f'เปลี่ยนเป็น "{replacement}"',
                ))
                pos += 1
        return issues
    
    def _check_formal_connectors(self, text: str) -> List[ValidationIssue]:
        issues = []
        for violation, replacement in self.formal_connector_violations.items():
            pos = 0
            while True:
                pos = text.find(violation, pos)
                if pos == -1:
                    break
                issues.append(ValidationIssue(
                    rule_id='FORMAL_CONNECTOR',
                    severity='warning',
                    message=f'Formal connector: แนะนำใช้ "{replacement}"',
                    matched_text=violation,
                    position=pos,
                    suggestion=f'พิจารณาเปลี่ยนเป็น "{replacement}"',
                ))
                pos += 1
        return issues
    
    def _check_stock_openings(self, text: str, paragraphs: List[str]) -> List[ValidationIssue]:
        issues = []
        if not paragraphs:
            return issues
        first_para = paragraphs[0]
        for violation, replacement in self.opening_violations.items():
            if violation in first_para:
                pos = first_para.find(violation)
                issues.append(ValidationIssue(
                    rule_id='STOCK_OPENING',
                    severity='error',
                    message=f'Stock opening ห้ามใช้: ใช้ "{replacement}" แทน',
                    matched_text=violation,
                    position=pos,
                    suggestion=f'เปลี่ยนเป็น "{replacement}"',
                ))
        return issues
    
    def _check_abstract_nouns(self, text: str, source_cards: List[str]) -> List[ValidationIssue]:
        issues = []
        has_source_cards = len(source_cards) > 0
        for violation, (replacement, context_note) in self.abstract_nouns.items():
            pos = 0
            while True:
                pos = text.find(violation, pos)
                if pos == -1:
                    break
                context_allowed = has_source_cards and context_note == 'source_cards_allowed'
                issues.append(ValidationIssue(
                    rule_id='ABSTRACT_NOUN',
                    severity='warning' if context_allowed else 'error',
                    message=f'Abstract noun: ใช้ "{replacement}" แทน' + 
                           (f' (allowed กับ source cards: {", ".join(source_cards)})' if context_allowed else ''),
                    matched_text=violation,
                    position=pos,
                    suggestion=f'เปลี่ยนเป็น "{replacement}"' if not context_allowed else 'ตรวจสอบบริบท source cards',
                    context_allowed=context_allowed,
                ))
                pos += 1
        return issues
    
    def _check_metaphors(self, text: str, source_cards: List[str]) -> List[ValidationIssue]:
        issues = []
        has_source_cards = len(source_cards) > 0
        for violation, (replacement, context_note) in self.metaphor_violations.items():
            pos = 0
            while True:
                pos = text.find(violation, pos)
                if pos == -1:
                    break
                context_allowed = has_source_cards and context_note.startswith('source_cards:')
                allowed_cards = context_note.replace('source_cards:', '').split('/') if context_allowed else []
                issues.append(ValidationIssue(
                    rule_id='METAPHOR',
                    severity='warning' if context_allowed else 'error',
                    message=f'Metaphor ห้ามใช้ generic: ใช้ "{replacement}" แทน' +
                           (f' (allowed กับ source cards: {", ".join(allowed_cards)})' if context_allowed else ''),
                    matched_text=violation,
                    position=pos,
                    suggestion=f'เปลี่ยนเป็น "{replacement}"' if not context_allowed else 'ตรวจสอบบริบท source cards',
                    context_allowed=context_allowed,
                ))
                pos += 1
        return issues
    
    def _check_signature_metaphors(self, text: str, source_cards: List[str]) -> List[ValidationIssue]:
        issues = []
        for metaphor, allowed_cards in self.signature_metaphors.items():
            pos = 0
            while True:
                pos = text.find(metaphor, pos)
                if pos == -1:
                    break
                # Check if any allowed card is mentioned nearby (200 chars window)
                context_window = text[max(0, pos-200):pos+200]
                card_mentioned = any(card in context_window for card in allowed_cards)
                if not card_mentioned:
                    issues.append(ValidationIssue(
                        rule_id='SIGNATURE_METAPHOR_CONTEXT',
                        severity='warning',
                        message=f'Signature metaphor "{metaphor}" ต้องใช้กับ source cards: {", ".join(allowed_cards)}',
                        matched_text=metaphor,
                        position=pos,
                        suggestion=f'เพิ่ม reference ไปยัง source cards: {", ".join(allowed_cards)}',
                    ))
                pos += 1
        return issues
    
    def _check_timeframes(self, text: str) -> List[ValidationIssue]:
        issues = []
        
        # Check banned timeframe patterns
        for pattern in self.compiled_timeframe_banned:
            for match in pattern.finditer(text):
                issues.append(ValidationIssue(
                    rule_id='TIMEFRAME_BANNED',
                    severity='error',
                    message='Timeframe แบบแน่ชัดห้ามใช้: ใช้ trend window แทน',
                    matched_text=match.group(),
                    position=match.start(),
                    suggestion='ใช้: "ช่วง 1–3 เดือนข้างหน้า" / "ประมาณ 3 เดือน" / "ราว 10 เดือน"',
                ))
        
        # Check if any timeframe exists but no required pattern found
        has_timeframe = any(p.search(text) for p in self.compiled_timeframe_required)
        if has_timeframe:
            # Verify required pattern is used
            if not any(p.search(text) for p in self.compiled_timeframe_required):
                issues.append(ValidationIssue(
                    rule_id='TIMEFRAME_FORMAT',
                    severity='warning',
                    message='Timeframe ควรใช้ frames มาตรฐาน',
                    matched_text='',
                    position=0,
                    suggestion='ใช้: "ช่วง 1–3 เดือนข้างหน้า" / "ประมาณ 3 เดือน" / "ราว 10 เดือน"',
                ))
        
        return issues
    
    def _check_opening_phrase(self, text: str) -> List[ValidationIssue]:
        issues = []
        has_required_opening = any(opening in text for opening in self.required_openings)
        if not has_required_opening:
            issues.append(ValidationIssue(
                rule_id='MISSING_OPENING',
                severity='error',
                message='ขาด opening phrase ที่จำเป็น',
                matched_text='',
                position=0,
                suggestion='เพิ่มหนึ่งใน: "ในมุมมุมของพี่หมอ" / "พี่หมอมองว่า" / "พี่หมอสัมผัสได้"',
            ))
        return issues
    
    def _check_addressing_consistency(self, text: str) -> List[ValidationIssue]:
            issues = []
        
            # Check for addressing pronouns, but exclude "ของคุณ" (possessive for client)
            # "คุณ" in "ของคุณ" refers to the client, not the other party
            found_pronouns = []
        
            if 'เรา' in text:
                found_pronouns.append('เรา')
        
            # Check for "คุณ" but exclude "ของคุณ"
            # "คุณ" alone = other party, "ของคุณ" = client's possession
            if 'คุณ' in text:
                # Count "คุณ" not preceded by "ของ"
                pattern = re.compile(r'(?<!ของ)คุณ')
                if pattern.search(text):
                    found_pronouns.append('คุณ')
        
            if 'ลูกดวง' in text:
                found_pronouns.append('ลูกดวง')
        
            if len(found_pronouns) > 1:
                issues.append(ValidationIssue(
                    rule_id='ADDRESSING_INCONSISTENT',
                    severity='warning',
                    message=f'Addressing pronouns สลับกัน: {", ".join(found_pronouns)} — ควรเลือก 1 ตัวต่อ reading',
                    matched_text=', '.join(found_pronouns),
                    position=0,
                    suggestion='เลือก: "เรา" (default warm) หรือ "คุณ" (other party) หรือ "ลูกดวง" (protective closing)',
                ))
            return issues
    
    def _check_paragraph_structure(self, paragraphs: List[str]) -> List[ValidationIssue]:
        issues = []
        for i, para in enumerate(paragraphs):
            if len(para) < 300:
                issues.append(ValidationIssue(
                    rule_id='PARAGRAPH_TOO_SHORT',
                    severity='error',
                    message=f'Paragraph {i+1} สั้นเกินไป: {len(para)} chars (< 300)',
                    matched_text=para[:100] + '...' if len(para) > 100 else para,
                    position=0,
                    suggestion='ขยายเป็น ≥300 chars (target 400-800+ chars)',
                ))
        return issues
    
    def _check_ka_placement(self, text: str) -> List[ValidationIssue]:
        issues = []
        
        # Check for "ค่ะ" after comma (banned)
        ka_after_comma = re.search(r'[^,]{0,50},\s*ค่ะ', text)
        if ka_after_comma:
            issues.append(ValidationIssue(
                rule_id='KA_AFTER_COMMA',
                severity='error',
                message='ห้ามวาง "ค่ะ" หลัง comma',
                matched_text=ka_after_comma.group(),
                position=ka_after_comma.start(),
                suggestion='ย้าย "ค่ะ" ไป: ปิดประโยค / ก่อน pivot / ก่อน action closing',
            ))
        
        # Check each "ค่ะ" position for valid placement
        ka_positions = [m.start() for m in re.finditer(r'ค่ะ', text)]
        for pos in ka_positions:
            # Get context around ค่ะ (150 chars before and after)
            before = text[max(0, pos-150):pos]
            after = text[pos:pos+150]
            context = before + 'ค่ะ' + after
            
            # Check if it's in a valid position
            valid_position = False
            
            # 1. After opening phrase: "ในมุมมุมของพี่หมอ ค่ะ" / "พี่หมอมองว่า ค่ะ" / "พี่หมอสัมผัสได้ ค่ะ"
            if re.search(r'(ในมุมมุมของพี่หมอ|พี่หมอมองว่า|พี่หมอสัมผัสได้)\s*ค่ะ', context):
                valid_position = True
            
            # 2. Before pivot connector: "ค่ะ แต่" / "ค่ะ อย่างไรก็ตาม"
            elif re.search(r'ค่ะ\s*(แต่|อย่างไรก็ตาม)', context):
                valid_position = True
            
            # 3. Before action closing: "ค่ะ" followed by action words in the same sentence
            # Pattern: "ค่ะ" then optional words, then action words (เข้าหา/ส่งสัญญาณ/ลอง/หาก)
            elif re.search(r'ค่ะ\s*(?:หาก|ถ้า)?\s*(เข้าหา|ส่งสัญญาณ|ลอง)', context):
                valid_position = True
            
            # 4. At end of paragraph/sentence: "ค่ะ." / "ค่ะ\n" / "ค่ะ$"
            elif re.search(r'ค่ะ\s*[\.\n]|ค่ะ\s*$', context):
                valid_position = True
            
            # 5. Before disclaimer/timeframe: "ค่ะ ขึ้นอยู่กับ" / "ค่ะ ในช่วง"
            elif re.search(r'ค่ะ\s*(ขึ้นอยู่กับ|ในช่วง|ประมาณ|ราว)', context):
                valid_position = True
            
            # 6. After transition heading: "ในขณะเดียวกัน ค่ะ" / "จุดที่สองคือ ค่ะ" / "อีกมุมหนึ่ง ค่ะ"
            elif re.search(r'(ในขณะเดียวกัน|จุดที่สองคือ|อีกมุมหนึ่ง)\s*ค่ะ', context):
                valid_position = True
            
            # 7. Before consequence/result: "ค่ะ สิ่งนี้" / "ค่ะ การที่" / "ค่ะ จุดนี้"
            elif re.search(r'ค่ะ\s*(สิ่งนี้|การที่|จุดนี้)', context):
                valid_position = True
            
            if not valid_position and pos > 0:
                # Check if it's mid-sentence (has Thai text before and after, not at boundary)
                if re.search(r'[ก-๙]', before[-20:]) and re.search(r'[ก-๙]', after[:20]):
                    issues.append(ValidationIssue(
                        rule_id='KA_MID_CLAUSE',
                        severity='warning',
                        message='ค่ะ อยู่กลาง clause — ควรอยู่: หลัง opening / ก่อน pivot / ก่อน action closing / ปิดย่อหน้า / ก่อน disclaimer / หลัง transition / ก่อน consequence',
                        matched_text='ค่ะ',
                        position=pos,
                        suggestion='ย้าย "ค่ะ" ไปตำแหน่งที่เหมาะสม',
                    ))
        return issues
    
    def _check_transition_headings(self, text: str, paragraphs: List[str]) -> List[ValidationIssue]:
        issues = []
        if len(paragraphs) <= 1:
            return issues
        
        # Check paragraphs 2+ for transition headings
        for i, para in enumerate(paragraphs[1:], 2):
            first_line = para.split('\n')[0].strip()
            has_transition = any(t in first_line for t in self.transition_headings)
            has_main_opening = any(op in first_line for op in self.required_openings)
            
            if has_main_opening:
                issues.append(ValidationIssue(
                    rule_id='DUPLICATE_OPENING',
                    severity='warning',
                    message=f'Paragraph {i} ใช้ main opening phrase ซ้ำ — ควรใช้ transition heading',
                    matched_text=first_line[:100],
                    position=0,
                    suggestion=f'ใช้: {", ".join(self.transition_headings)}',
                ))
            elif not has_transition and len(first_line) > 0:
                issues.append(ValidationIssue(
                    rule_id='MISSING_TRANSITION',
                    severity='info',
                    message=f'Paragraph {i} ควรมี transition heading',
                    matched_text=first_line[:100],
                    position=0,
                    suggestion=f'พิจารณาเพิ่ม: {", ".join(self.transition_headings)}',
                ))
        return issues
    
    def _check_disclaimer(self, text: str) -> List[ValidationIssue]:
        issues = []
        has_timeframe = any(p.search(text) for p in self.compiled_timeframe_required)
        has_disclaimer = self.compiled_disclaimer.search(text) is not None
        
        if has_timeframe and not has_disclaimer:
            issues.append(ValidationIssue(
                rule_id='MISSING_DISCLAIMER',
                severity='error',
                message='มี timeframe แต่ขาด disclaimer',
                matched_text='',
                position=0,
                suggestion='เพิ่ม: "ขึ้นอยู่กับการตัดสินใจ/สถานการณ์/การกระทำของคุณ"',
            ))
        return issues
    
    def format_report(self, result: ValidationResult) -> str:
        """Format validation result as human-readable report."""
        lines = []
        lines.append("=" * 60)
        lines.append("BooM Writing Style Validation Report")
        lines.append("=" * 60)
        lines.append(f"Status: {'✅ PASS' if result.is_valid else '❌ FAIL'}")
        lines.append(f"Paragraphs: {result.paragraph_count}")
        lines.append(f"Avg paragraph length: {result.avg_paragraph_length:.0f} chars")
        lines.append(f"Total chars: {result.stats['total_chars']:,}")
        lines.append(f"Issues: {result.stats['total_issues']} (Errors: {result.stats['errors']}, Warnings: {result.stats['warnings']}, Info: {result.stats['info']})")
        lines.append("")
        
        if result.issues:
            # Group by severity
            for severity in ['error', 'warning', 'info']:
                sev_issues = [i for i in result.issues if i.severity == severity]
                if not sev_issues:
                    continue
                lines.append(f"--- {severity.upper()} ({len(sev_issues)}) ---")
                for issue in sev_issues:
                    ctx = " [context-allowed]" if issue.context_allowed else ""
                    lines.append(f"  [{issue.rule_id}] {issue.message}{ctx}")
                    lines.append(f"    Found: '{issue.matched_text}' at pos {issue.position}")
                    lines.append(f"    Fix: {issue.suggestion}")
                    lines.append("")
        
        return "\n".join(lines)


def validate_file(filepath: str, source_cards: Optional[List[str]] = None) -> ValidationResult:
    """Convenience function to validate a file."""
    text = Path(filepath).read_text(encoding='utf-8')
    validator = BooMWritingValidator()
    return validator.validate(text, source_cards)


def validate_text(text: str, source_cards: Optional[List[str]] = None) -> ValidationResult:
    """Convenience function to validate text directly."""
    validator = BooMWritingValidator()
    return validator.validate(text, source_cards)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python boom_writing_validator.py <file_or_text> [source_cards...]")
        print("Example: python boom_writing_validator.py draft.md 'Death' '10 Wands'")
        sys.exit(1)
    
    input_arg = sys.argv[1]
    source_cards = sys.argv[2:] if len(sys.argv) > 2 else None
    
    if Path(input_arg).exists():
        result = validate_file(input_arg, source_cards)
    else:
        result = validate_text(input_arg, source_cards)
    
    validator = BooMWritingValidator()
    print(validator.format_report(result))
    
    sys.exit(0 if result.is_valid else 1)