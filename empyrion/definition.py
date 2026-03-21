from empyrion.parsers.ecf import CEcf

class CDefinition:
  def __init__(self):
    self.blockGroupsConfig      = CEcf("data/Content/Configuration/BlockGroupsConfig.ecf"     , "BlockGroup"           , "Name")
    self.blocksConfig           = CEcf("data/Content/Configuration/BlocksConfig.ecf"          , "Block"                , "Name")
    self.containers             = CEcf("data/Content/Configuration/Containers.ecf"            , "Container"            , "Id")
    self.damageMultiplierConfig = CEcf("data/Content/Configuration/DamageMultiplierConfig.ecf", "DamageMultiplierGroup", "Name")
    # self.defReputation          = CEcf("data/Content/Configuration/DefReputation.ecf"         , "Reputation"           , "Name")
    self.dialogues              = CEcf("data/Content/Configuration/Dialogues.ecf"             , "Dialogue"             , "Name")
    self.eClassConfig           = CEcf("data/Content/Configuration/EClassConfig.ecf"          , "Entity"               , "Name")
    self.eGroupsConfig          = CEcf("data/Content/Configuration/EGroupsConfig.ecf"         , "EGroup"               , "Name")
    # self.factionWarfare         = CEcf("data/Content/Configuration/FactionWarfare.ecf"        , "Element"              , "Name")
    self.factions               = CEcf("data/Content/Configuration/Factions.ecf"              , "Faction"              , "Name")
    self.galaxyConfig           = CEcf("data/Content/Configuration/GalaxyConfig.ecf"          , "GalaxyConfig"         , "Name")
    self.globalDefsConfig       = CEcf("data/Content/Configuration/GlobalDefsConfig.ecf"      , "GlobalDef"            , "Name")
    self.itemsConfig            = CEcf("data/Content/Configuration/ItemsConfig.ecf"           , "Item"                 , "Name")
    self.lootGroups             = CEcf("data/Content/Configuration/LootGroups.ecf"            , "LootGroup"            , "Name")
    self.materialConfig         = CEcf("data/Content/Configuration/MaterialConfig.ecf"        , "Material"             , "Name")
    self.statusEffects          = CEcf("data/Content/Configuration/StatusEffects.ecf"         , "StatusEffect"         , "Name")
    self.templates              = CEcf("data/Content/Configuration/Templates.ecf"             , "Template"             , "Name")
    self.tokenConfig            = CEcf("data/Content/Configuration/TokenConfig.ecf"           , "Token"                , "Id")
    self.traderNPCConfig        = CEcf("data/Content/Configuration/TraderNPCConfig.ecf"       , "Trader"               , "Name")
