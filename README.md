# egs-tools
Empyrion - Galactic Survival Tools

# Purpose
This toolset is designed for:
* creating a translation of the game [Empyrion - Galactic Survival](https://store.steampowered.com/app/383120/Empyrion__Galactic_Survival/) into the desired language
* creating item relationship graphs for the game

## Translation
Translation is performed (for now only) using ollama. Two models are used: regular and smart (specified in options.json). Lines are translated using the regular model, then several checks are performed and if necessary, a request for re-translation is sent with the error indicated. If the translation is incorrect several times (configurable in options.json), then ollama switches to the smarter model. Which models you choose depends only on your capabilities.

### Configuration
Check options.json. In general, I tried to name the options so that their purpose is clear. But it's also desirable to configure a glossary.

### Data Sources
I take data from the original game files. These are `*.ecf` files from `Content/Configuration`, all `*.csv` files, and `Extras/PDA/PDA.yaml`. The path to the files is specified in options.json `conf_path`. Copy the above files preserving the directory structure to a separate folder and specify the path in `conf_path`.
Only translation files (`*.csv`) are modified, the other files are needed for building context.
```
$ tree -d ./data
$ tree data | egrep -v '(png)'
data
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
Path: `context/glossary`. The glossary is a json file of the following format:
```json
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
```
Topic names don't matter and are made exclusively for convenient grouping of terms. Just fill in the glossary for your language minimally to start. Then, as you translate, supplement it with terms that the LLM translates incorrectly.

### Characters
Path: `context/characters`. Here you can describe game characters for more accurate translation. The file format is as follows:
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
The script attempts to find character mentions in the text, focusing on the `keywords` field, and if found - adds information about the character to the LLM prompt. In theory, it should work...

### "Correct/Incorrect" Examples
Path: `context/examples`. Here you can describe examples for the LLM on how to format text correctly. Since this additionally requires code changes, for now this can only be configured for tags. The file format is as follows:
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
For tags, this works as follows: if there are tags in the text, the examples are added to the prompt. If you have an idea what other examples can be added here (and how to understand when to output them to the prompt!) - write in the project Issues.


### Running
For convenience, I created a Makefile and it's enough to run `make translate`

### Cache
As translation progresses, `state.json` file created in the `trash` directory, which store identifiers of already translated lines (just in case the LLM has been translating for a day, and then a cat pressed the computer's power button?). If you want to start translation "from scratch", you should delete this file.

## Graphs
Currently, only a general graph is built. It's huge and difficult to work with. Connections are completely invisible (hard to track), but since this is SVG, I added the ability to navigate between elements by clicking on icons. Just click on the icons with your mouse and you'll understand.

### Configuration
No special configuration is needed other than what's mentioned in the translation section.

### Running
For convenience, I created a Makefile and it's enough to run `make graph`

### Data Sources
In addition to the data sources mentioned above, icons are also needed. They can be extracted from the game using [AssetRipper](https://github.com/AssetRipper/AssetRipper) and placed in the directory specified in `conf_path` with the path `SharedData/Content/Bundles/ItemIcons`.

# Custom Scenarios
If you work with custom scenarios, then `*.ecf` and `*.csv` files should be taken from the scenarios. If the scenario has additional icons (needed only for graphs), you should copy them as well.

# Dependencies
* python library [rich](https://rich.readthedocs.io/en/latest/)
* graphviz (only for graphs)

# Issues
Any questions, suggestions, or just "want to talk" - write in the Issues of this project.
