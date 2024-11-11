import random

class GameManager:
    #usar o front para iniciar já com número de jogadores e nome
    def __init__(self, num_players, human_player_name):
        self.num_players = num_players
        self.players = [
                       {'name': f"Player {i + 1}", 'hand': [], 'burned_pile': [], 'points': 0, 'score': 0}
                        for i in range(num_players)
                        ]
        self.players[0]['name'] = human_player_name
        self.table_piles =  {
        "ouros": [],
        "espadas": [],
        "copas": [],
        "paus": []
        }
        self.start_game(self.players)

    def __str__(self) -> str:
        return "GameManager"

    def create_deck(self): #testado e funcionando
        suits = ["ouros", "espadas", "copas", "paus"]
        suits_en = ["diamonds", "spades", "hearts", "clubs"]
        values = {"A": 1,"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13}
        suit_symbols = {
            "ouros": "♦",
            "espadas": "♠",
            "copas": "♥",
            "paus": "♣"
        }
        deck = []
        for i, suit in enumerate(suits):
            for value, points in values.items():
                deck.append({
                    "card": f"{value} de {suit}",
                    "card_en": f"{value}_of_{suits_en[i]}",
                    "value": value,
                    "suit": suit,
                    "suits_en": suits_en[i],  # Nome do naipe em inglês correspondente
                    "points": points,
                    "symbol": suit_symbols[suit],
                    "card_short": f"{value}{suit_symbols[suit]}",
                    "image_path": f"/Users/miltonbraghettojr/Documents/Python/Projetos/Domino_card_game/card_deck_imgs/{value}_of_{suits_en[i]}.png"  # Nome da carta em inglês para exibição
                })
        return deck

    def give_cards(self,players,deck): #testado e funcionando
        random.shuffle(deck)
        cards_per_player = len(deck) // len(players)
        for _player in players:
            _player['hand'].extend(deck[:cards_per_player])
            deck = deck[cards_per_player:]                                    # Remove as cartas já distribuídas do baralho
        if len(deck) > 0:                                                     # Verifica se sobraram cartas no baralho (no caso de 3 jogadores)
            for _,_player in enumerate(players):
                if any(card['card'] == '7 de ouros' for card in _player['hand']):
                    _player['hand'].extend(deck)                                      # Atribui qualquer carta restante ao jogador que começará com 7 de ouros
                    break

    def player_order(self,players): #testado e funcionando
        starting_index = next((i for i, player in enumerate(players) if any(card['card'] == '7 de ouros' for card in player['hand'])),None)
        ordered_players = players[starting_index:] + players[:starting_index]
        return ordered_players

    def check_plays(self,table_piles,hand): #testado e funcionando
        self.cards_playable = []
        for _card in hand:
            points = _card['points']
            suit = _card['suit']
            current_pile_values = [c['points'] for c in table_piles[suit]]
            if points == 7:
                self.cards_playable.append(_card)
            if current_pile_values and (points == max(current_pile_values) + 1 or points == min(current_pile_values) - 1):
                self.cards_playable.append(_card)
        return self.cards_playable

    def start_game(self, players):
        self.deck = self.create_deck()                                  # cria o baralho
        print("Embaralhando e distribuindo cartas...")
        self.give_cards(self.players,self.deck)                         # distribui as cartas de cada um
        self.ordered_players = self.player_order(self.players)          # define ordem dos jogadores
        
        # _card = next((card for card in self.deck if card["card"]== "7 de ouros"), None) #acha o 7♦ na mão dos jogadores
        # self.table_piles[_card["suit"]].append(_card) #adiciona o 7♦ na mesa
        # self.ordered_players[0]['hand'].remove(_card) #tira o 7♦ da mão do jogador

        #mostrar mãos no terminal
        for player in players:
            _sorted_hand = sorted(player['hand'], key=lambda c: (c['suit'], c['points']))
            print(f"\n{player['name']} tem: " + ", ".join(card['card_short'] for card in _sorted_hand))
            _player_hand = player['hand']
            cards_playable = sorted(self.check_plays(self.table_piles,_player_hand),key=lambda c: (c['suit'],c['points']))
            print("Cartas jogáveis: " + ", ".join(card['card_short'] for card in cards_playable))
            print("Qdt. cartas:" + str(len(player['hand'])))
        
        print(f"\n{self.ordered_players[0]['name']} tem o 7♦ e deve jogá-lo primeiro para iniciar a partida!\n")

    def game_ended(self): #
    # Exibe resultados
        print(f"\n\n####### Fim do jogo! #######\n\nPontuações:\n")
        for player in self.players:
            print(f"{player['name']} fez {player['points']} pontos")
            if player['burned_pile']:
                print(f" - Cartas queimadas: " + ", ".join(card['card_short'] for card in player['burned_pile']))
            else:
                print(" - Nenhuma carta queimada!")

        # Verifica o vencedor e empates
        min_points = min(self.players, key=lambda p: p['points'])['points']
        winners = [player for player in self.players if player['points'] == min_points]
        if len(winners) > 1:
            print("\nHouve um empate entre os seguintes jogadores: ")
            for winner in winners:
                print(f" - {winner['name']} com {winner['points']} pontos")
        else:
            winner = winners[0]
            print(f"\nO vencedor desta rodada é {winner['name']} com {winner['points']} pontos!")
        