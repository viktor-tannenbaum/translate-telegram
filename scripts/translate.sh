#!/usr/bin/env bash

set -eux -o pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

do_translate() {
  lang=$1
  platform=$2
  iso_code=$3
  python3 make_basic_translation.py                 \
    --defaults_dir data/default                     \
    --platform ${platform}                          \
    --telegram_language_code=${lang}                \
    --iso_language_code=${iso_code}                 \
    --snapshots_dir data/snapshots                  \
    --prompt_template_filename util/prompt.template \
    --openai_api_key=${OPENAI_API_TOKEN}
}

cd ${SCRIPT_DIR}/..

[ "$#" = "2" ]

lang=$1
iso_code=$2

for platform in android android_x tdesktop ios macos weba webk unigram; do
  do_translate ${lang} ${platform} ${iso_code}
done
