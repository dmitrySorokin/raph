from nethack_raph.glossaries.ArmorGlossary import ARMOR_GLOSSARY
from nethack_raph.glossaries.MonsterGlossary import MONSTERS_GLOSSARY
from nethack_raph.glossaries.WeaponGlossary import WEAPON_GLOSSARY

throw_skills = {'dart', 'shuriken', 'spear', 'dagger', 'knife'}
ITEMS_TO_THROW = {k for k, v in WEAPON_GLOSSARY.items() if v['skill'] in throw_skills}

melee_skills = {
    'flail', 'dagger', 'hammer', 'knife', 'long sword', 'short sword', 'morning star',
    'spear', 'trident', 'two-handed sword', 'whip', 'axe', 'broadsword', 'club',
    'lance', 'pick-axe', 'mace', 'polearms', 'quarterstaff', 'saber', 'scimitar'
}

MELEE_WEAPON = {k for k, v in WEAPON_GLOSSARY.items() if v['skill'] in melee_skills}

LAUNCHERS = {'bow', 'runed bow', 'runed bow', 'long bow', 'crossbow', 'sling'}
LAUNCHERS = [k for k, v in WEAPON_GLOSSARY.items() if v['name'] in LAUNCHERS]
MISSILES = [k for k, v in WEAPON_GLOSSARY.items() if v['skill'] in {'bow', 'crossbow', 'sling'} and k not in LAUNCHERS]
