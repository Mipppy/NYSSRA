from typing import Union
import logging

class BART2_SETTINGS:
    def __init__(self):
        self.loaded_data = {}
        self.load_settings()
        self.logger = logging.getLogger("BART2")
        self.logger.info("Successfully loaded Settings")

    def load_settings(self):
        """
        Settings are put in the file as 
        SETTING_NAME=SETTING_VALUE,SETTING_DEFAULT
        """
        try:
            with open('bart2_settings.txt', 'r') as file:
                for line in file:
                    s_line = line.strip().split('=')
                    self.loaded_data[s_line[0]] = s_line[1].split(',')[0]

        except FileNotFoundError:
            open('bart2_settings.txt','w')
            self.loaded_data = {}
    
    def get_setting(self, setting: str) -> Union[str, int, None]:
        """
        Retrieves a setting value from loaded data with automatic type conversion.
        
        Args:
            setting: The key to look up in the settings data
            
        Returns:
            The setting value as:
            - int if the value is numeric
            - str if the value is a string
            - None if the setting doesn't exist or value is None
            
        """
        if setting not in self.loaded_data:
            return None
            
        value = self.loaded_data[setting]
        
        if value is None:
            return None
        
        if isinstance(value, str) and value.isdigit():
            return int(value)
            
        return value
    
    def update_setting(self, setting_name: str, new_value: str) -> bool:
        """
        Update a specific setting in the configuration file.
        
        Args:
            setting_name: The setting key to update (left of '=')
            new_value: The new value to set (right of '=')
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if setting_name in self.loaded_data:
            self.loaded_data[setting_name] = new_value
        try:
            with open('bart2_settings.txt', 'r') as file:
                lines = file.readlines()
            
            found = False
            with open('bart2_settings.txt', 'w') as file:
                for line in lines:
                    if line.strip().startswith(setting_name + '='):
                        file.write(f"{setting_name}={new_value}\n")
                        found = True
                    else:
                        file.write(line)
            
            # If a TTS setting, update it for immediate change
            if "TTS" in setting_name:
                from instances import Instances
                Instances.announcer.load_settings()
            return found
        except Exception as e:
            self.logger.error(f"Error updating setting: {e}")
            return False
    
    def load_defaults(self) -> None:
        """
        Figure this one out yourself
        """
        try:
            with open('bart2_settings_defaults.txt', 'r') as file:
                for line in file:
                    s_line = line.strip().split('=')
                    self.update_setting(s_line[0],s_line[1])
                
        except Exception as e:
            self.logger.error(f'Error loading defaults {e}')
    
    def update_setting_from_window(self, data:dict):
        """
        This one is actually interesting, as this allows the HTML/JS to easily adjust settings

        Args:
            data (dict): The setting to update and the new value.
        """
        setting = data['setting']
        new_value = data['value']
        if setting and new_value:
            self.update_setting(setting, new_value)