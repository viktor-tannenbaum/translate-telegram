## Required Python packages
* beautifulsoup4
* lxml

## How to run

### Example of making translations

```bash
python3 make_basic_translation.py                 \
  --data_dir data/default                         \
  --platform android                              \
  --telegram_language_code=bashkir-ex-ru          \
  --iso_language_code=ba                          \
  --snapshots_dir data/candidate                  \
  --prompt_template_filname util/prompt.template  \
  --openai_api_key=${YOUR_OPENAI_API_TOKEN}
```

This will update the snapshots file from `data/candidate` directory for those phrases that are not present there.

### Example of preparing dumps to load to translations platform

```bash
python3 merge_and_prepare_candidate.py        \
  --default_data_dir data/default             \
  --default_languague_code ru                 \
  --canonical_data_dir data/canonical         \
  --canonical_languague_code bashkort-alifba  \
  --platform android                          \
  --snapshots_dir data/candidate              \
  --output_language_code bashkir-ex-ru        \
  --output_dir ${YOUR_OUTPUT_DIRECTORY}
```
