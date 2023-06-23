from configparser import SafeConfigParser
import os

# On récupère le fichier config.ini contenant les informations sur les caméras et les chemins d'accès
configfile=os.path.join(os.getcwd(),"config.ini")



config_parser = SafeConfigParser()
config_parser.read(configfile)

'''
This part is not used with the current architecture
'''

if os.name=="nt": #means this program is running on windows
    if os.getlogin()=="g.chauveau":
        config_parser.set("filesystem", "passerelle_path", config_parser["filesystem"]["passerelle_path_guillaume"])
    else:
        config_parser.set("filesystem", "passerelle_path", config_parser["filesystem"]["passerelle_path_windows"])
elif os.name=='posix': #means this program is running on linux
    if os.getlogin()=="guillaume":
        config_parser.set("filesystem", "passerelle_path", config_parser["filesystem"]["passerelle_path_linux_guillaume"])
    else:
        config_parser.set("filesystem", "passerelle_path", config_parser["filesystem"]["passerelle_path_linux"])
else :
    print("Unknown OS")