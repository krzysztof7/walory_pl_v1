# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 20:21:32 2017

@author: Krzysztof Piotrowski
"""

"""
Częsci kodu:
    1) Wczytanie tablicy/pliku z danymi: nazwa, wsp_x, wsp_y
    1a) Zaimportowanie danych w formacie csv
    2) Losowanie elementu
    2a) Losowanie z wagami - tj czestsze losowanie elementow sprawiajacych trudnosc (po zaimportowaniu wyników)
    3) Wyswietlenie pytania urzytkownikowi i przyjęcie odpowiedzi
    3a) Sprawdzenie czy dane są we własciwym formacie
    3b) Limitowanie czasu na odpowiedź
    3c) Przyjecie odpowiedzi na mapie (oraz zwrocenie wyniku na mapie)
    4) Weryfikacja poprawnosci (tj. odległosci pomiędzy faktyczynmi, a wprowadzonymi przez urzytkownika)
    4a) Przeliczenie odległosci na rzeczywistą (tj. wspólrzędne geograficzne a układ 1992/2000 lub dla WGS odległość)
    5) Zwrócenie informacji o poprawnej lokalizacji, poprawnosci oraz przyznanie punktow
    5a) Wyeksportowanie do pliku wyniku końcowego oraz elementow sprawiajacych klopoty (do kolejnego cyklu nauki)
    6) Powrót do kolejnego
    
Uwagi:
    Oczywiście  może tak być, ale pomysł dodania później konturówki Polski podsunął mi myśl, 
    że mógłbyś równoważnie zamiast tego napisać najpierw częściowy parser formatu SVG 
    (Shape do takiej zabawy na początku jest zbyt skomplikowany), 
    tzn. poszukać kontur Polski z województwami w SVG (to czysto tekstowy plik typu HTML) 
    i wyciągnąć z niego geometrię, a później wprowadzić ją do Matplotlib w adekwatnym dla niego formacie. 

"""

# 1 Zdefiniowanie listy walorow ze wspołrzędnymi (zmienna walory_zestaw)
# to będzie do usunięcia, gdy import zestawow będzie działał
#walory_zestaw = [["Poznań",52.4,16.9],["Świnoujście",53.9,14.2],["Suwałki",54.1,22.9],["Opołonek",49.0,22.9],["Śnieżka",50.7,15.7]]

#%% 
def import_zestawu ():
    """
    Funkcja pozwalająca na wybor zestawu, importująca go i konwertująca na listę list
    Wczytuje plik w kodowaniu utf-8
    
    !!! wyswietlac tylko pliki *.txt - w tej chwili rownież txt w dowolnej częsci nazwy wyswietli
    """
    import os ### czy importowanie modułow lepiej zapisywać tutaj czy gdzies globalnie, czy w danej funkcji na początku?
   
    sciezka = (os.getcwd()) # sprawdzenie w jakim katalogu się znajdujemy (katalog bieżący)
    pliki = os.listdir(sciezka) # lista plikow w katalogu bieżącym
    
    pliki_txt = "" #zestawienie plikow txt (typ str) do wyswietlenia użytkowinikowi 
    for x in range(len(pliki)):
        if "txt" in str(pliki[x]): #pętla sprawdzająca czy plik w nazwie zawiera txt (rowniez txt w nazwie wyswietli np. txt.doc)
            pliki_txt = pliki_txt + pliki[x] + ", "
    
    while 1:        # obsługa wyjątku: sprawdza czy user podaje istniejącą nazwę pliku, jesli nie wymusza poprawkę - do skutku
        try:
            komunikat = "Podaj nazwę zestawu walorow (*.txt), spośród " + pliki_txt + "(bez rozszerzenia): "
            nazwa_pliku = input(komunikat) #tu user wprowadza nazwę (wybiera plik do importu)
                
            import codecs # import modułu codecs, z ktorego funkcja open pozwala wybrać kodowanie
            plik = codecs.open (sciezka + "\\" + nazwa_pliku + ".txt",encoding="utf-8") #otwarcie wskazanego pliku

            break
        except FileNotFoundError:
            print("Podany plik nie istnieje.")
        
    
    tresc_pliku = plik.readlines() #wczytanie pliku liniami (każda linijka to kolejny element listy)
    
    plik.close()
    
    wybrany_zestaw = []
    for i in range(len(tresc_pliku)):# pętla z liczbą powtorzeń rowną liczbie wierszy w pliku, rozdziela kolejne wiersze wg separatora
        kolejny_wiersz = tresc_pliku[i].split(',')  # podział wiersza wg separatora na listę
        kolejny_wiersz[1] = float(kolejny_wiersz[1])    # zamiana wspołrzednych z str a float
        kolejny_wiersz[2] = float(kolejny_wiersz[2])    # jw
        ### !!!! - poniższe 2 linijki muszą być warunkowe (jesli plik ma te kolumny)
        if len(kolejny_wiersz) < 4: 
            kolejny_wiersz = kolejny_wiersz + [i, 5] # dodanie 2 pol: id i pola, ktore będzie wagą w losowaniu
        else:
            kolejny_wiersz[3] = int(kolejny_wiersz[3])  
            kolejny_wiersz[4] = int(kolejny_wiersz[4])
        wybrany_zestaw.append(kolejny_wiersz) #dodawanie kolejnych wierszy do wybranego zestawu
            
    return wybrany_zestaw
#%%
def zapis_do_pliku (dane):
    """
    Funkcja zapisująca do pliku wyniki uczenia się - w ostatniej kolumnie im większa liczba tym gorzej opanowany materiał i częsciej będzie losowany
    Zapisuje w kodowaniu uft-8
    !!!! wprowadzić ewentualnie wpisywanie daty do nazwy
    !!!! czy dodać opcję wyjscia bez zapisywania wynikow?
     
    """
    import os
   
    sciezka = (os.getcwd()) # sprawdzenie w jakim katalogu się znajdujemy (katalog bieżący)
    
    nazwa_pliku_out = input("Podaj nazwę pliku do zapisu wynikow, bez rozszerzenia *.txt: ")
    
    czy_istnieje = os.path.isfile(sciezka + "\\" + nazwa_pliku_out + ".txt")
        
    ### pętla i warunki do weryfikacji czy nie nadpisuje pliku (ew. swiadomego nadpisania)
    if (czy_istnieje == True):
        czy_petla = "t"
    else: czy_petla = "n"
    
    while czy_petla == "t":
        czy_nadpisac = input("Plik o podanej nazwie istnieje. Czy nadpisać? t/n: ")
        if czy_nadpisac != "t":
            nazwa_pliku_out = input("Podaj INNĄ nazwę pliku do zapisu wynikow, bez rozszerzenia *.txt: ")
        else: czy_petla = "n"

    print("Plik wybrany do zapisu: " + sciezka + "\\" + nazwa_pliku_out + ".txt")
    ### kod otwierający plik       
    import codecs 
    plik = codecs.open(sciezka + "\\" + nazwa_pliku_out + ".txt", 'w',encoding="utf-8") # - w oznacza, że będzie zapisywany plik (ewentualny istniejący zostanie nadpisany)
    
    
    for i in range(len(dane)-1): #pętla powtarza dla liczby wierszy minus 1 (bo ostatni ma być bez \n)
        wiersz = ""
        for j in range(len(dane[i])-1): #pętla powtarza dla liczby kolumn pomniejszonej o 1
            wiersz += str(dane[i][j])+"," #zapis kolumn bez ostatniej i dodanie separatora (przecinka)
            
        plik.write(str(wiersz)+str(dane[i][len(dane[i])-1])+"\n") #zapis w pliku wiersza (po + ostatnia kolumna bez przecinka, dalej \n - złamanie linii)
    
    # zapis ostatniego wiersza (osobno, bo bez \n na końcu)
    wiersz = ""
    for j in range(len(dane[i])): #pętla powtarza dla liczby kolumn itego wiersza
        wiersz = wiersz + str(dane[i+1][j])+"," 
        
    plik.write(str(wiersz)+str(dane[i+1][len(dane[i])-1])) 
    
    plik.close()
    print("Twoje wyniki zostały zapisane w pliku: " + sciezka + "\\" + nazwa_pliku_out + ".txt")

#%%
#def pyt_odp(zestaw):
    """
    JUŻ NIEPOTRZEBNA
    Funkcja przeprowadzająca losowanie z listy (zestaw), odpytująca, sprawdzająca i przyznająca punkty
    W wersji programu z losowaniem wg zmieniających się w miarę odpowiadania wag funkcja ta będzie niepotrzebna
    #(old_ver)
    """
"""    
    # 2 Losowanie elementu
    #zmienna (walor) to numer waloru na liscie walory_zestaw
    import random
    walor=(random.randint(0,len(zestaw)-1)) # -1 bo numeracja na liscie od 0
    
    # 3 Zadanie pytania i pobranie odpowiedzi urzytkownika (xUser i yUser)
    print("Wskaż gdzie znajduje się ",zestaw[walor][0])
    xUser = input ("Szerokość geograficzna (np. 52.1):")
    yUser = input ("Długość geograficzna (np. 19.5):")
       
           
    # 4 Weryfikacja poprawności udzielonej odpowiedzi
    # [1] i [2] to pozycje wspolrzednych na liscie walory_zestaw
    # konieczna jest zamiana str na float
    import math
    odleglosc = math.sqrt((float(xUser)-float(zestaw[walor][1]))**2+(float(yUser)-float(zestaw[walor][2]))**2) 
    punkty = 10 - odleglosc//1
    
    # 5 Zwrócenie informacji 
    print("Poprawna lokalizacja to ",zestaw[walor][1]," ",zestaw[walor][2])
    print("Błąd wyniósł ",odleglosc)
    print("Zdobyte punkty ",punkty)
    
    return punkty
"""
#%%
def pyt_odp_wagi(zestaw,walor):
    """
    Funkcja podobna do pyt_odp, ale bez losowania. Korzysta z wyniku losowania uwzględniającego wagi.
    Być może na podstawie odpowiedzi te wagi modyfikująca (??? Czy funkcja może zwracać więcej niż 1 parametr?)
    """
    # 3 Zadanie pytania i pobranie odpowiedzi urzytkownika (xUser i yUser)
    print("Wskaż gdzie znajduje się ",zestaw[walor][0])
    while 1:
        try: #obsługa wyjątku
            xUser = float(input ("Szerokość geograficzna (np. 52.1):"))
            yUser = float(input ("Długość geograficzna (np. 19.5):"))
            break
        except ValueError: #obsługuje tylko błąd typu valueError
            print("Wprowadzone dane są w niewłasciwym formacie")
                
    # 4 Weryfikacja poprawności udzielonej odpowiedzi
    # [1] i [2] to pozycje wspolrzednych na liscie walory_zestaw
    # konieczna jest zamiana str na float
    import math
    odleglosc = math.sqrt(((xUser)-float(zestaw[walor][1]))**2+((yUser)-float(zestaw[walor][2]))**2) # obliczona odległoć w stopnaich jakby to była płaszczyzna
    punkty = 10 - odleglosc//1
    
    ### obliczenie ortodromy - odległosci sferycznej
    L1 = math.radians(float(zestaw[walor][2])) # przeliczenie wartosci w stopniach na radiany - rzeczywista lokalizacja
    F1 = math.radians(float(zestaw[walor][1]))
    L2 = math.radians(yUser) # przeliczenie wartosci w stopniach na radiany - wskazana przez Usera
    F2 = math.radians(xUser)

    ortodr_rad = 2 * math.asin ( math.sqrt( math.sin((F1-F2)/2)**2 + math.cos(F1)*math.cos(F1)* math.sin((L1-L2)/2)**2 ))
    ortodr_deg = math.degrees(ortodr_rad)
    dst = ortodr_deg*111.195
    print("Pomyliłes się o ",int(dst)," km") # zaokrągla w doł do całkowitej

    
    # 5 Zwrócenie informacji 
    print("Poprawna lokalizacja to ",zestaw[walor][1]," ",zestaw[walor][2])
    print("Błąd wyniósł ",odleglosc)
    print("Zdobyte punkty ",punkty)
    
    return punkty

#%%
# KOD PROGRAMU

walory_zestaw = import_zestawu() # wywołanie funkcji wybierającej i konwertującej zestaw pytań

### Komunikat testowy - do weryfikacji poprawnosci importu i dalszego testowania
print("Komunikat testowy: Zaimportowany zestaw to ",walory_zestaw)


### zdefiniowanie zmiennych zliczających punkty, pytania
czy_powt = "t" #parametr przerywajacy zadawanie kolejnych pytań
suma_pkt = 0 # zmienna przechowująca sumę zdobytych punktow
k = 0 # zmienna zliczająca zadane pytania

while czy_powt != "n":    # zapętlenie zadawania pytań (!!! można dodać limit czasu na odpowiedź)
    k += 1
    print("Pytanie ",k)

    # konstruowanie zestawu do losowania - co pytanie nieco inny - uwzględniający uzyskane wyniki
    zestaw_do_los = [] # zmienna do losowania - tak aby zwiększyć prawdopodobieństwo wylosowania wierszy, ktroe maja większą wartosć w 4 kolumnie
    for i in range(len(walory_zestaw)):
        for j in range(int(walory_zestaw[i][4])):
            zestaw_do_los.append(walory_zestaw[i])
    ### Komunikat testowy - do weryfikacji poprawnosci importu i dalszego testowania
    print("Komunikat testowy: Zestaw do losowania to ",zestaw_do_los)


    # losowanie obiektu z listy do losowania (z powielonymi walorami) i zwrcenie id obiektu (z kolumny 3)
    import random
    id_walor = zestaw_do_los[(random.randint(0,len(zestaw_do_los)-1))][3] 
    print("id wybranego waloru to ",id_walor)

    punkty_za_pytanie = pyt_odp_wagi(walory_zestaw,id_walor) ## wywołanie funkcji odpytującej i zliczanie punktow - w wariancie z wagami
    
    walory_zestaw[id_walor][4] = int((walory_zestaw[id_walor][4]+(10-punkty_za_pytanie))/2)### modyfikacja wagi do losowania - wymaga dokończenia
    suma_pkt += punkty_za_pytanie 
    print("Razem punktów: ",suma_pkt, "Średnio punktów: ",suma_pkt/k)
    czy_powt = input("Czy kolejne pytanie (t/n)?")

### zapisanie wynikow (a zarazem nowego zestawu do losowania do pliku)
zapis_do_pliku (walory_zestaw)
