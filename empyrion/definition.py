from empyrion.parsers.ecf import CEcf
from empyrion.options import options

class CDefinition:
  def __init__(self):
    self.blockGroupsConfig      = CEcf(options.get("conf_path") + "/Content/Configuration/BlockGroupsConfig.ecf"     , "BlockGroup"           , "Name")
    self.blocksConfig           = CEcf(options.get("conf_path") + "/Content/Configuration/BlocksConfig.ecf"          , "Block"                , "Name")
    self.containers             = CEcf(options.get("conf_path") + "/Content/Configuration/Containers.ecf"            , "Container"            , "Id")
    self.damageMultiplierConfig = CEcf(options.get("conf_path") + "/Content/Configuration/DamageMultiplierConfig.ecf", "DamageMultiplierGroup", "Name")
    self.dialogues              = CEcf(options.get("conf_path") + "/Content/Configuration/Dialogues.ecf"             , "Dialogue"             , "Name")
    self.eClassConfig           = CEcf(options.get("conf_path") + "/Content/Configuration/EClassConfig.ecf"          , "Entity"               , "Name")
    self.eGroupsConfig          = CEcf(options.get("conf_path") + "/Content/Configuration/EGroupsConfig.ecf"         , "EGroup"               , "Name")
    self.factions               = CEcf(options.get("conf_path") + "/Content/Configuration/Factions.ecf"              , "Faction"              , "Name")
    self.galaxyConfig           = CEcf(options.get("conf_path") + "/Content/Configuration/GalaxyConfig.ecf"          , "GalaxyConfig"         , "Name")
    self.globalDefsConfig       = CEcf(options.get("conf_path") + "/Content/Configuration/GlobalDefsConfig.ecf"      , "GlobalDef"            , "Name")
    self.itemsConfig            = CEcf(options.get("conf_path") + "/Content/Configuration/ItemsConfig.ecf"           , "Item"                 , "Name")
    self.lootGroups             = CEcf(options.get("conf_path") + "/Content/Configuration/LootGroups.ecf"            , "LootGroup"            , "Name")
    self.materialConfig         = CEcf(options.get("conf_path") + "/Content/Configuration/MaterialConfig.ecf"        , "Material"             , "Name")
    self.statusEffects          = CEcf(options.get("conf_path") + "/Content/Configuration/StatusEffects.ecf"         , "StatusEffect"         , "Name")
    self.templates              = CEcf(options.get("conf_path") + "/Content/Configuration/Templates.ecf"             , "Template"             , "Name")
    self.tokenConfig            = CEcf(options.get("conf_path") + "/Content/Configuration/TokenConfig.ecf"           , "Token"                , "Id")
    self.traderNPCConfig        = CEcf(options.get("conf_path") + "/Content/Configuration/TraderNPCConfig.ecf"       , "Trader"               , "Name")

    # self.defReputation          = CEcf("data/Content/Configuration/DefReputation.ecf"         , "Reputation"           , "Name")
    # self.factionWarfare         = CEcf("data/Content/Configuration/FactionWarfare.ecf"        , "Element"              , "Name")

definition = CDefinition()
