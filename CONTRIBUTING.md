# Contributing

Bug reports, Intel NPU benchmark results, prompt examples, and focused pull requests are welcome.

1. Create a branch from `main`.
2. Keep models and runtime binaries out of Git.
3. Run `python -m ruff check .`, `python -m pytest -q`, and
   `node --check src/npu_motion_studio/web/app.js`.
4. Explain the hardware, driver, prompt, inputs, and measured timings for performance changes.

Please do not upload private input images or model files without redistribution permission.
