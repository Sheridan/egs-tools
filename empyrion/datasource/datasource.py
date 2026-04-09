from empyrion.options import options
from empyrion.parsers.csv import CCsv
from empyrion.parsers.ecf import CEcf

class CDataSource:
  def __init__(self):
    self._src_language = options.get("translation.src_language", "English")
    self._dst_language = options.get("translation.dst_language", "Russian")
    self._conf_path = options.get("conf_path")
    self._data = {}
    self._sources = {
      'data': {
        'blockGroupsConfig':      { 'path': "/Content/Configuration/BlockGroupsConfig.ecf"     , 'name': "BlockGroup"           , 'keyfield': 'Name' },
        'blocksConfig':           { 'path': "/Content/Configuration/BlocksConfig.ecf"          , 'name': "Block"                , 'keyfield': 'Name' },
        'containers':             { 'path': "/Content/Configuration/Containers.ecf"            , 'name': "Container"            , 'keyfield': 'Id' },
        'damageMultiplierConfig': { 'path': "/Content/Configuration/DamageMultiplierConfig.ecf", 'name': "DamageMultiplierGroup", 'keyfield': 'Name' },
        'ds_dialogues':           { 'path': "/Content/Configuration/Dialogues.ecf"             , 'name': "Dialogue"             , 'keyfield': 'Name' },
        'eClassConfig':           { 'path': "/Content/Configuration/EClassConfig.ecf"          , 'name': "Entity"               , 'keyfield': 'Name' },
        'eGroupsConfig':          { 'path': "/Content/Configuration/EGroupsConfig.ecf"         , 'name': "EGroup"               , 'keyfield': 'Name' },
        'factions':               { 'path': "/Content/Configuration/Factions.ecf"              , 'name': "Faction"              , 'keyfield': 'Name' },
        'galaxyConfig':           { 'path': "/Content/Configuration/GalaxyConfig.ecf"          , 'name': "GalaxyConfig"         , 'keyfield': 'Name' },
        'globalDefsConfig':       { 'path': "/Content/Configuration/GlobalDefsConfig.ecf"      , 'name': "GlobalDef"            , 'keyfield': 'Name' },
        'itemsConfig':            { 'path': "/Content/Configuration/ItemsConfig.ecf"           , 'name': "Item"                 , 'keyfield': 'Name' },
        'lootGroups':             { 'path': "/Content/Configuration/LootGroups.ecf"            , 'name': "LootGroup"            , 'keyfield': 'Name' },
        'materialConfig':         { 'path': "/Content/Configuration/MaterialConfig.ecf"        , 'name': "Material"             , 'keyfield': 'Name' },
        'statusEffects':          { 'path': "/Content/Configuration/StatusEffects.ecf"         , 'name': "StatusEffect"         , 'keyfield': 'Name' },
        'templates':              { 'path': "/Content/Configuration/Templates.ecf"             , 'name': "Template"             , 'keyfield': 'Name' },
        'tokenConfig':            { 'path': "/Content/Configuration/TokenConfig.ecf"           , 'name': "Token"                , 'keyfield': 'Id' },
        'traderNPCConfig':        { 'path': "/Content/Configuration/TraderNPCConfig.ecf"       , 'name': "Trader"               , 'keyfield': 'Name' },
        'defReputation':          { 'path': "/Content/Configuration/DefReputation.ecf"         , 'name': "Reputation"           , 'keyfield': "Name"},
        'factionWarfare':         { 'path': "/Content/Configuration/FactionWarfare.ecf"        , 'name': "Element"              , 'keyfield': "Name"}
      },
      'translation': {
        'localization': { 'path': "/Extras/Localization.csv"             },
        'dialogues':    { 'path': "/Content/Configuration/Dialogues.csv" },
        'pda':          { 'path': "/Extras/PDA/PDA.csv"                  }
      }
    }

  def _loadSource(self, source):
    if source in self._sources['data']:
      return CEcf(self._conf_path + self._sources['data'][source]['path'], self._sources['data'][source]['name'], self._sources['data'][source]['keyfield'])
    if source in self._sources['translation']:
      return CCsv(self._conf_path + self._sources['translation'][source]['path'], self._src_language, self._dst_language)
    return None

  def __getitem__(self, source):
    if source not in self._data.keys():
      self._data[source] = self._loadSource(source)
    return self._data[source]

  def datasources(self, group):
    return self._sources[group].keys()

  def exists(self, group, name):
    return name in self._sources[group]

datasource = CDataSource()
