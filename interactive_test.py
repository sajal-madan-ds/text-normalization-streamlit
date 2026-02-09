#!/usr/bin/env python3
"""
Interactive terminal tester for num2words_tts.
Run: python interactive_test.py
"""

import sys

try:
    from num2words_tts import TTSPreprocessor
except ImportError:
    print("Error: num2words_tts.py not found. Run from the same directory or add it to PYTHONPATH.")
    sys.exit(1)


def main():
    preprocessor = TTSPreprocessor(default_language='en')

    print("\n" + "=" * 60)
    print("  TTS Preprocessor – Interactive Test")
    print("  (numbers → words for English / Hindi)")
    print("=" * 60)
    print("\nCommands:")
    print("  [text]       – Type any sentence; see English & Hindi output")
    print("  auto [text]  – Auto-detect language and convert")
    print("  d [text]     – Show detected patterns only (debug)")
    print("  lang en|hi   – Set default language for conversion")
    print("  samples      – Run built-in sample sentences (incl. domain cases)")
    print("  help         – Show this help")
    print("  quit / q   – Exit")
    print()

    default_lang = "en"

    while True:
        try:
            line = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not line:
            continue

        # Quit
        if line.lower() in ("quit", "q", "exit"):
            print("Bye.")
            break

        # Help
        if line.lower() == "help":
            print("\nCommands: [text] | auto [text] | d [text] | lang en|hi | samples | help | quit")
            continue

        # Set language
        if line.lower().startswith("lang "):
            part = line[5:].strip().lower()
            if part in ("en", "hi"):
                default_lang = part
                preprocessor = TTSPreprocessor(default_language=part)
                print(f"Default language set to: {part}")
            else:
                print("Use: lang en   or   lang hi")
            continue

        # Debug: show detected patterns only
        if line.lower().startswith("d ") or line.lower() == "d":
            text = line[2:].strip() if line.lower().startswith("d ") else ""
            if not text:
                text = input("Text to analyze: ").strip()
            if not text:
                continue
            patterns = preprocessor.get_detected_patterns(text)
            print(f"Detected {len(patterns)} pattern(s):")
            for p in patterns:
                print(f"  {p['type']:15} | '{p['text']}' at {p['start']}-{p['end']}")
            continue

        # Auto-detect language and convert
        if line.lower().startswith("auto ") or line.lower() == "auto":
            text = line[5:].strip() if line.lower().startswith("auto ") else ""
            if not text:
                text = input("Text to convert (auto language): ").strip()
            if not text:
                continue
            auto = preprocessor.preprocess(text, language="auto")
            print(f"\n  Original: {text}")
            print(f"  Auto:     {auto}")
            print()
            continue

        # Run built-in samples
        if line.lower() == "samples":
            samples = [
                "The meeting is on 12-11-2026 at 2:30pm",
                "Call me at +91-9876543210",
                "The price is ₹500 or $50",
                "Room 123, Floor 5",
                "Today's temperature is 25.5°C",
                "Discount: 25% off on items worth $99.99",
                "He came 1st in the race",
                # Domain-specific / edge cases from prompt context
                "My employee id is bfrs02904",
                "My phone number is 9999303854",
                "Down payment is Rs 21000",
                "Weekly EMI is Rs 4500",
                "Range is 125-140 km per full charge",
                # ID / OTP / Aadhaar style
                "Aadhaar number is 1234 5678 9012",
                "Your OTP is 456789",
                "ATM PIN is 110001",
                # Time measurements
                "Fast charge takes 1.5 hours",
                "Normal charge takes 3 hours",
            ]
            for s in samples:
                en = preprocessor.preprocess(s, language="en")
                hi = preprocessor.preprocess(s, language="hi")
                print(f"\n  Original: {s}")
                print(f"  English:  {en}")
                print(f"  Hindi:    {hi}")
            continue

        # Normal input: treat as text to convert
        text = line
        en = preprocessor.preprocess(text, language="en")
        hi = preprocessor.preprocess(text, language="hi")
        print(f"\n  Original: {text}")
        print(f"  English:  {en}")
        print(f"  Hindi:    {hi}")
        print()


if __name__ == "__main__":
    main()
