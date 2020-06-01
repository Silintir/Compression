LISTA 3:

Rozwiązaniem zadania z listy 3 są dwa pliki 'lzw_encode.py' oraz 'lzw_decode.py'. Jest to zadanie na ocenę 5. Do jego uruchomienia wymagany
jest python 3.7.

Programy uruchamia się następująco:
    do kompresji pliku:
        lzw_encode <input_file> <output_file> [args..]
        args:
        -gamma - wariant kodowania gamma
        -delta - wariant kodowania delta
        -fibbo - kodowanie fibbonaciego
    do dekompresji pliku:
        lzw_decode <input_file> <output_file> [args..]
        args:
        -gamma - wariant kodowania gamma
        -delta - wariant kodowania delta
        -fibbo - kodowanie fibbonaciego    
        przy czym rodzaj kodowania musi być zgodny z rodzajem w którym plik został zakodowany