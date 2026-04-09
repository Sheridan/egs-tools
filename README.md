# egs-tools
**Empyrion - Galactic Survival Tools**

## Purpose
This toolset is designed for:
* Creating a translation of the game [Empyrion - Galactic Survival](https://store.steampowered.com/app/383120/Empyrion__Galactic_Survival/) into your desired language.
* Generating item relationship graphs for the game.

## Translation
Translation is currently performed using **ollama**. Two models are used: `translator` and `reasoner` (configured in `options.json`). Translation tasks are sent to the `translator`. When the algorithm detects errors in the translation, it asks the `reasoner` to correct them. Which models you choose depends on your available resources.

### Configuration
Review `options.json`. I’ve tried to name the options clearly. You should also set up a glossary (see below).

### Data Sources
The tool uses data from the original game files: all `*.ecf` files from `Content/Configuration`, all `*.csv` files, and `Extras/PDA/PDA.yaml`. Specify the path to these files in `options.json` under `conf_path`. Copy the files listed above, preserving the directory structure, into a separate folder and point `conf_path` to that folder.

> Only translation files (`*.csv`) are modified. The other files are only needed for building context.
> **If the script crashes when loading files**, first make sure the file ends with a blank line.

Example of required file structure:
```
$ tree game | egrep -v '(png)'
game
├── Content
│   └── Configuration
│       ├── BlockGroupsConfig.ecf
│       ├── BlocksConfig.ecf
│       ├── Containers.ecf
│       ├── DamageMultiplierConfig.ecf
│       ├── DefReputation.ecf
│       ├── Dialogues.csv
│       ├── Dialogues.ecf
│       ├── EClassConfig.ecf
│       ├── EGroupsConfig.ecf
│       ├── FactionWarfare.ecf
│       ├── Factions.ecf
│       ├── GalaxyConfig.ecf
│       ├── GlobalDefsConfig.ecf
│       ├── ItemsConfig.ecf
│       ├── LootGroups.ecf
│       ├── MaterialConfig.ecf
│       ├── SqlQueries.txt
│       ├── StatusEffects.ecf
│       ├── Templates.ecf
│       ├── TokenConfig.ecf
│       ├── TraderNPCConfig.ecf
│       └── Using Modified Configs READ FIRST.txt
├── Extras
│   ├── Localization.csv
│   └── PDA
│       ├── PDA.csv
│       └── PDA.yaml
└── SharedData
    └── Content
        └── Bundles
            └── ItemIcons
```

### Glossary
The glossary improves translation accuracy for specific words, terms, or phrases. When you add new entries to the glossary, the translator will re‑translate any lines that contain those entries.

**Path:** `context/glossary`
The glossary is a JSON file with the following format:
```json
{
  "insignificant_words":
  [
    "the", "and", "block", "blocks", "space", "light", "hard"
  ],
  "untranslable":
  [
    "whakaatu", "kaitiaki", "taatau", "kaupapa", "whakakake", "whakamatau", "manene", "hackan",
    "sssst", "Arachshe", "Benkult", "Fin fet!", "Hackan li boi", "Qe Genfet", "Nu nu nu", "Bejut",
    "terrsss", "L<i>ow</i>er"
  ],
  "glossary":
  {
    "topic1":
    {
      "english text": "your language text",
      ...
      "english text1": "your language text1"
    },
    "topic2":
    {
      "english text": "your language text",
      ...
      "english text1": "your language text1"
    }
  }
}
```
- `insignificant_words` – very common words that would only clutter the glossary.
- `untranslable` – words that should not be translated. If any of these appear in a text, the whole text is left untranslated.
- `glossary` – the actual glossary. Topic names are irrelevant – they only help you group terms. Start by filling in the glossary with a minimum set of terms for your language, then add more as you encounter words that the LLM translates incorrectly.

### Characters
Here you can describe game characters for more accurate translation. The script looks for character names using the `keywords` list. A character’s gender influences the translation of their lines.

**Path:** `context/characters`
File format:
```json
{
  "characters":
  {
    "name":
    {
      "keywords": ["possible", "encountered", "character names"],
      "gender": "male, female, other",
      "characteristic":
      [
        "character characteristic one",
        "character characteristic two",
        "for example, 'likes to joke'"
      ]
    },
    ...
  }
}
```
When the script finds a mention of a character (using the `keywords` field), it adds information about that character to the LLM prompt. In theory, this should improve translation.

### "Correct/Incorrect" Examples
**Path:** `context/examples`
You can provide examples to teach the LLM how to format text correctly. Currently this only works for **tags** (code changes would be required for other use cases). The file format is:
```json
{
  "tags":
  [
    {
      "original": "Original string",
      "correct":
      [
        "Correct processing example one",
        "Correct processing example two and so on"
      ],
      "wrong":
      [
        "Incorrect processing example one",
        "Incorrect processing example two and so on"
      ]
    },
    ...
  ]
}
```
For tags, the logic is: if the text contains tags, these examples are added to the prompt.
**Do not add examples without a good reason** – only add them when you notice the model consistently making a specific mistake. If you have ideas for other kinds of examples (and how to decide when to include them), please open an Issue.

### Running the Translation
For convenience, a `Makefile` is provided. Simply run:
```bash
make translate
```

### Cache
As translation progresses, a `progress.db` (SQLite3) file is created in the `trash` directory. It stores identifiers of already translated lines – just in case the LLM has been translating for a day and then a cat steps on the power button.
If you want to start translation from scratch, delete this file. However, if you need to translate **updated** files, **do not delete** `progress.db` – it will restore already translated lines without sending unnecessary requests to the LLM.

## Graphs
Currently only a general graph is built. It is huge and not very easy to work with – connections are hard to trace. Because the output is SVG, you can click on icons to navigate between elements. Give it a try.

### Configuration
No special configuration is needed beyond what is described in the translation section.

### Running the Graph
Use the Makefile:
```bash
make graph
```

### Data Sources for Graphs
In addition to the data sources mentioned above, you will need **icons**. Extract them from the game using [AssetRipper](https://github.com/AssetRipper/AssetRipper) and place them in the directory specified by `conf_path` under the path `SharedData/Content/Bundles/ItemIcons`.

## Custom Scenarios
If you work with custom scenarios, take the `*.ecf` and `*.csv` files from the scenario folder. If the scenario has additional icons (needed only for graphs), copy them as well.

## Dependencies
* Python library [rich](https://rich.readthedocs.io/en/latest/)
* SQLite3
* graphviz (only for graphs)

## Issues
Any questions, suggestions, or just a desire to talk – please open an Issue in this project.
