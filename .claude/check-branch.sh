#!/bin/bash
BRANCH=$(git branch --show-current 2>/dev/null)
if ! echo "$BRANCH" | grep -qE '^features/[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}$'; then
    printf '{"continue": false, "stopReason": "Branch must follow format: features/DD_MM_YY_NN (e.g. features/22_03_26_00). Current branch: %s. Run: git checkout -b features/DD_MM_YY_NN"}' "$BRANCH"
fi
