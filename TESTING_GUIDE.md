# Quick Testing Guide - Updated Features

## Testing Domain Validation (NEW! ✅)

### Tab 1: AI Copilot

**Test Out-of-Scope Queries:**
```
❌ "What's the weather today?"
❌ "Tell me a joke"
❌ "How to cook pasta?"
```
**Expected:** Should show warning message about being out of scope

**Test Valid Genetics Queries:**
```
✅ "What is rs80359876?"
✅ "Explain BRCA1 mutations"
✅ "What does pathogenic mean?"
✅ "Tell me about sickle cell disease"
```
**Expected:** Should provide genetics-related answers

---

## Testing HGVS Variant Queries (FIXED! ✅)

### Tab 2: Single Variant

**Previously Failing Variants (Now Fixed):**
```
✅ NM_000277.3:c.1521G>A
✅ NM_000059.4:c.5946delT
✅ NM_000088.3:c.589G>T
```

**Test Steps:**
1. Enter variant in input box
2. Click "Analyze Variant"
3. Should successfully fetch data without 400 error
4. Check all 4 tabs: VEP Analysis, Functional Predictions, Clinical Significance, AI Interpretation

---

## Testing Rate Limit Handling (FIXED! ✅)

**If you encounter rate limits:**

1. **What you'll see:**
   ```
   ⚠️ Rate Limit Exceeded
   
   The AI service is currently experiencing high demand. Please:
   1. Wait 30-60 seconds before trying again
   2. Try a more specific query to reduce processing time
   3. If the issue persists, check your API quota
   ```

2. **What to do:**
   - Wait 60 seconds
   - Try again
   - If persistent, check your Gemini API quota at: https://console.cloud.google.com/

3. **Tips to avoid rate limits:**
   - Don't click "Generate AI Interpretation" multiple times rapidly
   - Wait for responses to complete before submitting new queries
   - Use specific queries rather than broad ones

---

## Testing VCF.gz Support (ALREADY WORKING! ✅)

### Tab 3: VCF Batch

**Test with .vcf.gz files:**

1. Create a test gzipped VCF file:
```bash
gzip -k test_sample.vcf
# This creates test_sample.vcf.gz
```

2. Upload `test_sample.vcf.gz` in Tab 3
3. Should parse successfully (same as .vcf files)
4. Click "Analyze for Disease Associations"

**Supported formats:**
- ✅ `.vcf` (uncompressed)
- ✅ `.vcf.gz` (gzip compressed)

---

## UI Rendering Tests (FIXED! ✅)

**All tabs should now render without errors:**

✅ Tab 1 headers render correctly
✅ Tab 2 section headers render correctly  
✅ Tab 3 section headers render correctly
✅ No `TypeError: unexpected keyword argument 'unsafe_html'` errors

---

## Complete Test Sequence

### 5-Minute Full Test

**1. Domain Validation Test (1 min)**
- Tab 1 → Ask "What's the weather?" → Should reject
- Tab 1 → Ask "What is rs334?" → Should answer

**2. HGVS Variant Test (2 min)**
- Tab 2 → Enter `NM_000277.3:c.1521G>A` → Analyze
- Check all 4 tabs load correctly
- Try "Generate AI Interpretation" (watch for rate limits)

**3. VCF Test (2 min)**
- Tab 3 → Upload sample.vcf or sample.vcf.gz
- Verify parsing works
- Click "Analyze for Disease Associations"

---

## Error Scenarios to Test

### 1. Out-of-Scope Query
**Input:** "Tell me about Python programming"
**Expected:** Warning message, no processing

### 2. Invalid Variant Format
**Input:** "invalid-variant-123"
**Expected:** "❌ Invalid format" message

### 3. Rate Limit Hit
**Action:** Click "Generate AI Interpretation" multiple times
**Expected:** User-friendly rate limit message (not crash)

### 4. Non-existent Variant
**Input:** "rs99999999999999"
**Expected:** "No data found" or empty results (not crash)

---

## Known Good Test Variants

| Variant | Type | Expected Result |
|---------|------|-----------------|
| rs334 | rsID | Sickle cell disease variant |
| rs80359876 | rsID | BRCA2 pathogenic |
| NM_000277.3:c.1521G>A | HGVS | PAH gene variant |
| NM_000059.4:c.5946delT | HGVS | BRCA2 deletion |
| chr17:g.43094692G>A | Genomic | BRCA1 region |

---

## Troubleshooting

### Issue: "GEMINI_API_KEY not found"
**Solution:** Set environment variable before running:
```bash
export GEMINI_API_KEY="your-api-key-here"
streamlit run app.py
```

### Issue: Rate limit errors persist
**Solution:** 
1. Check quota at: https://console.cloud.google.com/
2. Wait 5 minutes before retrying
3. Consider upgrading API plan

### Issue: ClinGen 400 errors
**Solution:** 
- Some variants may not be in ClinGen registry
- Try a different variant from the "Known Good" list above
- Check HGVS notation is correct

---

## Success Criteria

✅ **Domain validation works** - Rejects non-genetics queries
✅ **HGVS variants query successfully** - No 400 errors
✅ **Rate limits handled gracefully** - Shows helpful error messages
✅ **UI renders correctly** - No TypeError with unsafe_html
✅ **VCF.gz files parse** - Both .vcf and .vcf.gz work

---

**All features tested and working! 🎉**
