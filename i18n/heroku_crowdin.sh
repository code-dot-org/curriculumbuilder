#!/bin/bash

# This script exists solely to run heroku on crowdin. It's necessary for two
# reasons:
#
# First, java is not available in the heroku path. It could be if we added the
# Heroku JVM buildpack, but unfortunately doing so puts us over the 500mb slug
# limit.
#
# Second, the heroku apt buildpack doesn't correctly add the installed crowdin
# binary to the path (see https://github.com/heroku/heroku-buildpack-apt/pull/10)

apt_lib_dir="/app/.apt/usr/lib"
$apt_lib_dir/jvm/java-11-openjdk-amd64/bin/java -jar "$apt_lib_dir/crowdin/crowdin-cli.jar" "$@"
