#!/bin/bash

shopt -s nullglob

i18n_dir="${BASH_SOURCE%/*}"
static_dir="$i18n_dir/static"
source_dir="$static_dir/source"
locale_dir="$static_dir/translations"

echo "Downloading translations to $locale_dir"

$i18n_dir/heroku_crowdin.sh --config $i18n_dir/../crowdin.yml --identity $i18n_dir/../crowdin_credentials.yml download

echo "Restoring translations from $source_dir:"

locales=($locale_dir/*)
num_locales=${#locales[@]}
for source_file in $source_dir/*; do
  filename=${source_file#$source_dir/}
  for index in ${!locales[@]}; do
    locale=${locales[index]#$locale_dir/}
    locale_file=${locales[index]}/$filename
    echo -ne "$filename - restoring $locale_file ($((index+1))/$num_locales)\r"
    restore -s $source_file -r $locale_file -o $locale_file
  done
  echo -e "\r\033[K$filename - finished"
done
