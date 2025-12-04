"""
Pedigree Generator Integration for Streamlit
Complete Python implementation with PIL rendering
"""

import streamlit as st
import os
from analysis.pedigree_generator import PedigreeGenerator


def display_pedigree_generator():
    """Display the complete pedigree generator in Streamlit"""
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1.5rem; 
                border-radius: 0.75rem; 
                margin-bottom: 2rem;
                color: white;'>
        <h2 style='margin: 0 0 0.5rem 0; color: white;'>🧬 Pedigree Tree Generator</h2>
        <p style='margin: 0; opacity: 0.9;'>Generate accurate medical pedigree charts from natural language family descriptions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY") or st.session_state.get("gemini_api_key")
    
    # API Key input section
    if not api_key:
        st.warning("⚠️ **Gemini API Key Required**")
        st.info("""
        For enhanced AI-powered parsing, add your Gemini API key. 
        You can get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
        
        The generator will work with simple parsing even without an API key.
        """)
        
        manual_key = st.text_input(
            "Enter your Gemini API Key (optional):",
            type="password",
            key="pedigree_api_key_input",
            help="Leave empty to use simple regex-based parsing"
        )
        if manual_key:
            st.session_state["gemini_api_key"] = manual_key
            st.rerun()
    else:
        st.success("✅ Gemini API configured - AI-enhanced parsing enabled")
        if st.button("Remove API Key", key="remove_api_key"):
            if "gemini_api_key" in st.session_state:
                del st.session_state["gemini_api_key"]
            st.rerun()
    
    st.markdown("""
    ### How to Use
    
    Describe your family tree using one of these formats:
    
    **Format 1 (Compact):**
    ```
    David (40 M, carrier) and Emma (38 F, carrier) have three children — 
    Noah (15 M, affected), Ava (12 F, carrier), and Liam (9 M, unaffected).
    ```
    
    **Format 2 (Traditional):**
    ```
    John is a 45-year-old male with diabetes. He is married to Sarah, 
    a 42-year-old female who is a carrier for color blindness...
    ```
    """)
    
    # Example buttons
    examples = {
        "Simple Family": "David (40 M, carrier) and Emma (38 F, carrier) have three children — Noah (15 M, affected), Ava (12 F, carrier), and Liam (9 M, unaffected).",
        "Multi-Generation": "Robert (65 M, affected) and Mary (62 F, carrier) have two sons — John (40 M, carrier) and David (38 M, unaffected). John married Sarah (37 F, affected) and they have children — Mike (15 M, affected), Lisa (13 F, carrier), and Tom (11 M, unaffected).",
        "Medical Focus": "Thomas (50 M, affected) and Linda (48 F, carrier) have four children — Michael (22 M, affected), Sarah (20 F, carrier), David (18 M, unaffected), and Rachel (16 F, affected)."
    }
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📋 Simple Family", use_container_width=True):
            st.session_state["pedigree_example"] = examples["Simple Family"]
            st.rerun()
    with col2:
        if st.button("📋 Multi-Generation", use_container_width=True):
            st.session_state["pedigree_example"] = examples["Multi-Generation"]
            st.rerun()
    with col3:
        if st.button("📋 Medical Focus", use_container_width=True):
            st.session_state["pedigree_example"] = examples["Medical Focus"]
            st.rerun()
    
    # Input area
    family_description = st.text_area(
        "Family Description:",
        value=st.session_state.get("pedigree_example", ""),
        height=150,
        placeholder="Describe your family tree here...",
        help="Include names, ages, gender (M/F), and status (affected/carrier/unaffected)"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        generate_btn = st.button("🧬 Generate Pedigree Tree", type="primary", use_container_width=True)
    with col2:
        clear_btn = st.button("Clear", use_container_width=True)
    with col3:
        use_ai = st.checkbox("Use AI", value=bool(api_key), disabled=not api_key, 
                            help="Use Gemini AI for enhanced parsing (requires API key)")
    
    if clear_btn:
        if "pedigree_data" in st.session_state:
            del st.session_state["pedigree_data"]
        if "pedigree_image" in st.session_state:
            del st.session_state["pedigree_image"]
        if "pedigree_example" in st.session_state:
            del st.session_state["pedigree_example"]
        st.rerun()
    
    if generate_btn and family_description:
        with st.spinner("🧬 Generating pedigree tree..."):
            try:
                generator = PedigreeGenerator(api_key=api_key)
                pedigree_data = generator.parse_family_description(family_description, use_ai=use_ai and bool(api_key))
                
                if pedigree_data.get("individuals"):
                    # Generate image
                    image = generator.generate_image(pedigree_data)
                    
                    st.session_state["pedigree_data"] = pedigree_data
                    st.session_state["pedigree_image"] = image
                    st.success(f"✅ Generated pedigree with {len(pedigree_data['individuals'])} individuals")
                else:
                    st.error("❌ No individuals found in the description. Please check the format.")
            except Exception as e:
                st.error(f"❌ Error generating pedigree: {str(e)}")
                with st.expander("Error Details"):
                    st.exception(e)
    
    # Display pedigree
    if "pedigree_data" in st.session_state and "pedigree_image" in st.session_state:
        st.markdown("---")
        st.markdown("### Generated Pedigree Tree")
        
        # Display image
        image = st.session_state["pedigree_image"]
        st.image(image, use_container_width=True)
        
        # Download button
        col1, col2 = st.columns([1, 4])
        with col1:
            png_bytes = PedigreeGenerator(api_key=api_key).generate_png_bytes(st.session_state["pedigree_data"])
            st.download_button(
                "📥 Download PNG",
                data=png_bytes,
                file_name="pedigree_tree.png",
                mime="image/png",
                use_container_width=True
            )
        
        # Display data
        with st.expander("📊 View Pedigree Data", expanded=False):
            pedigree_data = st.session_state["pedigree_data"]
            
            st.markdown("#### Individuals")
            for individual in pedigree_data["individuals"]:
                status_emoji = "🔴" if individual["status"] == "affected" else "🟡" if individual["status"] == "carrier" else "⚪"
                gender_emoji = "♂️" if individual["gender"] == "male" else "♀️" if individual["gender"] == "female" else "⚧"
                deceased_mark = " ⚡" if individual.get("deceased") else ""
                st.write(f"{status_emoji} {gender_emoji} **{individual['name']}** - {individual.get('age', '?')}y, {individual['status']}, Gen {individual.get('generation', 0)}{deceased_mark}")
            
            st.markdown("#### Relationships")
            marriages = [r for r in pedigree_data.get("relationships", []) if r["type"] == "marriage"]
            parent_child = [r for r in pedigree_data.get("relationships", []) if r["type"] == "parent-child"]
            
            if marriages:
                st.markdown("**Marriages:**")
                for rel in marriages:
                    st.write(f"💑 {rel['person1']} ↔ {rel['person2']}")
            
            if parent_child:
                st.markdown("**Parent-Child:**")
                for rel in parent_child[:10]:  # Show first 10
                    st.write(f"👨‍👩‍👧 {rel['person1']} → {rel['person2']}")
                if len(parent_child) > 10:
                    st.write(f"... and {len(parent_child) - 10} more")
            
            st.markdown("#### Generations")
            for gen_data in pedigree_data.get("generations", []):
                gen_num = gen_data["generation"]
                individuals = gen_data["individuals"]
                st.write(f"**Generation {gen_num}:** {', '.join([ind['name'] for ind in individuals])}")
            
            with st.expander("📄 Raw JSON", expanded=False):
                st.json(pedigree_data)
    
    # Information sections
    with st.expander("📖 Symbol Legend", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Symbols:**
            - ⬜ Male (square)
            - ⭕ Female (circle)
            - ⬛ Affected (filled)
            - ⚫ Carrier (dot in center)
            - ⚪ Unaffected (empty)
            - ⚡ Deceased (diagonal line)
            """)
        with col2:
            st.markdown("""
            **Status:**
            - 🔴 Affected
            - 🟡 Carrier
            - ⚪ Unaffected
            - ⚡ Deceased
            """)
    
    with st.expander("💡 Tips for Best Results", expanded=False):
        st.markdown("""
        1. **Include ages** for each person
        2. **Specify gender** (M/F or male/female)
        3. **Mention status** (affected/carrier/unaffected)
        4. **Use clear relationships** ("married to", "have children")
        5. **List children** after mentioning parents
        
        ### Common Medical Conditions
        - Diabetes, Heart Disease, Cancer
        - Color Blindness, Hemophilia
        - Sickle Cell Disease, Cystic Fibrosis
        - Alzheimer's, Huntington's Disease
        
        ### Supported Formats
        - `Name (age gender, status)` - e.g., "David (40 M, carrier)"
        - `Name is a X-year-old gender` - e.g., "John is a 45-year-old male"
        - `have children — Name (age gender, status)` - e.g., "have three children — Noah (15 M, affected)"
        """)
    
    st.markdown("""
    ---
    **🔧 Technical Details:**
    - Python-based pedigree generator with PIL/Pillow rendering
    - Supports both simple regex parsing and AI-enhanced parsing (Gemini)
    - Generates high-quality PNG images
    - Follows standard medical genetics pedigree conventions
    """)
