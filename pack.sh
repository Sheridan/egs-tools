#!/bin/bash

ARCHIVE_NAME="${1:-translation.7z}"

    # "trash/ollama.log"
    # "trash/dialogues.translate.log"
    # "trash/localization.translate.log"
    # "trash/pda.translate.log"

# Build file list
FILES=(
    "game/Extras/PDA/PDA.csv"
    "game/Extras/Localization.csv"
    "game/Content/Configuration/Dialogues.csv"
    "trash/stat.db"
    "trash/progress.db"
)

# Archive
7z a -t7z "$ARCHIVE_NAME" "${FILES[@]}"
