#!/bin/bash

shopt -s nullglob

i18n_dir="${BASH_SOURCE%/*}"
static_dir="$i18n_dir/static"
source_dir="$static_dir/source"
redacted_dir="$static_dir/redacted"

mkdir -p $redacted_dir

echo "Redacting sources in $source_dir to $redacted_dir"

for source_file in $source_dir/*; do
  filename=${source_file#$source_dir/}
  redacted_file=$redacted_dir/$filename
  redact $source_file -o $redacted_file
  echo $filename
done

echo "Uploading redacted sources"

$i18n_dir/heroku_crowdin.sh --config $i18n_dir/../crowdin.yml --identity $i18n_dir/../crowdin_credentials.yml upload sources
