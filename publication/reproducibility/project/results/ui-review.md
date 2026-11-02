# UI revision

The Streamlit app now uses a four-step student profile, followed by a dedicated result page.

- Short, clearly named sections and a progress indicator replace the single 30-field form.
- Inputs start blank, use descriptive UCI labels, and are required. This prevents training
  defaults from being silently treated as a real student's answers.
- Back and Continue retain committed entries in session memory. A review confirmation
  prevents accidental final submission. No student record is written to disk.
- Inline feedback names missing fields. Field-specific help explains unusual feature
  meanings, particularly absence totals, past failures, and self-reported ordinal ratings.
- The results page shows the category, estimated probability, interpretation, and exact
  model explanation. It supports editing or starting a new assessment. Changing model
  settings does not relabel an existing result.
- A consistent light palette, spacing, readable text, visible keyboard focus, native
  labeled controls, semantic headings, and responsive columns improve navigation.
- The research disclaimer remains prominent. Technical model settings and research
  performance tables use disclosure controls to keep the primary task focused.

Browser checks covered 390px phone, 760px in-app preview, and 1440px desktop layouts.
Phone and desktop document widths matched the viewport, with no horizontal page overflow.
The form stacks on narrower screens. Required-field feedback was verified in the browser.
`ui-preview.jpg` shows the final interface at the normal in-app browser size.

Eight tests cover the scientific audit, grade exclusion, fold-local preprocessing,
predictions and explanations for both models using real held-out students, model-setting
changes, backward navigation, required fields, final review, editing, resetting, and
unchanged experiment results. `tests.xml` records the executed test results.
`verification.json` records the scientific audit. `ui-change-baseline.json` preserves the
actual pre-revision experiment scores for a regression comparison.

No features, target definition, split, hyperparameter search, model-selection objective,
or threshold were changed. The experiment was rerun to record current source hashes;
all reported metrics match the pre-revision experiment.
