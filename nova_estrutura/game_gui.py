import random
from game_manager import GameManager
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk

class Config_Screen:
    def __init__(self,root):
        self.root = root
        self.root.title("Dominó em Python Por: Milton Braghetto Jr.")
        self.root.geometry("1000x700")
        self.mainframe = Frame(root, bg='green')
        self.mainframe.place(x=0,y=0,relwidth=1,relheight=1)
        self.mainframe.columnconfigure((0,1,2), weight=1)
        self.mainframe.rowconfigure((0,1,2), weight=1)
        self.initialize()
        
    def jogar_button(self):
        try:                        
            self.human_player_name = self.human_name.get()
            self.number_of_players = int(self.number_players.get())
            print(f"Nome jogador: {self.human_player_name}")
            print(f"Número de jogadores:{self.number_of_players}")
            self.l1_frame.destroy()
            self.mainframe.destroy()
            print("Apertou o botão JOGAR")
            self.start_game_ui()
        except ValueError:
            pass

    def start_game_ui(self):
        GameUI(self.root,self.number_of_players,self.human_player_name)

    def initialize(self):
        self.l1_frame = Frame(self.mainframe)
        self.l1_frame.place(width=350,height=250,relx=0.5,rely=0.1,anchor='n')
        self.l1_frame.rowconfigure((0,1,2,3,4,5,6,7,8,9),weight=1)
        self.l1_frame.columnconfigure((0,1),weight=1)

        t1 = ttk.Label(self.l1_frame, text="Bem vindo ao Dominó!\n").grid(row=0,column=0,columnspan=2)
        t2 = ttk.Label(self.l1_frame, text="Seu nome:")             .grid(row=1,column=0,columnspan=2)

        self.human_name = StringVar(master=self.l1_frame)
        t3 = ttk.Entry(self.l1_frame,textvariable=self.human_name,takefocus=1)
        t3.grid(row=2,column=0,columnspan=2)
        t4 = ttk.Label(self.l1_frame, text="É possível jogar de 2 a 4 jogadores").grid(row=3,column=0,columnspan=2,pady=10)
        t5 = ttk.Label(self.l1_frame, text="Quantos jogadores nessa partida?").grid(row=4,column=0,columnspan=2,pady=5)

        self.number_players = StringVar(master=self.l1_frame)
        t5_2_players = ttk.Radiobutton(self.l1_frame, text='2', variable=self.number_players, value='2')
        t5_3_players = ttk.Radiobutton(self.l1_frame, text='3', variable=self.number_players, value='3')
        t5_4_players = ttk.Radiobutton(self.l1_frame, text='4', variable=self.number_players, value='4')
        t5_2_players.grid(row=5, column=0, columnspan=2,pady=5)
        t5_3_players.grid(row=6, column=0, columnspan=2,pady=5)
        t5_4_players.grid(row=7, column=0, columnspan=2,pady=5)
        b1 = ttk.Button(self.l1_frame,command=self.jogar_button,text="Jogar")
        b1.grid(row=8,column=0,columnspan=2,pady=10)

class GameUI:
    def __init__(self,root,num_players,human_player_name):
        self.root = root
        self.num_players = num_players
        self.human_player_name = human_player_name
        self.mainframe = Frame(root, bg='green')
        self.mainframe.place(x=0,y=0,relwidth=1,relheight=1)
        self.mainframe.columnconfigure((0,1,2), weight=1)
        self.mainframe.rowconfigure((0,1,2), weight=1)
        self.card_back_red_resize = Image.open("/Users/miltonbraghettojr/Documents/Python/Projetos/Domino_card_game/card_deck_imgs/card_back_red.png").resize((60,90))
        self.card_back_red = ImageTk.PhotoImage(self.card_back_red_resize)
        print("Preparando mesa...")
        self.setup_table()
        self.create_player_frame()
        self.create_opponent_frames()
        print("Iniciando jogo...")
        self.active_game = GameManager(num_players, human_player_name)
        self.display_player_hand()
        self.display_opponent_hand()
        
        self.game_loop()

    def __str__(self) -> str:
        return "GameUI"

    def update_table_pile(self, card):
        suit = card['suit']  # Exemplo: "ouros"
        points = card['points']
        pile = self.active_game.table_piles[suit] # Acessa a pilha correta para o naipe da carta
        pile.append(card)
        pile_values = [c['points'] for c in pile]
        # Determina a posição (top, mid, bot) na mesa com base nos pontos
        if points < 7:
            position = "bot"
        elif points == 7:
            position = "mid"
        else:
            position = "top"
        # Define a imagem no local adequado do monte
        img_path = card["image_path"]
        img = Image.open(img_path).resize((60, 90))
        img_photo = ImageTk.PhotoImage(img)

        # Atualiza a imagem correspondente na mesa
        pile_label = getattr(self, f"monte_{suit}_{position}")
        pile_label.configure(image=img_photo)
        pile_label.image = img_photo  # Mantém referência
        self.table_frame.update()

    def game_loop(self):
        self.current_player_index = 0
        self.run_turn()

    def run_turn(self):
        player = self.active_game.ordered_players[self.current_player_index]
        if player['name'] == self.human_player_name: #se for o jogador humano
            print(f"\n{player['name']}, é a sua vez!")
            cards_playable = sorted(self.active_game.check_plays(self.active_game.table_piles, player['hand']), key=lambda c: (c['suit'], c['points']))
            if cards_playable: #se há jogadas possíveis:
                print("Cartas jogáveis: " + ", ".join(card['card_short'] for card in cards_playable))
                print("Cartas queimadas: " + ", ".join(card['card_short'] for card in player['burned_pile']))
                for card in player['hand']: #para cada carta na mão do player
                    if card in cards_playable: # se é jogável
                        card_name = f"{card['points']}+{card['suit']}" #atribui o mesmo formato de nome da label
                        for widget in self.player_frame.winfo_children():
                            if widget.winfo_name() == card_name:
                                widget.bind('<ButtonPress-1>', lambda e, c=card: self.play_card(c,player)) #torna a carta clicável > ao clicar roda play_card
            else:
                print("Nenhuma jogada possível. Escolha uma carta para queimar")
                for card in player['hand']:
                    card_name = f"{card['points']}+{card['suit']}" #atribui o mesmo formato de nome da label
                    for widget in self.player_frame.winfo_children():
                        if widget.winfo_name() == card_name:
                            widget.bind('<ButtonPress-1>', lambda e, c=card: self.burn_card(c,player)) #torna a carta clicável > ao clicar roda burn_card
        else:
        #Cálculo de jogada do oponente
            cards_playable = sorted(self.active_game.check_plays(self.active_game.table_piles, player['hand']), key=lambda c: (c['suit'], c['points']))
            if cards_playable:
                card_to_play = random.choice(cards_playable)
                self.play_card(card_to_play,player)
            else:
                card_to_burn = random.choice(player['hand'])
                self.burn_card(card_to_burn,player)

    def next_turn(self):
            # Passa ao próximo jogador
        self.current_player_index = (self.current_player_index + 1) % len(self.active_game.ordered_players)
        if all(not player['hand'] for player in self.active_game.ordered_players):  # Se todos os jogadores ficaram sem cartas
            self.end_game()
        else:
            self.run_turn() 

    def play_card(self,card,player):
        player['hand'].remove(card)                      #remove carta da mão
        self.display_player_hand()                       #atualiza as imagens de cartas do player
        self.display_opponent_hand()                     #atualiza as imagens de cartas do oponente
        self.update_table_pile(card)                     #atualiza as imagens de cartas da mesa
        print(f"\n{player['name']} jogou {card['card_short']}")
        self.next_turn()

    def burn_card(self,card,player):
        player['hand'].remove(card)                     #remove carta da mão
        player['burned_pile'].append(card)              #adiciona à pilha de queima
        player['points'] += card['points']              #soma os pontos
        self.display_player_hand()                      #atualiza as imagens de cartas da mão
        self.display_opponent_hand()                    #atualiza as imagens de cartas do oponente
        print(f"\n{player['name']} queimou uma carta")
        self.next_turn()

    def setup_table(self):
        self.table_frame = Frame(self.mainframe,bd=1) 
        self.table_frame.place(relx=0.5,rely=0.5,anchor=CENTER)
        self.table_frame.columnconfigure((0,2,4,6,8), weight=1)
        self.table_frame.columnconfigure((1,3,5,7), weight=10)
        self.table_frame.rowconfigure((0,2,4,6), weight=1)
        self.table_frame.rowconfigure((1,3,5,7), weight=3)
        
        self.monte_ouros_top   = Label(self.table_frame,image=self.card_back_red, background='green', width=60,height=90)
        self.monte_ouros_top.grid(row=1,column=1,ipadx=10,ipady=10)
        self.monte_ouros_mid   = Label(self.table_frame,image=self.card_back_red, background='green', width=60,height=90)
        self.monte_ouros_mid.grid(row=3,column=1,ipadx=10,ipady=10)
        self.monte_ouros_bot   = Label(self.table_frame,image=self.card_back_red, background='green', width=60,height=90)
        self.monte_ouros_bot.grid(row=5,column=1,ipadx=10,ipady=10)

        self.monte_espadas_top = Label(self.table_frame,image=self.card_back_red, background='green', width=60,height=90)
        self.monte_espadas_top.grid(row=1,column=3,ipadx=10,ipady=10)
        self.monte_espadas_mid = Label(self.table_frame,image=self.card_back_red, background='green', width=60,height=90)
        self.monte_espadas_mid.grid(row=3,column=3,ipadx=10,ipady=10)
        self.monte_espadas_bot = Label(self.table_frame,image=self.card_back_red, background='green', width=60,height=90)
        self.monte_espadas_bot.grid(row=5,column=3,ipadx=10,ipady=10)

        self.monte_copas_top   = Label(self.table_frame,image=self.card_back_red, background='green', width=60,height=90)
        self.monte_copas_top.grid(row=1,column=5,ipadx=10,ipady=10)        
        self.monte_copas_mid   = Label(self.table_frame,image=self.card_back_red, background='green', width=60,height=90)
        self.monte_copas_mid.grid(row=3,column=5,ipadx=10,ipady=10)
        self.monte_copas_bot   = Label(self.table_frame,image=self.card_back_red, background='green', width=60,height=90)
        self.monte_copas_bot.grid(row=5,column=5,ipadx=10,ipady=10)
        
        self.monte_paus_top    = Label(self.table_frame,image=self.card_back_red, background='green', width=60,height=90)
        self.monte_paus_top.grid(row=1,column=7,ipadx=10,ipady=10)        
        self.monte_paus_mid    = Label(self.table_frame,image=self.card_back_red, background='green', width=60,height=90)
        self.monte_paus_mid.grid(row=3,column=7,ipadx=10,ipady=10)
        self.monte_paus_bot    = Label(self.table_frame,image=self.card_back_red, background='green', width=60,height=90)
        self.monte_paus_bot.grid(row=5,column=7,ipadx=10,ipady=10)

        self.monte_ouros_top.image = self.card_back_red
        self.monte_ouros_mid.image = self.card_back_red
        self.monte_ouros_bot.image = self.card_back_red
        self.monte_espadas_top.image = self.card_back_red
        self.monte_espadas_mid.image = self.card_back_red
        self.monte_espadas_bot.image = self.card_back_red
        self.monte_copas_top.image = self.card_back_red
        self.monte_copas_mid.image = self.card_back_red
        self.monte_copas_bot.image = self.card_back_red
        self.monte_paus_top.image = self.card_back_red
        self.monte_paus_mid.image = self.card_back_red
        self.monte_paus_bot.image = self.card_back_red
        self.table_frame.update()

    def create_player_frame(self):
        self.player_frame = LabelFrame(self.mainframe,text=self.human_player_name,labelanchor=S,background="green")
        self.player_frame.place(in_=self.mainframe,relx=0.5, rely=1, anchor="s", width=450, height=120)       

    def display_player_hand(self):
        if self.player_frame.winfo_children():
            for widget in self.player_frame.winfo_children(): 
                widget.destroy()                             #exclui as imagens de cartas da mão
        x_offset = 15
        card_width = 80
        total_width = card_width + (len(self.active_game.players[0]['hand']) - 2) * x_offset 
        frame_width = self.player_frame.winfo_width()
        start_x = (frame_width - total_width) // 2
        _sorted_hand = sorted(self.active_game.players[0]['hand'], key=lambda c: (c['suit'], c['points']))
        for index, card in enumerate(_sorted_hand):
            card_img_path = card["image_path"]
            card_img = Image.open(card_img_path).resize((60, 90))
            card_photo = ImageTk.PhotoImage(card_img)
            # Cria o Label para a carta e define a imagem
            card_label = Label(self.player_frame, image=card_photo, width=60, height=90,name=f"{card['points']}+{card['suit']}")
            card_label.image = card_photo  # Mantém uma referência à imagem
            card_label.place(x=start_x + index * x_offset, y=0)  # Centraliza a carta no eixo x

    def create_opponent_frames(self):
        number_of_players = int(self.num_players)
        if number_of_players == 2:      #2 oponentes
            self.opponent_frame1 = LabelFrame(self.mainframe,text="Player 2",labelanchor=S,background="green")
            self.opponent_frame1.place(in_=self.mainframe,relx=0.5, rely=0, anchor="n", width=450, height=120)
            self.mainframe.update()
        elif number_of_players == 3:    #3 oponentes
            self.opponent_frame1 = LabelFrame(self.mainframe,text="Player 2",labelanchor=S,background="green")
            self.opponent_frame1.place(in_=self.mainframe,relx=0.15, rely=0.5, anchor="e", width=120, height=450)
            self.opponent_frame2 = LabelFrame(self.mainframe,text="Player 3",labelanchor=S,background="green")
            self.opponent_frame2.place(in_=self.mainframe,relx=0.85, rely=0.5, anchor="w", width=120, height=450)
            self.mainframe.update()
        else:                           #4 oponentes
            self.opponent_frame1 = LabelFrame(self.mainframe,text="Player 2",labelanchor=S,background="green")
            self.opponent_frame1.place(in_=self.mainframe,relx=0.15, rely=0.5, anchor="e", width=120, height=450)
            self.opponent_frame2 = LabelFrame(self.mainframe,text="Player 3",labelanchor=S,background="green")
            self.opponent_frame2.place(in_=self.mainframe,relx=0.5, rely=0, anchor="n", width=450, height=120)
            self.opponent_frame3 = LabelFrame(self.mainframe,text="Player 4",labelanchor=S,background="green")
            self.opponent_frame3.place(in_=self.mainframe,relx=0.85, rely=0.5, anchor="w", width=120, height=450)
            self.mainframe.update()
    
    def display_opponent_hand(self):
        opponent_frames = []
        if self.num_players >= 2:
            opponent_frames.append(self.opponent_frame1)
        if self.num_players >= 3:
            opponent_frames.append(self.opponent_frame2)
        if self.num_players == 4:
            opponent_frames.append(self.opponent_frame3)    
        # Para cada frame de oponente
        for frame in opponent_frames:
            if frame.winfo_children():  # Verifica se existem widgets (cartas) no frame
                for widget in frame.winfo_children(): 
                    widget.destroy()  # Exclui todos os widgets filhos (cartas)
        # 1 oponente
        if self.num_players == 2: 
            #player 2 em cima
            x_offset = 15
            card_width = 80
            total_width = card_width + (len(self.active_game.players[1]['hand']) - 2) * x_offset 
            frame_width = self.opponent_frame1.winfo_width()
            start_x = (frame_width - total_width) // 2
            _sorted_hand = sorted(self.active_game.players[1]['hand'], key=lambda c: (c['suit'], c['points']))
            for index, card in enumerate(_sorted_hand):
                card_img_path = "/Users/miltonbraghettojr/Documents/Python/Projetos/Domino_card_game/card_deck_imgs/card_back_red.png"
                card_img = Image.open(card_img_path).resize((60, 90))
                card_photo = ImageTk.PhotoImage(card_img)
                # Cria o Label para a carta e define a imagem
                card_label = Label(self.opponent_frame1, image=card_photo, width=60, height=90)
                card_label.image = card_photo  # Mantém uma referência à imagem
                card_label.place(x=start_x + index * x_offset, y=0)  # Centraliza a carta no eixo x
        # 2 oponentes
        elif self.num_players == 3:
            #player 2 na esquerda
            y_offset = 15
            card_height = 60
            total_height = card_height + (len(self.active_game.players[1]['hand']) - 2) * y_offset 
            frame_height = self.opponent_frame1.winfo_height()
            start_y = (frame_height - total_height) // 2
            _sorted_hand = sorted(self.active_game.players[1]['hand'], key=lambda c: (c['suit'], c['points']))
            for index, card in enumerate(_sorted_hand):
                card_img_path = "/Users/miltonbraghettojr/Documents/Python/Projetos/Domino_card_game/card_deck_imgs/card_back_red.png"
                card_img = Image.open(card_img_path).resize((60, 90))
                card_img = card_img.rotate(90, expand=True)
                card_photo = ImageTk.PhotoImage(card_img)
                # Cria o Label para a carta e define a imagem
                card_label = Label(self.opponent_frame1, image=card_photo, width=90, height=60)
                card_label.image = card_photo  # Mantém uma referência à imagem
                card_label.place(x=0, y=start_y + index * y_offset)  # Centraliza a carta no eixo x
            #player 3 na direita
            y_offset = 15
            card_height = 60
            total_height = card_height + (len(self.active_game.players[2]['hand']) - 2) * y_offset 
            frame_height = self.opponent_frame2.winfo_height()
            start_y = (frame_height - total_height) // 2
            _sorted_hand = sorted(self.active_game.players[2]['hand'], key=lambda c: (c['suit'], c['points']))
            for index, card in enumerate(_sorted_hand):
                card_img_path = "/Users/miltonbraghettojr/Documents/Python/Projetos/Domino_card_game/card_deck_imgs/card_back_red.png"
                card_img = Image.open(card_img_path).resize((60, 90))
                card_img = card_img.rotate(90, expand=True)
                card_photo = ImageTk.PhotoImage(card_img)
                # Cria o Label para a carta e define a imagem
                card_label = Label(self.opponent_frame2, image=card_photo, width=90, height=60)
                card_label.image = card_photo  # Mantém uma referência à imagem
                card_label.place(x=0, y=start_y + index * y_offset)  # Centraliza a carta no eixo x
        # 3 oponentes
        else:
            #player 2 na esquerda
            y_offset = 15
            card_height = 60
            total_height = card_height + (len(self.active_game.players[1]['hand']) - 2) * y_offset 
            frame_height = self.opponent_frame1.winfo_height()
            start_y = (frame_height - total_height) // 2
            _sorted_hand = sorted(self.active_game.players[1]['hand'], key=lambda c: (c['suit'], c['points']))
            for index, card in enumerate(_sorted_hand):
                card_img_path = "/Users/miltonbraghettojr/Documents/Python/Projetos/Domino_card_game/card_deck_imgs/card_back_red.png"
                card_img = Image.open(card_img_path).resize((60, 90))
                card_img = card_img.rotate(90, expand=True)
                card_photo = ImageTk.PhotoImage(card_img)
                # Cria o Label para a carta e define a imagem
                card_label = Label(self.opponent_frame1, image=card_photo, width=90, height=60)
                card_label.image = card_photo  # Mantém uma referência à imagem
                card_label.place(x=0, y=start_y + index * y_offset)  # Centraliza a carta no eixo x
            #player 3 em cima
            x_offset = 15
            card_width = 80
            total_width = card_width + (len(self.active_game.players[2]['hand']) - 2) * x_offset 
            frame_width = self.opponent_frame2.winfo_width()
            start_x = (frame_width - total_width) // 2
            _sorted_hand = sorted(self.active_game.players[2]['hand'], key=lambda c: (c['suit'], c['points']))
            for index, card in enumerate(_sorted_hand):
                card_img_path = "/Users/miltonbraghettojr/Documents/Python/Projetos/Domino_card_game/card_deck_imgs/card_back_red.png"
                card_img = Image.open(card_img_path).resize((60, 90))
                card_photo = ImageTk.PhotoImage(card_img)
                # Cria o Label para a carta e define a imagem
                card_label = Label(self.opponent_frame2, image=card_photo, width=60, height=90)
                card_label.image = card_photo  # Mantém uma referência à imagem
                card_label.place(x=start_x + index * x_offset, y=0)  # Centraliza a carta no eixo x
            #player 4 na direita
            y_offset = 15
            card_height = 60
            total_height = card_height + (len(self.active_game.players[3]['hand']) - 2) * y_offset 
            frame_height = self.opponent_frame3.winfo_height()
            start_y = (frame_height - total_height) // 2
            _sorted_hand = sorted(self.active_game.players[3]['hand'], key=lambda c: (c['suit'], c['points']))
            for index, card in enumerate(_sorted_hand):
                card_img_path = "/Users/miltonbraghettojr/Documents/Python/Projetos/Domino_card_game/card_deck_imgs/card_back_red.png"
                card_img = Image.open(card_img_path).resize((60, 90))
                card_img = card_img.rotate(90, expand=True)
                card_photo = ImageTk.PhotoImage(card_img)
                # Cria o Label para a carta e define a imagem
                card_label = Label(self.opponent_frame3, image=card_photo, width=90, height=60)
                card_label.image = card_photo  # Mantém uma referência à imagem
                card_label.place(x=0, y=start_y + index * y_offset)  # Centraliza a carta no eixo x
    
    def end_game(self):
        self.active_game.game_ended() #mostra resultados no terminal
        if len(self.active_game.players[0]['burned_pile']) > 0: #mostra cartas queimadas do jogador
            x_offset = 15
            card_width = 80
            total_width = card_width + (len(self.active_game.players[0]['burned_pile']) - 2) * x_offset 
            frame_width = self.player_frame.winfo_width()
            start_x = (frame_width - total_width) // 2
            _sorted_burned_pile = sorted(self.active_game.players[0]['burned_pile'], key=lambda c: (c['suit'], c['points']))
            for index, card in enumerate(_sorted_burned_pile):
                card_img_path = card["image_path"]
                card_img = Image.open(card_img_path).resize((60, 90))
                card_photo = ImageTk.PhotoImage(card_img)
                # Cria o Label para a carta e define a imagem
                card_label = Label(self.player_frame, image=card_photo, width=60, height=90,name=f"{card['points']}+{card['suit']}")
                card_label.image = card_photo  # Mantém uma referência à imagem
                card_label.place(x=start_x + index * x_offset, y=0)  # Centraliza a carta no eixo x
        for player in self.active_game.players:
            player['score'] = player['points']
        self.player_frame.configure(text=self.human_player_name+f": {self.active_game.players[0]['points']} pontos")
        #atualiza frames com pontuação e mostra cartas queimadas
        if self.num_players == 2:
            self.opponent_frame1.configure(text=f"Player 2: {self.active_game.players[1]['points']} pontos")
            #player 2 em cima
            x_offset = 15
            card_width = 80
            total_width = card_width + (len(self.active_game.players[1]['burned_pile']) - 2) * x_offset 
            frame_width = self.opponent_frame1.winfo_width()
            start_x = (frame_width - total_width) // 2
            _sorted_hand = sorted(self.active_game.players[1]['burned_pile'], key=lambda c: (c['suit'], c['points']))
            for index, card in enumerate(_sorted_hand):
                card_img_path = card['image_path']
                card_img = Image.open(card_img_path).resize((60, 90))
                card_photo = ImageTk.PhotoImage(card_img)
                # Cria o Label para a carta e define a imagem
                card_label = Label(self.opponent_frame1, image=card_photo, width=60, height=90)
                card_label.image = card_photo  # Mantém uma referência à imagem
                card_label.place(x=start_x + index * x_offset, y=0)  # Centraliza a carta no eixo x
        if self.num_players == 3:
            self.opponent_frame1.configure(text=f"Player 2: {self.active_game.players[1]['points']} pontos")
            #player 2 na esquerda
            y_offset = 15
            card_height = 60
            total_height = card_height + (len(self.active_game.players[1]['burned_pile']) - 2) * y_offset 
            frame_height = self.opponent_frame1.winfo_height()
            start_y = (frame_height - total_height) // 2
            _sorted_hand = sorted(self.active_game.players[1]['burned_pile'], key=lambda c: (c['suit'], c['points']))
            for index, card in enumerate(_sorted_hand):
                card_img_path = card['image_path']
                card_img = Image.open(card_img_path).resize((60, 90))
                card_img = card_img.rotate(90, expand=True)
                card_photo = ImageTk.PhotoImage(card_img)
                # Cria o Label para a carta e define a imagem
                card_label = Label(self.opponent_frame1, image=card_photo, width=90, height=60)
                card_label.image = card_photo  # Mantém uma referência à imagem
                card_label.place(x=0, y=start_y + index * y_offset)  # Centraliza a carta no eixo x
            self.opponent_frame2.configure(text=f"Player 3: {self.active_game.players[2]['points']} pontos")
            #player 3 na direita
            y_offset = 15
            card_height = 60
            total_height = card_height + (len(self.active_game.players[2]['burned_pile']) - 2) * y_offset 
            frame_height = self.opponent_frame2.winfo_height()
            start_y = (frame_height - total_height) // 2
            _sorted_hand = sorted(self.active_game.players[2]['burned_pile'], key=lambda c: (c['suit'], c['points']))
            for index, card in enumerate(_sorted_hand):
                card_img_path = card['image_path']
                card_img = Image.open(card_img_path).resize((60, 90))
                card_img = card_img.rotate(90, expand=True)
                card_photo = ImageTk.PhotoImage(card_img)
                # Cria o Label para a carta e define a imagem
                card_label = Label(self.opponent_frame2, image=card_photo, width=90, height=60)
                card_label.image = card_photo  # Mantém uma referência à imagem
                card_label.place(x=0, y=start_y + index * y_offset)  # Centraliza a carta no eixo x
        if self.num_players == 4:
            self.opponent_frame1.configure(text=f"Player 2: {self.active_game.players[1]['points']} pontos")
            #player 2 na esquerda
            y_offset = 15
            card_height = 60
            total_height = card_height + (len(self.active_game.players[1]['burned_pile']) - 2) * y_offset 
            frame_height = self.opponent_frame1.winfo_height()
            start_y = (frame_height - total_height) // 2
            _sorted_hand = sorted(self.active_game.players[1]['burned_pile'], key=lambda c: (c['suit'], c['points']))
            for index, card in enumerate(_sorted_hand):
                card_img_path = card['image_path']
                card_img = Image.open(card_img_path).resize((60, 90))
                card_img = card_img.rotate(90, expand=True)
                card_photo = ImageTk.PhotoImage(card_img)
                # Cria o Label para a carta e define a imagem
                card_label = Label(self.opponent_frame1, image=card_photo, width=90, height=60)
                card_label.image = card_photo  # Mantém uma referência à imagem
                card_label.place(x=0, y=start_y + index * y_offset)  # Centraliza a carta no eixo x
            self.opponent_frame2.configure(text=f"Player 3: {self.active_game.players[2]['points']} pontos")
            #player 3 em cima
            x_offset = 15
            card_width = 80
            total_width = card_width + (len(self.active_game.players[2]['burned_pile']) - 2) * x_offset 
            frame_width = self.opponent_frame2.winfo_width()
            start_x = (frame_width - total_width) // 2
            _sorted_hand = sorted(self.active_game.players[2]['burned_pile'], key=lambda c: (c['suit'], c['points']))
            for index, card in enumerate(_sorted_hand):
                card_img_path = card['image_path']
                card_img = Image.open(card_img_path).resize((60, 90))
                card_photo = ImageTk.PhotoImage(card_img)
                # Cria o Label para a carta e define a imagem
                card_label = Label(self.opponent_frame2, image=card_photo, width=60, height=90)
                card_label.image = card_photo  # Mantém uma referência à imagem
                card_label.place(x=start_x + index * x_offset, y=0)  # Centraliza a carta no eixo x
            self.opponent_frame3.configure(text=f"Player 4: {self.active_game.players[3]['points']} pontos")
            #player 4 na direita
            y_offset = 15
            card_height = 60
            total_height = card_height + (len(self.active_game.players[3]['burned_pile']) - 2) * y_offset 
            frame_height = self.opponent_frame3.winfo_height()
            start_y = (frame_height - total_height) // 2
            _sorted_hand = sorted(self.active_game.players[3]['burned_pile'], key=lambda c: (c['suit'], c['points']))
            for index, card in enumerate(_sorted_hand):
                card_img_path = card['image_path']
                card_img = Image.open(card_img_path).resize((60, 90))
                card_img = card_img.rotate(90, expand=True)
                card_photo = ImageTk.PhotoImage(card_img)
                # Cria o Label para a carta e define a imagem
                card_label = Label(self.opponent_frame3, image=card_photo, width=90, height=60)
                card_label.image = card_photo  # Mantém uma referência à imagem
                card_label.place(x=0, y=start_y + index * y_offset)  # Centraliza a carta no eixo x

        self.frame_final = Frame(self.mainframe)
        self.frame_final.place(relx=0.5,rely=0.1,width=350,height=250)
        self.frame_final.columnconfigure((0,1,2), weight=1)
        self.frame_final.rowconfigure((0,1,2), weight=1)
        t1 = ttk.Label(self.frame_final, text="Fim de jogo!\n").grid(row=0,column=0,columnspan=2)
        t2 = ttk.Label(self.frame_final, text="Deseja jogar novamente?").grid(row=1,column=0,columnspan=2)
        b1 = ttk.Button(self.l1_frame,command="",text="Jogar")
        b1.grid(row=3,column=2,columnspan=2,pady=10)
        b2 = ttk.Button(self.l1_frame,command="",text="Sair")
        b2.grid(row=3,column=1,columnspan=2,pady=10)


if __name__ == "__main__":
    root = Tk()
    config_screen = Config_Screen(root)
    root.mainloop()

# Fazer uma tela de fim de jogo melhor
# Dar opção de continuar jogar mais partidas (atualizar frames para score)
# Adicionar console