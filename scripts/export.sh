#!/usr/bin/env bash

set -eux -o pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

do_export() {
  lang=$1
  platform=$2
  cano_lang=$3
  output_dir=$4
  python3 merge_and_prepare_candidate.py \
    --defaults_dir data/default \
    --default_languague_code ru \
    --canonical_data_dir data/canonical \
    --canonical_languague_code ${cano_lang} \
    --platform ${platform} \
    --snapshots_dir data/snapshots \
    --telegram_language_code ${lang} \
    --output_dir ${output_dir}
}

cd ${SCRIPT_DIR}/..

[ "$#" = "3" ]

lang=$1
cano_lang=$2
output_dir=$3

for platform in android android_x tdesktop ios macos weba webk unigram; do
  do_export ${lang} ${platform} ${cano_lang} ${output_dir}
done
