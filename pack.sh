#!/bin/bash

ARCHIVE_NAME="${1:-translation.7z}"

# Build file list
FILES=(
    "game/Extras/PDA/PDA.csv"
    "game/Extras/Localization.csv"
    "game/Content/Configuration/Dialogues.csv"
    "trash/state.json"
    "trash/storage.json"
    "trash/statistics.json"
    "trash/ollama.log"
    "trash/dialogues.translate.log"
    "trash/localization.translate.log"
    "trash/pda.translate.log"
)

# Archive
7z a -t7z "$ARCHIVE_NAME" "${FILES[@]}"
