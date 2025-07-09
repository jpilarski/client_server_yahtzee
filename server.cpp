#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/types.h>
#include <fcntl.h>
#include <ctime>
#include <cstdlib>
#include <sys/epoll.h>
#include <iostream>
#include <string.h>
#include <unistd.h>
#include <vector>
#include <thread>
#include <chrono>

using namespace std;

struct game // Struktura przechowująca informacje o grze
{
    int player_0, player_1;
    int result[14][2];
    int sum_0, sum_1;
    int current_player;
    int round;
    bool bonus_0, bonus_1;
};

void setnonblock(int fd) // Ustawienie nieblokujących operacji wejścia/wyjścia
{
    int flags = fcntl(fd, F_GETFL, 0);
    fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

int main(int argcounter, char* argtab[])
{
    if(argcounter != 2) // Weryfikacja poprawności uruchomienia programu
    {
        cout << "Usage: ./serwer <port>" << endl;
        return 1;
    }

    int port = atoi(argtab[1]); // Inicjalizacja zmiennych do komunikacji klient-serwer
    int server_fd, client_fd, epoll_fd, number_fd, on = 1;
    sockaddr_in server_addr, client_addr;
    epoll_event event, events[32];
    socklen_t sl = sizeof(client_addr);

    memset(&server_addr, 0, sizeof(server_addr)); // Konfiguracja struktury adresu serwera
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);

    server_fd = socket(AF_INET, SOCK_STREAM, 0); // Konfiguracja gniazda serwera
    setnonblock(server_fd);
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, (char*)&on, sizeof(on));
    bind(server_fd, (sockaddr*)&server_addr, sizeof(server_addr));
    listen(server_fd, 10);

    epoll_fd = epoll_create1(0); // Konfiguracja mechanizmu epoll
    event.events = EPOLLIN;
    event.data.fd = server_fd;
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, server_fd, &event);

    vector <int> players(16); // Inicjalizacja zmiennych do gier
    int max_player = 15;
    int waiting_player = 0;
    vector <game> games;
    game newgame;
    games.push_back(newgame);
    char buffer[512];
    int received_bytes;

    while(1)
    {
        number_fd = epoll_wait(epoll_fd, events, 32, -1);
        for(int i = 0; i < number_fd; i++)
        {
            if(events[i].data.fd == server_fd)
            {
                client_fd = accept(server_fd, (sockaddr*)&client_addr, &sl); // Przyjmowanie nowych klientów
                setnonblock(client_fd);
                if(client_fd > max_player)
                {
                    players.resize(client_fd + 5);
                    max_player += 5;
                }
                if(waiting_player == 0) waiting_player = client_fd; // Łączenie graczy w pary i wysyłanie komunikatów 
                else                                                // o rozpoczęciu gry
                {
                    memset(&newgame, 0, sizeof(newgame));
                    newgame.player_0 = waiting_player;
                    newgame.player_1 = client_fd;
                    newgame.current_player = waiting_player;
                    games.push_back(newgame);
                    players[waiting_player] = games.size() - 1;
                    players[client_fd] = games.size() - 1;
                    waiting_player = 0;
                    write(newgame.player_0, "START\n", 6);
                    write(newgame.player_1, "STOP\n", 5);
                    this_thread::sleep_for(chrono::milliseconds(500));
                }
                event.events = EPOLLIN; // Dodanie gniazda klienta do mechanizmu epoll
                event.data.fd = client_fd;
                epoll_ctl(epoll_fd, EPOLL_CTL_ADD, client_fd, &event); 
            }
            else
            {
                int player_playing, player_rival, my_game; // Ustalenie indeksu gry i graczy
                player_playing = events[i].data.fd;
                my_game = players[player_playing];
                player_rival = games[my_game].player_0;
                if(player_playing == player_rival) player_rival = games[my_game].player_1;

                memset(&buffer, 0, sizeof(buffer));
                received_bytes = read(player_playing, buffer, sizeof(buffer)); // Odebranie wiadomości

                if(received_bytes <= 0) // Obsługa błędu lub zakończenia komunikacji
                {
                    epoll_ctl(epoll_fd, EPOLL_CTL_DEL, player_playing, NULL);
                    close(player_playing);
                    players[player_playing] = 0;
                    if(my_game != 0)
                    {
                        write(player_rival, "DISCC\n", 6);
                        epoll_ctl(epoll_fd, EPOLL_CTL_DEL, player_rival, NULL);
                        close(player_rival);
                        players[player_rival] = 0;
                    }
                }

                if(player_playing != games[my_game].current_player) continue; // Ignorowanie wiadomości niepochodzących
                                                                              // od gracza wykonującego ruch
                if(received_bytes == 5) // Odebranie informacji o sekwencji kości i przesłanie jej rywalowi
                {
                    buffer[5] = '\n';
                    write(player_rival, buffer, 6);
                    this_thread::sleep_for(chrono::milliseconds(500));
                }

                if(received_bytes < 5 && received_bytes > 0) // Odebranie komunikatu o wybraniu jednej z kategorii
                {
                    int choosed;
                    switch(buffer[0]) // Określenie wybranej kategorii
                    {
                        case 'A': choosed = 1; break;
                        case 'B': choosed = 2; break;
                        case 'C': choosed = 3; break;
                        case 'D': choosed = 4; break;
                        case 'E': choosed = 5; break;
                        case 'F': choosed = 6; break;
                        case 'G': choosed = 7; break;
                        case 'H': choosed = 8; break;
                        case 'I': choosed = 9; break;
                        case 'J': choosed = 10; break;
                        case 'K': choosed = 11; break;
                        case 'L': choosed = 12; break;
                        case 'M': choosed = 13; break;
                        default: break;
                    }
                    int score = atoi(buffer + 1); // Określenie liczby zdobytych punktów
                    if(player_playing == games[my_game].player_0) // Zapisanie wyniku w przypadku ruchu gracza rozpoczynającego
                    {
                        games[my_game].result[choosed][0] = score;
                        buffer[received_bytes] = '\n';
                        write(player_rival, buffer, received_bytes+1); // Przesłanie informacji o wyniku do rywala
                        this_thread::sleep_for(chrono::milliseconds(500));
                        if(!games[my_game].bonus_0) // Weryfikacja, czy zaistniał bonus
                        {
                            int s_b = 0;
                            for(int b = 1; b <= 6; b++) s_b += games[my_game].result[b][0];
                            if(s_b >= 63)
                            {
                                write(player_rival, "BONUS\n", 6);
                                this_thread::sleep_for(chrono::milliseconds(500));
                                games[my_game].bonus_0 = 1;
                                games[my_game].result[0][0] = 35;
                            }
                        }
                    }
                    else // Zapisanie wyniku w przypadku ruchu gracza numer 2
                    {
                        games[my_game].result[choosed][1] = score;
                        buffer[received_bytes] = '\n';
                        write(player_rival, buffer, received_bytes+1);
                        this_thread::sleep_for(chrono::milliseconds(500));
                        if(!games[my_game].bonus_1)
                        {
                            int s_b = 0;
                            for(int b = 1; b <= 6; b++) s_b += games[my_game].result[b][1];
                            if(s_b >= 63)
                            {
                                write(player_rival, "BONUS\n", 6);
                                this_thread::sleep_for(chrono::milliseconds(500));
                                games[my_game].bonus_1 = 1;
                                games[my_game].result[0][1] = 35;
                            }
                        }
                    }
                    write(player_playing, "STOP\n", 5); // Zablokowanie ruchów dla gracza grającego
                    this_thread::sleep_for(chrono::milliseconds(500));
                    games[my_game].round += 1;
                    if(games[my_game].round == 26) // Sprawdzenie, czy nie zakończyła się gra
                    {
                        for(int s = 0; s < 14; s++) // Obliczenie zdobytych punktów
                        {
                            games[my_game].sum_0 += games[my_game].result[s][0];
                            games[my_game].sum_1 += games[my_game].result[s][1];
                        }
                        if(games[my_game].sum_0 == games[my_game].sum_1) // Nadanie informacji o rozstrzygnięciu
                        {
                            write(player_playing, "DRAW\n", 5);
                            write(player_rival, "DRAW\n", 5);
                        }
                        else if(games[my_game].sum_0 > games[my_game].sum_1)
                        {
                            write(games[my_game].player_0, "WIN\n", 4);
                            write(games[my_game].player_1, "LOSE\n", 5);
                        }
                        else
                        {
                            write(games[my_game].player_0, "LOSE\n", 4);
                            write(games[my_game].player_1, "WIN\n", 5);
                        }
                        this_thread::sleep_for(chrono::milliseconds(500)); // Zakończenie połączeń
                        epoll_ctl(epoll_fd, EPOLL_CTL_DEL, player_playing, NULL);
                        close(player_playing);
                        players[player_playing] = 0;
                        epoll_ctl(epoll_fd, EPOLL_CTL_DEL, player_rival, NULL);
                        close(player_rival);
                        players[player_rival] = 0;
                    }
                    games[my_game].current_player = player_rival; // Jeśli gra toczy się dalej zmiana gracza grającego
                    write(player_rival, "START\n", 6);
                    this_thread::sleep_for(chrono::milliseconds(500)); // Odblokowanie ruchów dla nowego grającego
                } 
            }
        }
    }
}