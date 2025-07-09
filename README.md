# 🌐🎲 Network Yahtzee

## ℹ️ O projekcie

#### [🇬🇧 English version](#ℹ️-about-the-project)

Projekt powstał na przedmiocie `Sieci komputerowe 2`, na V semestrze studiów pierwszego stopnia na kierunku Informatyka na Politechnice Poznańskiej.

### ⚙️ Działanie aplikacji

* Aplikacja pozwala na współbieżną, wieloosobową rozgrywkę w Yahtzee (gra jest dwuosobowa, ale można toczyć kilka gier równocześnie).
* Zastosowano protokół komunikacyjny TCP.
* Współbieżność zapewniono multipleksacją wejścia-wyjścia z użyciem mechanizmu systemowego epoll.

#### 🖥️ Działanie serwera:

* Serwer akceptuje nowe połączenia od klientów,
* łączy klientów w pary zgodnie z kolejnością dołączania,
* wysyła komunikaty kontrolujące, który z graczy wykonuje obecnie ruch,
* zbiera informacje od gracza rzucającego kośćmi, aby przeciwnik widział na bieżąco jakie ruchy wykonuje rzucający,
* po dokonaniu wyboru przez gracza aktualizuje wyniki w swojej strukturze, przekazuje do rywala informację o punktach i zmienia gracza rzucającego,
* po zakończeniu rozgrywki podlicza punkty i wysyła do graczy informację o rezultacie,
* serwer bezpiecznie kończy rozgrywki rozłączając klientów w przypadku rezygnacji jednego z nich lub w przypadku zakończenia graczy.

#### 👤 Działanie klienta:

* Klient tworzy klasę `YahtzeeGUI` bazującą na bibliotece tkinter,
* ustala layout aplikacji tworząc pola do rzucania koścmi, tabelkę z wynikami i potrzebne przyciski,
* nawiązuje połączenie z serwerem,
* tworzy osobny wątek do odbierania komunikatów od serwera,
* blokuje wykonywanie ruchów przez nieaktywnego gracza,
* pozwala wykonywać ruchy grającemu zgodne z zasadami graczy,
* wysyła komunikaty na temat wyborów gracza,
* na podstawie odebranych komunikatów aktualizuje wyniki, aktualnego gracza i kości rywala,
* pilnuje zasad gry uniemożliwiając wielokrotne wybranie jednej kategorii i przeliczając punkty,
* informuje użytkownika o wyniku rozgrywki bądź o rozłączeniu i zamyka połączenie.

### 🚀 Uruchomienie aplikacji

1. Na Linuxie skompiluj serwer: `> g++ -Wall -o server server.cpp`.
2. Uruchom serwer, podając numer portu (>1024): `> ./server <nr portu>`.
3. Uruchom klienta, podając adres IP serwera, oraz ten san numer portu: `> python client.py <adres IP> <nr portu>` (Windows) lub `> python3 client.py <adres IP> <nr portu>` (Linux).
4. Do gry potrzebne jest uruchomienie przynajmniej dwóch klientów. Interfejs graficzny pokazuje dostępne opcje w grze.

## ℹ️ About the project

#### [🇵🇱 Wersja polska](#ℹ️-o-projekcie)

The project was created for the `Computer networks 2` course during the 5th semester of the Bachelor's degree in Computer Science at Poznan University of Technology.

### ⚙️ Application overview

* The application enables concurrent, multiplayer Yahtzee games (each game is two-player, but multiple games can run simultaneously).
* TCP is used as the communication protocol.
* Concurrency is achieved through I/O multiplexing using the epoll system mechanism.

#### 🖥️ Server operation:

* The server accepts new client connections,
* pairs clients in the order they connect,
* sends control messages to determine which player can make a move,
* receives dice roll data from the active player so the opponent can see actions in real time,
* updates internal game state after a move, informs the opponent of the updated score, and switches the active player,
* calculates final scores and sends results to both players at the end of a game,
* safely ends games and disconnects clients when one resigns or when the game concludes.

#### 👤 Client operation:

* The client creates a YahtzeeGUI class based on the tkinter library,
* sets up the application layout with dice fields, score table, and necessary buttons,
* connects to the server,
* starts a separate thread to receive messages from the server,
* blocks actions for the inactive player,
* enables valid moves for the active player according to game rules,
* sends messages about player choices,
* updates scores, active player, and opponent’s dice based on received messages,
* enforces game rules by preventing category reuse and recalculating points,
* informs the user of the result or disconnection, and closes the connection.

### 🚀 Running the application

1. On Linux, compile the server: `> g++ -Wall -o server server.cpp`.
2. Run the server with a port number (>1024): `> ./server <port>`.
3. Run the client with the server's IP address and same port: `> python client.py <IP address> <port>` (Windows) or `> python3 client.py <IP address> <port> (Linux)`.
4. At least two clients must be launched to start a game. The GUI displays available options during the game.