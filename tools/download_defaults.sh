#!/usr/bin/env bash

set -eux -o pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

cd ${SCRIPT_DIR}/../data/default

do_download() {
  lang=$1
  curl https://translations.telegram.org/${lang}/android/export -o android_${lang}.xml
  curl https://translations.telegram.org/${lang}/android_x/export -o android_x_${lang}.xml
  curl https://translations.telegram.org/${lang}/unigram/export -o unigram_${lang}.xml
  curl https://translations.telegram.org/${lang}/tdesktop/export -o tdesktop_${lang}.strings
  curl https://translations.telegram.org/${lang}/ios/export -o ios_${lang}.strings
  curl https://translations.telegram.org/${lang}/weba/export -o weba_${lang}.strings
  curl https://translations.telegram.org/${lang}/webk/export -o webk_${lang}.strings
  curl https://translations.telegram.org/${lang}/macos/export -o macos_${lang}.strings
}

do_download "en"
do_download "ru"
