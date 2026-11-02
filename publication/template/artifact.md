# IEEE Access template execution contract

Reference: Access-Template-2024.docx, downloaded from the official IEEE Access submission page on 1 November 2026. Retain the reference unchanged. Its SHA-256 is recorded in the final manifest.

Reference rendering: review/template-render, eight pages exported with Microsoft Word after the packaged renderer failed because LibreOffice is absent. The reference has nine sections: a full-width title/abstract block and repeated continuous two-column sections. Repeated sections are sample-content artifacts and may be replaced by a single continuous body section.

Page system: 8 x 10.875 inches; left/right margins 740 twips; first top margin 1280 twips and body top 1300 twips; bottom 1040 twips; header 360 twips; footer 640 twips. Body has two equal columns with a 400-twip gap. Keep this geometry. Single-column title and abstract precede the two-column main text.

Typography: use source Paper Title (22 pt Helvetica), AU (10 pt Helvetica), PI (7.5 pt), Abstract (10 pt), IT (10 pt), PARA (10 pt), H1/H2 source roles (9 pt Helvetica), Fig Caption and Table Caption (7 pt Helvetica), and Ref (7.5 pt). Template headings and title may be made black to follow document skill requirements. Native Word equations replace the example equation. Automatic sample numbering is removed in generated paragraphs and explicit Roman section numbers are used to avoid inherited sequence artifacts.

Slots: replace all example body paragraphs, sample tables, images, references, and author biographies. Omit fictitious publication date, DOI, volume, support footnote, author honors, and biographies unsupported by author evidence. Preserve styles, numbering definitions, theme, and page geometry. Header text may be replaced by the actual short title and author surname; footer must use an actual PAGE field without fictitious volume metadata. Sample header branding may be retained. These are editable boilerplate slots, not scientific content.

Tables: fit the 3.35-inch body column with explicit widths, compact numerical cells, captions above, no fixed row heights, repeat header row, light gray borders. Figures: actual 600 dpi PNG with SVG/PDF companions, inserted inline at column width and captioned below. Keep image and caption together.

Source data: original author names/order, affiliation, corresponding author/email are immutable scientific identity slots. Full tables and methodological detail may flow over additional pages; do not shrink the source body type to impose a page cap. Required author declarations and biographies absent from the original are tracked outside the manuscript, with no fabricated content or visible placeholders.

Fidelity gates: inspect every rendered final page; verify title/abstract/body columns, tables, equations, captions, references, and page numbering. Confirm retained reference SHA unchanged. The generated manuscript changes all example body slots; opaque custom XML associated with sample citations is not used for references. Preserve underlying template package styles and theme via python-docx.
