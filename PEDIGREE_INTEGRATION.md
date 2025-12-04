# 🧬 Pedigree Tree Generator Integration

## Overview
The Pedigree Tree Generator has been integrated into the Genetic Variant Analyzer Streamlit application as a new tab.

## What Was Added

### 1. New Tab in Main Application
- **Tab Name:** "🧬 Pedigree Generator"
- **Location:** First tab in the application
- **Purpose:** Generate medical pedigree charts from natural language descriptions

### 2. Files Created

#### `analysis/pedigree_streamlit.py`
- Main Streamlit integration module
- Handles UI and user interaction
- Provides example prompts and documentation
- Basic parsing demonstration

#### `ui/pedigree_component.html`
- HTML template for full interactive version
- Placeholder for canvas-based rendering

### 3. Features

#### Current Features (Streamlit Version)
- ✅ Natural language input for family descriptions
- ✅ Example prompts (Simple, Multi-Generation, Medical Focus)
- ✅ Basic individual extraction and display
- ✅ Symbol legend and documentation
- ✅ Tips and usage guidelines

#### Full Features (Standalone Version)
- ✅ Interactive canvas-based pedigree rendering
- ✅ Proper medical genetics symbols (squares, circles, filled, carriers)
- ✅ Family relationship lines (marriage, parent-child)
- ✅ Multi-generation support
- ✅ PNG export functionality
- ✅ Gemini AI-enhanced parsing
- ✅ Real-time generation

## How to Use

### In Streamlit App

1. **Start the Streamlit app:**
   ```bash
   cd gc.workbench
   streamlit run app.py
   ```

2. **Navigate to the "🧬 Pedigree Generator" tab**

3. **Enter a family description** using one of these formats:

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

4. **Click "Generate Pedigree Tree"**

### Standalone Full Version

For the complete interactive experience with canvas rendering:

1. **Navigate to the pedigree generator folder:**
   ```bash
   cd ..  # Go back to parent directory
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open in browser:**
   ```
   http://localhost:3000
   ```

## Supported Formats

### Individual Format
```
Name (age gender, status)
```

**Examples:**
- `David (40 M, carrier)`
- `Emma (38 F, affected)`
- `Noah (15 M, unaffected)`

### Gender Options
- `M` or `male` = Male (square symbol)
- `F` or `female` = Female (circle symbol)

### Status Options
- `affected` = Has the condition (filled symbol)
- `carrier` = Carries gene (dot in center)
- `unaffected` = Normal (empty symbol)
- `deceased` = Deceased (diagonal line)

### Relationship Keywords
- Marriage: "married to", "and" (between spouses)
- Children: "have children", "have three children —"
- Family: "son", "daughter", "twins"

## Example Prompts

### Simple Nuclear Family
```
Alex (30 M, affected) and Beth (28 F, carrier) have children — 
Chris (5 M, unaffected) and Dana (3 F, carrier).
```

### Multi-Generation Family
```
Robert (65 M, affected) and Mary (62 F, carrier) have two sons — 
John (40 M, carrier) and David (38 M, unaffected). John married 
Sarah (37 F, affected) and they have children — Mike (15 M, affected), 
Lisa (13 F, carrier), and Tom (11 M, unaffected).
```

### Medical Conditions Focus
```
Thomas (50 M, affected) and Linda (48 F, carrier) have four children — 
Michael (22 M, affected), Sarah (20 F, carrier), David (18 M, unaffected), 
and Rachel (16 F, affected).
```

## Symbol Legend

| Symbol | Meaning |
|--------|---------|
| ⬜ | Male (square) |
| ⭕ | Female (circle) |
| ⬛ | Affected (filled) |
| ⚫ | Carrier (dot in center) |
| ⚪ | Unaffected (empty) |
| ⚡ | Deceased (diagonal line) |

## Technical Details

### Architecture
- **Frontend:** HTML/CSS/JavaScript with Fabric.js for canvas rendering
- **Backend:** Python/Streamlit for integration
- **AI:** Google Gemini API for enhanced parsing (optional)
- **Parsing:** Regex-based fallback parser + AI-enhanced parser

### Dependencies
- Fabric.js 5.3.0 (canvas manipulation)
- Streamlit (Python web framework)
- Google Gemini API (optional, for better accuracy)

### File Structure
```
gc.workbench/
├── analysis/
│   ├── pedigree_streamlit.py    # Streamlit integration
│   └── pedigree_generator.py    # (optional) Full Python version
├── ui/
│   └── pedigree_component.html  # HTML template
└── app.py                        # Main Streamlit app (updated)

../  (parent directory)
├── js/
│   ├── simplePedigreeParser.js  # Parser logic
│   ├── pedigreeRenderer.js      # Canvas rendering
│   └── main.js                   # Main app logic
├── styles/
│   └── main.css                  # Styling
└── index.html                    # Standalone version
```

## Future Enhancements

### Planned Features
- [ ] Full canvas rendering in Streamlit using components.html
- [ ] Direct Gemini API integration in Streamlit version
- [ ] Database storage for generated pedigrees
- [ ] PDF export functionality
- [ ] Annotation and notes on individuals
- [ ] Disease-specific color coding
- [ ] Consanguinity indicators
- [ ] Multiple condition tracking per individual

### Integration Opportunities
- Link pedigree data with variant analysis
- Auto-populate from VCF file family information
- Export pedigree data to genetic analysis tools
- Integration with clinical databases

## Troubleshooting

### Issue: Pedigree not generating
**Solution:** Check that the format matches the expected pattern with age, gender, and status

### Issue: Individuals not found
**Solution:** Ensure each person is described as: `Name (age gender, status)`

### Issue: Relationships not showing
**Solution:** Use clear relationship keywords like "married to" and "have children"

### Issue: API key errors
**Solution:** Add Gemini API key to `.env` file or enter manually in the UI

## Support

For issues or questions:
1. Check the example prompts in the UI
2. Review the symbol legend and tips
3. Try the standalone version for full functionality
4. Refer to the main README.md for general setup

## Credits

- Pedigree generation logic based on medical genetics standards
- Symbol conventions follow standard pedigree chart guidelines
- AI parsing powered by Google Gemini API
- Canvas rendering using Fabric.js library
