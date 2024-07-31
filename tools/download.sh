#!/usr/bin/env bash

set -eux -o pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

cd ${SCRIPT_DIR}/../data/default

do_download() {
  lang=$1
  curl https://translations.telegram.org/${lang}/android/export -o android.xml
  curl https://translations.telegram.org/${lang}/android_x/export -o android_x.xml
  curl https://translations.telegram.org/${lang}/tdesktop/export -o tdesktop.strings
  curl https://translations.telegram.org/${lang}/ios/export -o ios.strings
  curl https://translations.telegram.org/${lang}/macos/export -o macos.strings
  curl https://translations.telegram.org/${lang}/weba/export -o weba.strings
  curl https://translations.telegram.org/${lang}/webk/export -o webk.strings
  curl https://translations.telegram.org/${lang}/unigram/export -o unigram.xml
}

[ "$#" = "1" ]

if [ "$1" == "--default" ]; then
  cd ${SCRIPT_DIR}/../data/default/en
  do_download "en"

  cd ${SCRIPT_DIR}/../data/default/ru
  do_download "ru"

elif [ "$1" == "--all" ]; then
  cd ${SCRIPT_DIR}/../canonical/$1

  do_download $1
fi