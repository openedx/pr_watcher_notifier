#!/bin/bash
set -eu
app_root_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $app_root_dir
rm -rf $app_root_dir/custom_config
git clone $CUSTOM_CONFIG_REPO $app_root_dir/custom_config
cp $app_root_dir/custom_config/config.yml $WATCH_CONFIG_FILE
CUSTOM_TEMPLATES_DIR="$app_root_dir/custom_config/templates"
if [ -d "$CUSTOM_TEMPLATES_DIR" ]; then
    cp $CUSTOM_TEMPLATES_DIR/* $app_root_dir/pr_watcher_notifier/templates/.
fi
