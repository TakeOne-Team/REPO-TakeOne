import xbmcaddon

import os

#########################################################
#         Variáveis globais - NÃO EDITE !!!            #
#########################################################
ADDON_ID = xbmcaddon.Addon().getAddonInfo('id')
PATH = xbmcaddon.Addon().getAddonInfo('path')
ART = os.path.join(PATH, 'resources', 'media')
#########################################################

#########################################################
#        Variáveis de edição do usuário                 #
#########################################################
ADDONTITLE = '[COLOR dodgerblue][B]TakeOne[/B][/COLOR] Wizard'
BUILDERNAME = 'TakeOne-Wizard'
EXCLUDES = [ADDON_ID, 'TakeOneWizard']
# Arquivo de texto com informações da Build nele.
BUILDFILE = 'http://takeoneplus.wuaze.com/builds.txt'
# Com que frequência você gostaria de verificar se há atualizações de versão em dias
# 0 sendo cada inicialização do Kodi
UPDATECHECK = 0
# Arquivo de texto com informações apk nele. Deixe como 'http: //' para ignorar
APKFILE = 'http://'
# Arquivo de texto com urls de vídeos do Youtube. Deixe como 'http: //' para ignorar
YOUTUBETITLE = ''
YOUTUBEFILE = 'http://'
# Arquivo de texto para o instalador do addon. Deixe como 'http: //' para ignorar
ADDONFILE = 'http://'
# Arquivo de texto para configurações avançadas. Deixe como 'http: //' para ignorar
ADVANCEDFILE = 'http://'
#########################################################

#########################################################
#       Itens do menu de temas                            #
#########################################################
# Se você quiser usar ícones armazenados localmente, coloque-os na pasta Recursos / Arte /
# pasta do assistente e, em seguida, use os.path.join (ART, 'imagename.png')
# do not place quotes around os.path.join
# pasta do assistente e, em seguida, use os.path.join (ART, 'imagename.png') 'https://www.yourhost.com/repo/wizard/settings.png'
# Deixe como http: // para o ícone padrão
ICONBUILDS = os.path.join(ART, 'builds.png')
ICONMAINT = os.path.join(ART, 'maintenance.png')
ICONSPEED = os.path.join(ART, 'speed.png')
ICONAPK = os.path.join(ART, 'apkinstaller.png')
ICONADDONS = os.path.join(ART, 'addoninstaller.png')
ICONYOUTUBE = os.path.join(ART, 'youtube.png')
ICONSAVE = os.path.join(ART, 'savedata.png')
ICONTRAKT = os.path.join(ART, 'keeptrakt.png')
ICONREAL = os.path.join(ART, 'keepdebrid.png')
ICONLOGIN = os.path.join(ART, 'keeplogin.png')
ICONCONTACT = os.path.join(ART, 'information.png')
ICONSETTINGS = os.path.join(ART, 'settings.png')
# Hide the section separators 'Yes' or 'No'
HIDESPACERS = 'No'
# Character used in separator
SPACER = '='

# Você pode editá-los como quiser, apenas certifique-se de ter um %s em cada um dos
# THEME's é para pegar o texto do item de menu
COLOR1 = 'dodgerblue'
COLOR2 = 'white'
# Itens do menu principal / {0} é o item do menu e é obrigatório
THEME1 = u'[COLOR {color1}][I][COLOR {color1}][B]Wizard -[/B][/COLOR][COLOR {color2}][COLOR {color1}][/I][/COLOR] [COLOR {color2}]{{}}[/COLOR]'.format(color1=COLOR1, color2=COLOR2)
# Build Nomes             / {0} é o item de menu e é obrigatório
THEME2 = u'[COLOR {color1}]{{}}[/COLOR]'.format(color1=COLOR1)
# Itens alternativos      / {0} é o item do menu e é obrigatório
THEME3 = u'[COLOR {color1}]{{}}[/COLOR]'.format(color1=COLOR1)
# Current Build Header    / {0} é o item de menu e é obrigatório
THEME4 = u'[COLOR {color1}]Build Atual:[/COLOR] [COLOR {color2}]{{}}[/COLOR]'.format(color1=COLOR1, color2=COLOR2)
# Current Theme Header    / {0} é o item de menu e é obrigatório
THEME5 = u'[COLOR {color1}]Theme Atual:[/COLOR] [COLOR {color2}]{{}}[/COLOR]'.format(color1=COLOR1, color2=COLOR2)

# Mensagem para a página de contato
# Habilitar item de menu 'Contato' 'Sim' ocultar ou 'Não' não ocultar
HIDECONTACT = 'Yes'
# Você pode adicionar \n para fazer quebras de linha
CONTACT = 'http://'
# Imagens usadas para a janela de contato. http:// para ícone padrão e fanart
CONTACTICON = os.path.join(ART, 'qricon.png')
CONTACTFANART = 'http://'
#########################################################

#########################################################
# Atualização automática para quem não tem repositório #
#########################################################
# Ative a atualização automática 'Sim' ou 'Não'
AUTOUPDATE = 'Yes'
#########################################################

#########################################################
# Instalação automática do Repo se não estiver instalado#
#########################################################
# Habilite a instalação automática 'Sim' ou 'Não'
AUTOINSTALL = 'No'
# Addon ID para o repositório
REPOID = 'repository.TakeOneWizard'
# Url para o arquivo Addons.xml em sua pasta repo (para que possamos obter a versão mais recente)
REPOADDONXML = 'https://'
# O URL para a pasta zip está localizado em
REPOZIPURL = 'https://'
#########################################################

#########################################################
#        Janela de Notificação                          #
#########################################################
# Ativar tela de notificação Sim ou Não
ENABLE = 'Yes'
# Url para o arquivo de notificação
NOTIFICATION = 'http://'
# Use 'Texto' ou 'Imagem'
HEADERTYPE = 'Text'
# Font size of header
FONTHEADER = 'Font14'
HEADERMESSAGE = '[COLOR dodgerblue][B]TakeOne [/B][/COLOR]Wizard'
# url para a imagem se estiver usando a imagem 424x180
HEADERIMAGE = 'http://'
# Fonte para janela de notificação
FONTSETTINGS = 'Font13'
# Plano de fundo para janela de notificação
BACKGROUND = 'http://'
#########################################################
