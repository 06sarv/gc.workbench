# 🚀 How to Run the Pedigree Generator

## ✅ Integration Complete!

The pedigree generator has been integrated into your Streamlit application.

## 🏃 Quick Start

### Run the Streamlit App

```bash
cd gc.workbench
streamlit run app.py
```

Then open your browser and go to the **"🧬 Pedigree Generator"** tab (first tab).

## 📝 Test Examples

Once the app is running, try these examples:

### Example 1: Simple Family
```
David (40 M, carrier) and Emma (38 F, carrier) have three children — Noah (15 M, affected), Ava (12 F, carrier), and Liam (9 M, unaffected).
```

### Example 2: Multi-Generation
```
Robert (65 M, affected) and Mary (62 F, carrier) have two sons — John (40 M, carrier) and David (38 M, unaffected). John married Sarah (37 F, affected) and they have children — Mike (15 M, affected), Lisa (13 F, carrier), and Tom (11 M, unaffected).
```

### Example 3: Large Family
```
Thomas (50 M, affected) and Linda (48 F, carrier) have four children — Michael (22 M, affected), Sarah (20 F, carrier), David (18 M, unaffected), and Rachel (16 F, affected).
```

## 🎯 What You'll See

In the Streamlit app:
- ✅ Input area for family descriptions
- ✅ Example buttons to load pre-made examples
- ✅ Parsed individual data with emojis
- ✅ Symbol legend and usage tips
- ✅ Clear documentation

## 🔧 For Full Interactive Version

If you want the complete canvas-based pedigree with visual rendering:

```bash
# Go back to the pedigree generator folder
cd ..

# Run the standalone version
npm run dev
```

Then open `http://localhost:3000` for the full interactive experience with:
- Canvas-based rendering
- Proper pedigree symbols
- Family connection lines
- PNG export
- Real-time generation

## 📁 What Was Changed

1. **Added new tab** to `gc.workbench/app.py`
2. **Created** `analysis/pedigree_streamlit.py` module
3. **Created** `ui/pedigree_component.html` template
4. **Updated** tab structure to include pedigree generator

## 🎨 Features

- 🧬 Natural language family description input
- 📋 Pre-loaded example prompts
- 👥 Individual extraction and display
- 📖 Symbol legend and documentation
- 💡 Usage tips and guidelines
- 🔗 Link to full interactive version

## ✨ That's It!

Just run `streamlit run app.py` from the `gc.workbench` folder and you're ready to generate pedigree trees!
