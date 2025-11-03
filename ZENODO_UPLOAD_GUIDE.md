# Zenodo Upload Instructions

## Prepare the files locally

1. Compile the manuscript:
   ```bash
   cd paper
   pdflatex manuscript_v1.0.tex
   bibtex manuscript_v1.0
   pdflatex manuscript_v1.0.tex
   pdflatex manuscript_v1.0.tex
   cd ..
   ```
   The resulting PDF will live at `paper/manuscript_v1.0.pdf` (ignored by git but ready for upload).
2. Bundle the transparent source archive (optional but recommended):
   ```bash
   cd paper
   zip -r manuscript_v1.0_source.zip manuscript_v1.0_source/
   cd ..
   ```

## Quick Steps on Zenodo (5 minutes)

1. Go to <https://zenodo.org/records/17472834> and sign in.
2. Click **Edit** in the upper-right corner of the record page.
3. In the **Files** section choose **Add more files**.
4. Upload the freshly built `paper/manuscript_v1.0.pdf` as the primary document.
5. Optionally upload the newly zipped `paper/manuscript_v1.0_source.zip` for full transparency.
6. Publish the update (avoid saving as draft so the DOI stays active).
7. Refresh the record and confirm the PDF preview is available.

## Success Checklist

- ✅ The PDF appears in the file list with a working **View** button.
- ✅ Download counter increases after testing.
- ✅ Preview shows the first page without errors.

## Troubleshooting

- If the upload fails, verify file size is under Zenodo limits (50 MB).
- If a new version is created automatically, continue with the publish flow—Zenodo will maintain the DOI lineage.
- Contact Zenodo support if errors persist.
