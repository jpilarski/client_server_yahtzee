import tkinter as tk
import threading
import socket
import random
import sys

host = 0 # Adres serwera i numer portu
port = 0

class YahtzeeGUI(tk.Tk): # Główna klasa programu - GUI
    def __init__(self):
        super().__init__() # Konstruktor klasy

        self.title("Yahtzee") # Tytuł i rozmiar okna
        self.geometry("600x500")

        self.state = False # Wszystkie zmienne do sterowania pracą i wyświetlania danych w GUI
        self.used_buttons = set()
        self.dice_values = []
        self.dice_checks = []
        self.val_labels = []
        self.etiq = ["Ones", "Twos", "Threes", "Fours", "Fives",
                     "Sixes", "3 of kind", "4 of kind", "Full house",
                     "Small straight", "Large straight", "Chance", "Yahtzee"]
        self.table = []
        self.turns = 0
        self.bonus_sum = 0
        self.running = True

        left_frame = tk.Frame(self) # Lewa część okienka, na kości
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        for i in range(5):
            frame = tk.Frame(left_frame)
            frame.pack(fill=tk.X, pady=5)

            var = tk.IntVar() # Checkbox do zaznaczania wybranych kości
            check = tk.Checkbutton(frame, variable=var)
            check.pack(side=tk.LEFT)

            value_label = tk.Label(frame, text=0, width=5, relief=tk.SUNKEN) # Etykieta z wartością kości
            value_label.pack(side=tk.LEFT, padx=5)

            self.dice_values.append(value_label)
            self.dice_checks.append(var)

        right_frame = tk.Frame(self) # Prawa część okienka, na tabelę z wynikami
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        headers = ["", "Gracz", "Przeciwnik"] # Nagłówki tabeli
        for col, text in enumerate(headers):
            label = tk.Label(right_frame, text=text, width=15, borderwidth=2, relief=tk.RIDGE)
            label.grid(row=0, column=col)

        bonus_label = tk.Label(right_frame, text="Bonus", width=10, borderwidth=2, relief=tk.RIDGE) # Pierwszy wiersz, na bonus
        bonus_label.grid(row=1, column=0)

        val1 = tk.Label(right_frame, text="", width=15, borderwidth=2, relief=tk.SUNKEN)
        val1.grid(row=1, column=1)
        val2 = tk.Label(right_frame, text="", width=15, borderwidth=2, relief=tk.SUNKEN)
        val2.grid(row=1, column=2)
        self.val_labels.append((val1, val2))

        for i in range(2, 15): # 13 wierszy na przycisk i dwie wartości punktowe
            btn = tk.Button(right_frame, text=self.etiq[i-2], width=10, command=lambda i=i: self.send_button_message(i))
            btn.grid(row=i, column=0)
            self.table.append(btn)
            val1 = tk.Label(right_frame, text="", width=15, borderwidth=2, relief=tk.SUNKEN)
            val1.grid(row=i, column=1)
            val2 = tk.Label(right_frame, text="", width=15, borderwidth=2, relief=tk.SUNKEN)
            val2.grid(row=i, column=2)
            self.val_labels.append((val1, val2))

        self.roll_button = tk.Button(self, text="Losuj", font=("Arial", 16), width=10, command=self.roll) # Przycisk do losowania
        self.roll_button.pack(side=tk.BOTTOM, pady=20)

        self.result_label = tk.Label(self, text="", width=15, relief=tk.SUNKEN) # Etykieta do wyświetlenia wyniku
        self.result_label.pack(side=tk.BOTTOM, pady=5)

        self.start_message_thread() # Inicjalizacja wątku do odbierania wiadomości
        self.update_buttons()

    def roll(self): # Funkcja losująca
        rolled_values = []
        self.turns += 1
        for i, value_label in enumerate(self.dice_values): # Funkcja nadaje nowe wartości tylko tym kościom
            if self.dice_checks[i].get() == 0:             # które nie mają zaznaczonego checkboxa
                new_value = str(random.randint(1, 6))
                value_label.config(text=new_value)
                rolled_values.append(new_value)
            else:
                rolled_values.append(value_label.cget("text"))

        rolled_message = "".join(rolled_values) # Zapisanie sekwencji kości do wysłania
        self.send_message_to_server(rolled_message)
        self.update_buttons()

    def send_button_message(self, index): # Funkcja weryfikuje który z przycisków od kategorii został wciśnięty
        if 2 <= index <= 7:               # Na podstawie aktualnych wartości kości wyznacza liczbę punktów i generuje wiadomość
            target_value = index - 1
            count = sum(1 for label in self.dice_values if label.cget("text") == str(target_value))
            message = chr(63 + index) + str(count * target_value)
            self.bonus_sum = count * target_value + self.bonus_sum
        elif index == 8:
            counts = {}
            for label in self.dice_values:
                value = label.cget("text")
                counts[value] = counts.get(value, 0) + 1
            if any(count >= 3 for count in counts.values()):
                message = "G" + str(sum(int(label.cget("text")) for label in self.dice_values))
            else:
                message = "G0"
        elif index == 9:
            counts = {}
            for label in self.dice_values:
                value = label.cget("text")
                counts[value] = counts.get(value, 0) + 1
            if any(count >= 4 for count in counts.values()):
                message = "H" + str(sum(int(label.cget("text")) for label in self.dice_values))
            else:
                message = "H0"
        elif index == 10:
            counts = {}
            for label in self.dice_values:
                value = label.cget("text")
                counts[value] = counts.get(value, 0) + 1
            if any(count == 3 for count in counts.values()) and any(count == 2 for count in counts.values()):
                message = "I25"
            else:
                message = "I0"
        elif index == 11:
            values = [int(label.cget("text")) for label in self.dice_values]
            unique_values = sorted(set(values))
            if any(all(num in unique_values for num in range(start, start + 4)) for start in range(1, 4)):
                message = "J30"
            else:
                message = "J0"
        elif index == 12:
            values = sorted(int(label.cget("text")) for label in self.dice_values)
            if (values[0] == 1 and values[1] == 2 and values[2] == 3 and values[3] == 4 and values[4] == 5) or \
               (values[0] == 2 and values[1] == 3 and values[2] == 4 and values[3] == 5 and values[4] == 6):
                message = "K40"
            else:
                message = "K0"
        elif index == 13:
            total_sum = sum(int(label.cget("text")) for label in self.dice_values)
            message = "L" + str(total_sum)
        elif index == 14:
            if all(label.cget("text") == self.dice_values[0].cget("text") for label in self.dice_values):
                message = "M50"
            else:
                message = "M0"
        self.send_message_to_server(message) # Wysłanie wiadomości
        self.used_buttons.add(index) # Zaznaczenie przycisku jako użytego
        numeric_value = int(message[1:]) if message[1:].isdigit() else 0 # Zapisanie zdobytej liczby punktó
        self.val_labels[index-1][0].config(text=str(numeric_value))      # w tabelce
        if self.bonus_sum >= 63: # Zapisanie w tabeli informacji o bonusie
            self.val_labels[0][0].config(text="35")

    def start_message_thread(self): # Uruchomienie wątku ze wskazaniem funkcji którą ma wykonywać
        self.thread = threading.Thread(target=self.receive_messages)
        self.thread.daemon = True # Wątek zakończy się wraz z głównym programem
        self.thread.start()

    def receive_messages(self): # Funkcja do odbierania wiadomości
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Konfiguracja połączenia z serwerem
        self.s.connect((host, port))
        while self.running: # Wątek działa, gdy flaga jest ustawiona
            data = self.s.recv(1024) # Odebranie komunikatu
            if not data:
                break
            message = data.decode('utf-8')
            print("Odebrana wiadomość:", message)
            if message.startswith('START'): # Przekazanie sterowania temu graczowi
                self.turns = 0
                self.state = True
                for value_label in self.dice_values: # Zresetowanie kości i checkboxów
                    value_label.config(text="0")
                for check in self.dice_checks:
                    check.set(0)
            elif message.startswith('STOP'): # Zablokowanie sterowania
                self.state = False
            elif message.startswith('BONUS'): # Dodanie bonusu przeciwnikowi w tabeli
                self.val_labels[0][1].config(text="35")
            elif message.startswith('DISCC'): # Informacja o rozłączeniu
                self.result_label.config(text="Opponent\ndisconnected")
                self.state = False
                self.s.close() # Zamknięcie gniazda i zakończenie wątku
                self.running = False 
            elif message.startswith('WIN'): # Informacja o wygranej
                self.result_label.config(text="You win")
                self.state = False
                self.s.close()
                self.running = False
            elif message.startswith('LOSE'): # Informacja o przegranej
                self.result_label.config(text="You lose")
                self.state = False
                self.s.close()
                self.running = False
            elif message.startswith('DRAW'): # Informacja o remisie
                self.result_label.config(text="Draw")
                self.state = False
                self.s.close()
                self.running = False
            elif message[0].isdigit(): # Odebranie i aktualizacja kości (podgląd ruchów przeciwnika)
                for i, char in enumerate(message[:5]):
                    self.dice_values[i].config(text=char)
            elif message[0].isalpha() and message[0] in 'ABCDEFGHIJKLM': # Odebranie komunikatu o wyniku konkretnej
                letter_index = ord(message[0]) - 64                      # kategoii przeciwnika
                numeric_value = int(message[1:])
                self.val_labels[letter_index][1].config(text=str(numeric_value))  
            self.update_buttons()


    def send_message_to_server(self, message): # Funkcja do wysyłania komunikatów do serwera
        if self.s:
            self.s.sendall(message.encode('utf-8'))

    def update_buttons(self): # Aktualizacja dostępności przycisków do kliknięcia
        any_zero = any(label.cget("text") == "0" for label in self.dice_values) # Klient nie wykonujący ruchu nie może
        if self.state:                                                          # wcisnąć żadnego przycisku
            state = tk.DISABLED if any_zero else tk.NORMAL                      # Klient wykonujący ruch może wcisnąć
        else:                                                                   # na początku tylko przycisk do rzucania
            state = tk.DISABLED                                                 # Po 3 rzutach można wybrać tylko jedną
        for i, btn in enumerate(self.table, start=2):                           # z dostępnych jeszcze kategorii
            if i not in self.used_buttons:
                btn.config(state=state)                                         # Funkcja ta jest wywoływana po każdej zmianie stanu gry
            else:
                btn.config(state=tk.DISABLED)
        if self.state:
            self.roll_button.config(state=tk.NORMAL)
        else:
            self.roll_button.config(state=tk.DISABLED)
        if self.turns >= 3:
            self.roll_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    if len(sys.argv) != 3: # Weryfikacja poprawności argumentów
        print("Użycie: python klient.py <adres_ip> <port>")
        sys.exit(1)
    host = sys.argv[1]
    port = int(sys.argv[2])
    app = YahtzeeGUI() # Uruchomienie głównej klasy
    app.mainloop()
