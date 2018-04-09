import ConfigParser

config = ConfigParser.ConfigParser()
config.add_section('Section1')
config.set('Section1','input_destination','133.69.128.66')
config.set('Section1','event_type','histogram-owdelay')
config.add_section('Section2')
config.set('Section2','input_destination2','slac-owamp.es.net')
config.set('Section2','event_type2','histogram-owdelay')
config.add_section('Section3')
config.set('Section3','input_destination3','sdsc-owamp.es.net')
config.set('Section3','event_type3','histogram-owdelay')

with open('test.cfg','wb') as configfile:
    config.write(configfile)

