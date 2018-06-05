#!/bin/bash

# This script exists solely to run heroku on crowdin. It's necessary for two
# reasons:
#
# First, the heroku apt buildpack doesn't correctly add the installed crowdin
# binary to the path (see https://github.com/heroku/heroku-buildpack-apt/pull/10)
#
# Second, the heroku apt buildpack also doesn't add the java executable to the
# path. This might be because the default-jre package expects
# update-alternatives to set up the symlinks, but the actual cause is unclear.
#
# Either way, this script exists solely to get around that, and if we are ever
# able to come up with a clean way to install the crowdin-cli and its
# dependencies on heroku this can be removed.

apt_dir="${BASH_SOURCE%/*}/../.apt/"
$apt_dir/usr/lib/jvm/java-8-openjdk-amd64/bin/java -jar "$apt_dir/usr/local/bin/crowdin-cli.jar" "$@"
