"""
TTS Text Normalization App
Deploy on Streamlit Cloud to convert numbers to words for TTS (English & Hindi)
"""

import streamlit as st
from num2words_tts import TTSPreprocessor

# Page configuration
st.set_page_config(
    page_title="TTS Text Normalization",
    page_icon="🔢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize preprocessor (cached for performance)
@st.cache_resource
def get_preprocessor(language='en'):
    return TTSPreprocessor(default_language=language)

# Title and description
st.title("🔢 TTS Text Normalization")
st.markdown("""
Convert numbers and numeric patterns in text to words for Text-to-Speech systems.
Supports **English** and **Hindi** languages with automatic pattern detection.
""")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    language_mode = st.radio(
        "Language Mode",
        ["English", "Hindi", "Auto-detect"],
        index=0,
        help="Select the target language for conversion"
    )
    
    show_patterns = st.checkbox(
        "Show detected patterns",
        value=False,
        help="Display which patterns were detected in the text"
    )
    
    st.markdown("---")
    st.markdown("### 📝 Sample Examples")
    
    sample_texts = [
        "The meeting is on 12-11-2026 at 2:30pm",
        "Call me at +91-9876543210",
        "The price is ₹500 or $50",
        "Room 123, Floor 5",
        "Today's temperature is 25.5°C",
        "Discount: 25% off on items worth $99.99",
        "He came 1st in the race",
        "My employee id is bfrs02904",
        "My phone number is 9999303854",
        "Down payment is Rs 21000",
        "Weekly EMI is Rs 4500",
        "Range is 125-140 km per full charge",
        "Aadhaar number is 1234 5678 9012",
        "Your OTP is 456789",
        "ATM PIN is 110001",
        "Fast charge takes 1.5 hours",
    ]
    
    for i, sample in enumerate(sample_texts):
        if st.button(f"📌 Example {i+1}", key=f"sample_{i}", use_container_width=True):
            st.session_state.input_text = sample
            # Clear previous output when loading a new example
            if 'normalized_output' in st.session_state:
                st.session_state.normalized_output = ''
            if 'detected_patterns' in st.session_state:
                st.session_state.detected_patterns = []

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 Input Text")
    input_text = st.text_area(
        "Enter text with numbers to normalize:",
        value=st.session_state.get('input_text', ''),
        height=200,
        placeholder="Example: The meeting is on 12-11-2026 at 2:30pm. Call me at +91-9876543210",
        key="input_text_area"
    )
    
    # Convert button
    convert_button = st.button(
        "🔄 Convert to Normalized Text",
        type="primary",
        use_container_width=True,
        help="Click to convert the input text to normalized words"
    )

with col2:
    st.subheader("📤 Normalized Output")
    
    # Initialize session state for output
    if 'normalized_output' not in st.session_state:
        st.session_state.normalized_output = ''
    if 'detected_patterns' not in st.session_state:
        st.session_state.detected_patterns = []
    
    # Process text only when button is clicked
    if convert_button and input_text.strip():
        # Map language mode to code
        lang_map = {
            "English": "en",
            "Hindi": "hi",
            "Auto-detect": "auto"
        }
        lang_code = lang_map[language_mode]
        
        # Get preprocessor
        preprocessor = get_preprocessor(lang_code if lang_code != "auto" else "en")
        
        # Process text
        try:
            normalized_output = preprocessor.preprocess(input_text, language=lang_code)
            st.session_state.normalized_output = normalized_output
            
            # Get detected patterns if enabled
            if show_patterns:
                patterns = preprocessor.get_detected_patterns(input_text)
                st.session_state.detected_patterns = patterns
            else:
                st.session_state.detected_patterns = []
            
        except Exception as e:
            st.error(f"Error processing text: {str(e)}")
            st.exception(e)
            st.session_state.normalized_output = ''
            st.session_state.detected_patterns = []
    
    # Display output if available
    if st.session_state.normalized_output:
        st.text_area(
            "Normalized text:",
            value=st.session_state.normalized_output,
            height=200,
            key="output",
            disabled=False
        )
        
        # Show detected patterns if enabled and available
        if show_patterns and st.session_state.detected_patterns:
            patterns = st.session_state.detected_patterns
            if patterns:
                st.markdown("**Detected Patterns:**")
                pattern_data = []
                for p in patterns:
                    pattern_data.append({
                        "Type": p['type'],
                        "Text": p['text'],
                        "Position": f"{p['start']}-{p['end']}"
                    })
                st.dataframe(pattern_data, use_container_width=True, hide_index=True)
            else:
                st.info("No patterns detected in the input text.")
        
        # Copy functionality (using st.code for easy selection)
        st.markdown("**💡 Tip:** Select the text above and copy it manually, or use the code block below:")
        st.code(st.session_state.normalized_output, language=None)
    elif not input_text.strip():
        st.info("👈 Enter text in the input box and click 'Convert' to see the normalized output here.")
    else:
        st.info("👆 Click the 'Convert to Normalized Text' button to process your input.")

# Additional information
st.markdown("---")
st.markdown("### 📚 Supported Patterns")
st.markdown("""
This tool can normalize the following patterns:

- **Dates**: 12-11-2026, 12/11/2026, January 15th 2024
- **Time**: 2:30pm, 14:30, 5 baj (Hinglish)
- **Phone Numbers**: +91-9876543210, 9999303854
- **Currency**: ₹500, $50, Rs 21000, 150 dollars
- **Percentages**: 25%, 15.5 percent
- **Measurements**: 25.5°C, 125-140 km, 1.5 hours
- **IDs & Codes**: Aadhaar numbers, OTP, PIN codes, Employee IDs
- **Ordinals**: 1st, 2nd, 3rd, 4th
- **Ratios**: 3:1, 16:9
- **Ranges**: 125-140
- **Decimals**: 25.5, 99.99
- **Vehicle Numbers**: DL01CA1234
- **Alphanumeric**: Room 123, Floor 5

**Note**: Email addresses are preserved as-is (numbers inside emails are not converted).
""")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Built with ❤️ using Streamlit | TTS Text Normalization Tool"
    "</div>",
    unsafe_allow_html=True
)

