import configparser

############ Config ############
def get_config(path):
    """
    Returns the config object
    """    
    print ('read config')
    config = configparser.ConfigParser()
    config.read(path, encoding='utf-8')
    
    return config
 
 
def get_setting(path, section, setting):
    """
    Print out a setting
    """
    print('get value config')
    config = get_config(path)
    value = config.get(section, setting)
    
    return value
 
 
def update_setting(path, section, setting, value):
    """
    Update a setting
    """
    print ('update config')
    config = get_config(path)
    config.set(section, setting, value)
    with open(path, "w", encoding='utf-8') as config_file:
        config.write(config_file)
 
 
def delete_setting(path, section, setting):
    """
    Delete a setting
    """
    print ('delete config')
    config = get_config(path)
    config.remove_option(section, setting)
    with open(path, "w") as config_file:
        config.write(config_file)
