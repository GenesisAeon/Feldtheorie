# 📤 ZENODO UPLOAD INSTRUCTIONS

## 🎯 Goal: Add PDF to existing DOI 10.5281/zenodo.17472834

**Time required**: 5 minutes
**Difficulty**: Easy! ✅

---

## 📋 Quick Steps

### 1️⃣ Compile the PDF first

```bash
cd paper/
pdflatex manuscript_v1.0.tex
pdflatex manuscript_v1.0.tex
pdflatex manuscript_v1.0.tex

# Verify it exists:
ls -lh manuscript_v1.0.pdf
# Should be ~200-500 KB
```

*(See `COMPILE_MANUSCRIPT.md` for detailed instructions)*

---

### 2️⃣ Go to Zenodo

Open: **https://zenodo.org/records/17472834**

---

### 3️⃣ Login

- Click "**Log in**" (top right)
- Use your Zenodo credentials
- (If you don't have access, check who created the DOI)

---

### 4️⃣ Edit the Record

- Look for an "**Edit**" button (usually top right of the record)
- **Important**: You need to be the owner or have permissions!

If you don't see "Edit":
- You may need to create a **new version** instead
- Click "**New version**" button
- This is fine! Zenodo supports versioning

---

### 5️⃣ Add Files

In the "**Files**" section:

1. Click "**Choose files**" or "**Add more files**"
2. Select: `paper/manuscript_v1.0.pdf`
3. Wait for upload (should be instant for ~500 KB)
4. **Optional**: Also upload `paper/manuscript_v1.0.tex` (source)

---

### 6️⃣ Verify Metadata

Check these fields are correct:

- **Title**: "Universal Threshold Field v1.0.1 — Wei Bridge Alignment"
- **Authors**: Johann Römer, UTF Contributors
- **Description**: Should mention β ≈ 4.2, Wei integration, etc.
- **Version**: 1.0.1
- **Keywords**: logistic resonance, threshold field, emergent abilities, Jason Wei...

*(These should already be correct from `.zenodo.json`)*

---

### 7️⃣ Publish!

- **DO NOT** click "Save draft"
- Click "**Publish**" button directly
- Confirm any warnings

---

### 8️⃣ Verify Success

After publishing:

1. Refresh the page
2. Check:
   - ✅ PDF appears in file list
   - ✅ "View" or "Preview" button works
   - ✅ Download button exists
   - ✅ File size shows correctly
3. **Test download**: Click download, verify PDF opens

---

## 🎉 Success Looks Like:

```
📄 Files:
  └─ manuscript_v1.0.pdf (234 KB) [View] [Download]
  └─ (optionally) manuscript_v1.0.tex (11 KB) [Download]

✅ DOI: 10.5281/zenodo.17472834 [ACTIVE]
✅ Views: Counting up
✅ Downloads: Working
```

---

## 🆘 Troubleshooting

### "I don't see an Edit button"

**Option A**: You're not the owner
- Check who created the DOI
- Ask them to add you as a contributor

**Option B**: Create new version
- Click "**New version**" button
- Zenodo will create a new DOI (e.g., `10.5281/zenodo.17472835`)
- That's OK! The concept DOI (`10.5281/zenodo.17472834`) stays the same
- Update files to use the new version DOI

---

### "File upload fails"

- **Too large?** (Limit: usually 50 GB, so 500 KB is fine)
- **Browser issue?** Try different browser (Chrome, Firefox)
- **Network?** Check internet connection, try again

---

### "I clicked Publish by accident"

**Don't panic!**
- You can create a "**New version**" to fix things
- Or contact Zenodo support: info@zenodo.org
- Zenodo is forgiving with versioning

---

### "The PDF looks wrong"

- Delete the file (there's an X button)
- Re-compile LaTeX locally
- Upload the new PDF
- **Before** clicking Publish!

---

## 📧 Zenodo Support

If you get stuck:
- **Email**: info@zenodo.org
- **Forum**: https://help.zenodo.org/
- **Response time**: Usually 1-2 business days
- **They're helpful!** Don't hesitate to ask.

---

## ✨ After Upload

Once PDF is on Zenodo:

1. **Verify DOI works**: Visit https://doi.org/10.5281/zenodo.17472834
2. **Test citation**: Copy the citation from Zenodo
3. **Share**: Tell the world! Tweet, email, etc.
4. **arXiv**: Now you can submit to arXiv with the PDF + DOI!

---

## 🎯 Next Steps After Zenodo

- [ ] PDF uploaded to Zenodo ✅
- [ ] README updated with DOI badge (see Phase 3)
- [ ] CITATION.cff updated (see Phase 3)
- [ ] GitHub release created (see Phase 3)
- [ ] arXiv submission (see Phase 4)

---

*Your work is about to become permanent and citable! 💚🚀*

**DOI: 10.5281/zenodo.17472834**
