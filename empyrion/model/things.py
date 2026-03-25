import os
import shutil
import pprint
import json
from empyrion.definition import definition
from empyrion.translation import translation
from empyrion.options import options
from empyrion.objectcache import ObjectCache

class CCThings:
  def __init__(self):
    self.icons_path = options.get("conf_path") + "/SharedData/Content/Bundles/ItemIcons"
    self.default_icon = "Eden_DummyRE"
    self.output_path = "output/graph/icons"
    self._used_in_index = {}
    self._things_cache = ObjectCache()

  def exportIcon(self, name):
    dst_filename = f"{self.output_path}/{name}.png"
    src_filename = f"{self.icons_path}/{name}.png"
    os.makedirs(self.output_path, exist_ok=True)
    if os.path.exists(dst_filename):
      src_size = os.path.getsize(src_filename)
      dst_size = os.path.getsize(dst_filename)
      if src_size == dst_size:
        return
    shutil.copy2(src_filename, dst_filename)

  def _iconExists(self, icon):
    return os.path.isfile(f"{self.icons_path}/{icon}.png")

  def _thingIcon(self, thing):
    if 'CustomIcon' in thing['thing']:
      if self._iconExists(thing['thing']['CustomIcon']):
        return thing['thing']['CustomIcon']
    if self._iconExists(thing['things_keys']['thing']):
      return thing['things_keys']['thing']
    if 'recipe' in thing['things_keys']:
      if self._iconExists(thing['things_keys']['recipe']):
        return thing['things_keys']['recipe']
    return self.default_icon

  def thingIcon(self, thing):
    icon = self._thingIcon(thing)
    self.exportIcon(icon)
    return icon

  def _translateThing(self, thing):
    description_key = f"{thing['things_keys']['thing']}info"
    if 'Info' in thing['merged']:
      description_key = thing['merged']['Info']['value'] if 'value' in thing['merged']['Info'] else thing['merged']['Info']
    return {
      'caption': translation.translateKey(thing['things_keys']['thing']),
      'description': translation.translateKey(description_key)
    }

  def thingHasCrafting(self, thing):
    return ( 'recipe' in thing and
             thing['recipe'] and
             'Child' in thing['recipe'] and
             'Inputs' in thing['recipe']['Child'] and
             len(thing['recipe']['Child']['Inputs'].items()) > 0 and
             'Target' in thing['recipe'] and
             (thing['recipe']['Target'] != '' and thing['recipe']['Target'] != '""')
           )

  def thingTemplate(self, key, raw):
    recipeKey = key
    if 'TemplateRoot' in raw:
      recipeKey = raw['TemplateRoot']
    return (definition['templates'].get(recipeKey), recipeKey)

  def _getThing(self, block, key):
    cache_key = f"{block}_{key}"
    if not self._things_cache.contains(cache_key):
      raw = definition[block].get(key)
      if raw:
        thing = { 'thing': raw,
                  'source': block,
                  'things_keys': { 'thing': key } }
        (template, template_key) = self.thingTemplate(key, raw)
        if template:
          thing['recipe'] = template
          thing['things_keys']['recipe'] = template_key
        if 'Ref' in thing['thing']:
          parent = self._getThing(block, thing['thing']['Ref'])
          if parent:
            thing['parent'] = parent
        thing['merged'] = (thing['parent']['thing'] if 'parent' in thing and thing['parent'] else {}) | thing['thing']
        thing['hasCrafting'] = self.thingHasCrafting(thing)
        thing['icon'] = self.thingIcon(thing)
        thing['labels'] = self._translateThing(thing)
        return self._things_cache.set(cache_key, thing)
      return self._things_cache.set(cache_key, None)
    return self._things_cache.get(cache_key)

  def _searchByKey(self, keyname, thing):
    childs = []
    for child in definition[thing['source']].search(keyname, thing['things_keys']['thing']):
      child_thing = self._getThing(thing['source'], child['Name'])
      if child_thing:
        childs.append(child_thing)
    if len(childs) > 0:
      return childs
    return None

  def _weaponAmmoKeyFromWeaponItemKey(self, weapon_item_key):
    raw = definition['itemsConfig'].get(weapon_item_key)
    if raw and 'Child' in raw and '0' in raw['Child'] and 'AmmoType' in raw['Child']['0']:
      return raw['Child']['0']['AmmoType']['value']
    return None

  def _thisAmmoForThisWeapon(self, weapon_ammo_key, weapon_item_key):
    raw = definition['itemsConfig'].get(weapon_item_key)
    return ( raw and
            'Category' in raw and raw['Category'] == 'Weapons/Items' and
            'Child' in raw and '0' in raw['Child']
            and 'AmmoType' in raw['Child']['0'] and
            raw['Child']['0']['AmmoType']['value'] == weapon_ammo_key)

  def _weaponItemKeyFromWeaponAmmoKey(self, weapon_ammo_key):
    for key in definition['itemsConfig'].names():
      if self._thisAmmoForThisWeapon(weapon_ammo_key, key):
        return definition['itemsConfig'].get(key)['Name']
    return None

  def _mineWeaponAmmo(self, weapon_item_key):
    if weapon_item_key:
      weapon_ammo_key = self._weaponAmmoKeyFromWeaponItemKey(weapon_item_key)
      return self._getThing('itemsConfig', weapon_ammo_key)
    return None

  def _mineAmmoWeapon(self, weapon_ammo_key):
    weapons = []
    if weapon_ammo_key:
      for key in definition['itemsConfig'].names():
        if self._thisAmmoForThisWeapon(weapon_ammo_key, key):
          weapons.append(self._getThing('itemsConfig', key))
    if len(weapons) > 0:
      return weapons
    return None

  def _mineWeapon(self, thing):
    print(f'Mining weapon data of {thing['merged']['Name']}...')
    weapon_item_key = None
    weapon_ammo_key = None
    weapon_or_ammo = None
    if thing['source'] == 'blocksConfig' and 'WeaponItem' in thing['merged']: # is classic weapon block
      weapon_item_key = thing['merged']['WeaponItem']
      weapon_or_ammo = 'weapon'
    if thing['source'] == 'blocksConfig' and 'AmmoType' in thing['merged']: # is RE2 weapon block
      weapon_ammo_key = thing['merged']['AmmoType']['value']
      weapon_or_ammo = 'weapon'
    if thing['source'] == 'itemsConfig' and 'HoldType' in thing['merged'] and int(thing['merged']['HoldType']) > 0: # is weapon item
      weapon_item_key = thing['merged']['Name']
      weapon_or_ammo = 'weapon'
    if thing['source'] == 'itemsConfig' and 'HoldType' in thing['merged'] and int(thing['merged']['HoldType']) == 0 and 'Canhold' in thing['merged'] and thing['merged']['Canhold'] == 'false': # is probally bullet
      weapon_ammo_key = thing['merged']['Name']
      weapon_or_ammo = 'ammo'
      # if 'Child' in thing['merged'] and '0' in thing['merged']['Child'] and 'Class' in thing['merged']['Child']['0'] and thing['merged']['Child']['0']['Class'] == 'Projectile': # is bullet 4 turrel
      #   weapon_ammo_key = thing['merged']['Name']
    if weapon_item_key is not None and weapon_ammo_key is None:
      weapon_ammo_key = self._weaponAmmoKeyFromWeaponItemKey(weapon_item_key)
    if weapon_ammo_key is not None and weapon_item_key is None:
      weapon_item_key = self._weaponItemKeyFromWeaponAmmoKey(weapon_ammo_key)
    result = {
      'item': None if weapon_item_key is None else self._getThing('itemsConfig', weapon_item_key),
      'weapon_or_ammo': weapon_or_ammo,
      'ammo': self._mineWeaponAmmo(weapon_item_key),
      'weapon': self._mineAmmoWeapon(weapon_ammo_key)
    }
    if result['ammo'] or result['weapon']:
      return result
    return None

  def _thingRecipe(self, thing):
    if 'recipe' in thing and 'Child' in thing['recipe'] and 'Inputs' in thing['recipe']['Child']:
      return thing['recipe']['Child']['Inputs']
    return None

  def _thingInRecipe(self, thing, recipe):
    for recipe_item in recipe.keys():
      if recipe_item == thing['things_keys']['thing']:
        return True
    return False

  def _getUsedIn(self, thing):
    print(f'Mining thing {thing['merged']['Name']} used in recipes...')
    result = []
    if thing['things_keys']['thing'] in self._used_in_index:
      result = self._used_in_index[thing['things_keys']['thing']]
    if len(result) > 0:
      print(f"Thing {thing['things_keys']['thing']} used in {len(result)} recipes")
      return result
    return None

  def _appendInRecipeIndex(self, recipe_item, thing):
    if recipe_item not in self._used_in_index:
      self._used_in_index[recipe_item] = []
    self._used_in_index[recipe_item].append(thing)

  def _buildUsedInIndex(self):
    for block in ['blocksConfig', 'itemsConfig']:
      for key in definition[block].names():
        thing = self._getThing(block, key)
        if thing and self._canAddToThings(thing) and not self._isChild(thing) and thing['hasCrafting']:
          thing_recipe = self._thingRecipe(thing)
          if thing_recipe:
            for recipe_item in thing_recipe.keys():
              self._appendInRecipeIndex(recipe_item, thing)
    # pprint.pprint(self._used_in_index)

  def _getChilds(self, thing):
    if 'ChildBlocks' in thing['thing']:
      childs = []
      for child_key in thing['thing']['ChildBlocks'].strip('"').split(','):
        child_key = child_key.strip()
        child_thing = self.getThing(child_key)
        if child_thing:
          childs.append(child_thing)
      if len(childs) > 0:
        return childs
    return None

  def getThing(self, key):
    for block in ['blocksConfig', 'itemsConfig']:
      thing = self._getThing(block, key)
      if thing:
        if options.get("graph.referenced", False):
          referenced = self._searchByKey('Ref', thing)
          if referenced:
            thing['referenced'] = referenced
        if options.get("graph.neighbors", False):
          neighbors = self._searchByKey('TemplateRoot', thing)
          if neighbors:
            thing['neighbors'] = neighbors
        if options.get("graph.childs", True):
          childs = self._getChilds(thing)
          if childs:
            thing['childs'] = childs
        if options.get("graph.used_in", True):
          used_in = self._getUsedIn(thing)
          if used_in:
            thing['used_in'] = used_in
        if 'Category' in thing['merged'] and thing['merged']['Category'] == 'Weapons/Items':
          weapon = self._mineWeapon(thing)
          if weapon:
            thing['weapon'] = weapon
        return thing
    return None

  def _isChild(self, thing):
    if thing['source'] == 'blocksConfig':
      for block in ['blocksConfig']:
        for key in definition[block].names():
          raw = definition[block].get(key)
          if raw and 'ChildBlocks' in raw:
            for child_key in raw['ChildBlocks'].strip('"').split(','):
              if thing['merged']['Name'] == child_key.strip():
                return True
    return False

  def _canAddToThings(self, thing):
    # if 'Class' in thing['merged'] and thing['merged']['Class'] in ['PlantGrowing', 'NPCDialogue']: #'CropsGrown'
    #   return False
    if 'ShowUser' in thing['merged'] and thing['merged']['ShowUser'] != 'Yes':
      return False
    if thing['source'] == 'itemsConfig' and 'Category' not in thing['merged']:
      return False
    if thing['source'] == 'blocksConfig' and 'ParentBlocks' in thing['merged']:
      return False
    if thing['source'] == 'blocksConfig' and 'recipe' not in thing:
      return False
    return True

  def things(self):
    result = []
    self._buildUsedInIndex()
    for block in ['blocksConfig', 'itemsConfig']:
      block_total_records = definition[block].count()
      block_current_record = 0
      for key in definition[block].names():
        block_current_record += 1
        print(f'[{block}] [{block_current_record} of {block_total_records}] Mining key {key}...')
        thing = self.getThing(key)
        if self._canAddToThings(thing) and not self._isChild(thing):
          # pprint.pprint(thing)
          print(f'Appending {key} of block {block} to things render list...')
          result.append(thing)
    print(f'Total things in things render list: {len(result)}')
    with open("trash/data.json", "w", encoding="utf-8") as f:
      json.dump(result, f, ensure_ascii=False, indent=4)
    return result

things = CCThings()
