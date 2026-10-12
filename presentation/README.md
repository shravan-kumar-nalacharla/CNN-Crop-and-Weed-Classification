# Individual ten-minute presentation

Roll_43_VGG16_Presentation.pptx contains eleven slides with speaker notes and timings totaling 600 seconds. Full-run result placeholders are intentional until outputs/results_summary.json reports full_training_completed. Smoke numbers are never imported.

Rebuild with scripts/build_presentation.mjs using the Codex bundled Node runtime and @oai/artifact-tool. Set CODEX_ARTIFACT_RUNTIME and CODEX_PRESENTATIONS_SKILL when their paths differ. Link .build/node_modules to the bundled runtime node_modules first. The finalizer checks package integrity, slide count, geometry and fonts; inspect rendered .build/slides images after any rebuild. This authoring dependency is separate from Python model training.
