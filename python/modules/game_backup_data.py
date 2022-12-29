#!/usr/bin/env python
"""Data for important game files to backup"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import shell_boilerplate as sh


# https://realpython.com/python-data-classes
@dataclass
class GameBackup:
    """Class that tracks game backup details"""
    id: str  # arbitrary 'game_id' given for ad hoc commands
    root: str  # install directory path without game title
    name: str  # directory for the game title (mirrored by backup)
    options: Optional[Dict[str, Any]] = field(default=None)  # provide additional options [only, exclude, include]
    addon: Optional[str] = field(default=None)
    addon_opts: Optional[List[str]] = field(default=None)
    screenshot: Optional[str] = field(default=None)
    screenshot_opts: Optional[List[str]] = field(default=None)
    setting: Optional[str] = field(default=None)
    setting_opts: Optional[List[str]] = field(default=None)


game_root_dir = sh.environment_variable('AppData')  # %UserProfile%/AppData/Roaming

game_backups: List[GameBackup] = [
    # GameBackup(
    #     id='blade_and_soul',
    #     root='/mnt/c/Users/david/Documents/My Games',
    #     name='BnS',
    #     setting="NCWEST",
    # ),
    GameBackup(
        id='diablo_iii',
        root='/mnt/c/Users/david/Documents',
        name='Diablo III',
        screenshot='Screenshots',
        screenshot_opts=['--backup', "--backup-dir=backup_{{ lookup('pipe','date +%Y-%m-%d') }}"],
        setting=' ',
        setting_opts=['--include=D3Prefs.txt', '--exclude=*'],
        options={
            'only': ['global.ini', 'basic/*'],
        },
    ),
    GameBackup(
        id='elder_scrolls_online',
        root='/mnt/c/Users/david/Documents',
        name='Elder Scrolls Online/live',
        addon='AddOns',
        screenshot='Screenshots',
        setting=' ',
        setting_opts=['--include=SavedVariables/', '--include=SavedVariables/*',
                      '--exclude=*/', '--include=*.txt', '--exclude=*'],
    ),
    GameBackup(
        id='elite_dangerous',
        root='/mnt/c/Users/david/AppData/Local',
        name='Frontier Developments/Elite Dangerous',
        screenshot='Screenshots',
        setting='Options/Bindings',
        setting_opts=['--exclude=*.log'],
    ),
    # GameBackup(
    #     id='elite_dangerous_screenshot',
    #     root='/mnt/c/Users/david/Pictures',
    #     name='Frontier Developments/Elite Dangerous',
    #     screenshot=' ',
    # ),
    GameBackup(
        id='final_fantasy_xiv',
        root='/mnt/c/Users/david/Documents/My Games',
        name='FINAL FANTASY XIV - A Realm Reborn',
        screenshot='screenshots',
        setting=' ',
        # setting_opts=['--include=*.cfg', '--exclude=*'],
        setting_opts=[
            '--include=FFXIV_CHR004000174BCC982B/', '--include=FFXIV_CHR004000174BCC982B/*',  # Goo Clone
            '--include=FFXIV_CHR0040002E933812EA/', '--include=FFXIV_CHR0040002E933812EA/*',  # Zaiba Igawa
            '--include=FFXIV_CHR004000174B3A4759/', '--include=FFXIV_CHR004000174B3A4759/*',  # Callia Denma
            '--exclude=log/', '--exclude=log/*', '--exclude=*/'
        ],
    ),
    GameBackup(
        id='hotline_miami',
        root='/mnt/c/Users/david/Documents/My Games',
        name='HotlineMiami',
        setting=' ',
        # setting_opts=['--include=*.cfg', '--exclude=*'],
        setting_opts=['--include=*.sav', '--exclude=*'],
    ),
    GameBackup(
        id='killing_floor_2',
        root='/mnt/c/Users/david/Documents/My Games',
        name='KillingFloor2',
        setting='KFGame/Config',
    ),
    GameBackup(
        id='rocket_league',
        root='/mnt/c/Users/david/Documents/My Games',
        name='Rocket League',
        setting='TAGame/Config',
    ),
    # GameBackup(
    #     id='sims_iii',
    #     # Sims 3 [archive screenshots/settings/addons, run memory cleanup]
    # ),
    GameBackup(
        id='skyrim_se',
        root='/mnt/c/Users/david/Documents/My Games',
        name='Skyrim Special Edition',
        setting=' ',
        setting_opts=['--include=Saves/', '--include=Saves/*', '--exclude=*/', '--include=*.ini', '--exclude=*'],
    ),
    GameBackup(
        id='skyrim_vr',
        root='/mnt/c/Users/david/Documents/My Games',
        name='Skyrim VR',
        setting=' ',
        setting_opts=['--include=Saves/', '--include=Saves/*', '--exclude=*/', '--include=*.ini', '--exclude=*'],
    ),
    GameBackup(
        id='stardew_valley',
        root='/mnt/c/Users/david/AppData/Roaming',
        name='StardewValley',
        setting=' ',
    ),
    GameBackup(
        id='world_of_warcraft',
        root='/mnt/e/GameFiles',
        name='World of Warcraft/_retail_',
        addon='Interface/AddOns',
        addon_opts=['--exclude=DataStore*/', '--exclude=TradeSkillMaster_AppHelper/'],
        screenshot='Screenshots',
        setting='WTF',
        setting_opts=['--exclude=*.bak', '--exclude=*.old'],
    ),
    GameBackup(
        id='world_of_warcraft_classic',
        root='/mnt/e/GameFiles',
        name='World of Warcraft/_classic_',
        addon='Interface/AddOns',
        addon_opts=['--exclude=DataStore*/', '--exclude=TradeSkillMaster_AppHelper/'],
        screenshot='Screenshots',
        setting='WTF',
        setting_opts=['--exclude=*.bak', '--exclude=*.old'],
    ),
    GameBackup(
        id='world_of_warcraft_weakauras_companion',
        root='/mnt/c/Users/david/AppData/Roaming',
        name='weakauras-companion',
        setting=' ',
        setting_opts=['--include=config.json', '--exclude=*'],
    ),
    GameBackup(
        id='yiffalicious',
        root='/mnt/c/Users/david/AppData/Roaming',
        name='yiffalicious',
        screenshot='screenshots',
        setting='interactions/favorites',
    ),

    # --- Covered by OneDrive ---
    # overwatch
    # --- Covered by Steam ---
    # *most other games
]
