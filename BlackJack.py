from random import seed
from random import randint

class BlackJack:
    def __init__(self, number_of_decks, players, my_position):
        self.number_of_decks = number_of_decks
        self.my_position = my_position
        self.players = players + 1
        self.player_hands = []
        self.init_deck_quantity = self.number_of_decks * 52
        self.init_card_quantity = 4 * self.number_of_decks
        self.cards_left_in_deck = 0
        self.card_to_value_map = [
            {'A': 11, 'quantity': self.init_card_quantity},
            {'2': 2, 'quantity': self.init_card_quantity},
            {'3': 3, 'quantity': self.init_card_quantity},
            {'4': 4, 'quantity': self.init_card_quantity},
            {'5': 5, 'quantity': self.init_card_quantity},
            {'6': 6, 'quantity': self.init_card_quantity},
            {'7': 7, 'quantity': self.init_card_quantity},
            {'8': 8, 'quantity': self.init_card_quantity},
            {'9': 9, 'quantity': self.init_card_quantity},
            {'10': 10, 'quantity': self.init_card_quantity},
            {'J': 10, 'quantity': self.init_card_quantity},
            {'Q': 10, 'quantity': self.init_card_quantity},
            {'K': 10, 'quantity': self.init_card_quantity}
        ]

    # Entry point of program
    def begin_game(self):
        self.deal_first_hand()
        self.ask_to_hit()

    # Assign initial cards to every player hand at the beginning of game
    def deal_first_hand(self):
        for i in range(self.players):

            # Generate a random value to index the list of playing cards by, thus providing a random card
            value_1 = randint(0, 12)
            value_2 = randint(0, 12)

            # Return the first key of the indexed dictionary, which is what we'll use to identify the card
            card_1 = next(iter(self.card_to_value_map[value_1]))
            card_2 = next(iter(self.card_to_value_map[value_2]))

            # Append these cards to a player's hand
            self.player_hands.append(
                {f'p{i + 1}': i + 1, 'hand': [card_1, card_2]})

            # For every card dealt, decrement the quantity of that card left in the deck
            self.card_to_value_map[value_1]['quantity'] = self.card_to_value_map[value_1]['quantity'] - 1
            self.card_to_value_map[value_2]['quantity'] = self.card_to_value_map[value_2]['quantity'] - 1

            # If a card has zero quantity left, remove it from the deck
            if self.card_to_value_map[value_1]['quantity'] == 0:
                del self.card_to_value_map[value_1]
            if self.card_to_value_map[value_2]['quantity'] == 0:
                del self.card_to_value_map[value_2]

    def ask_to_hit(self):
        print("Note: 'X' is the face down card.\n")

        # For every hand besides the dealer's, ask the player if they want to 'hit'
        i = 0
        while i < len(self.player_hands) -1:
            print(f"The Dealer is showing: X {self.player_hands[-1]['hand'][:-1]}")

            # If i == the position of the player we care about, calculate odds of "busting" upon receiving another card
            if i == self.my_position:
                self.calculate_chance_of_busting(self.player_hands[i]['hand'])

            hit = input(f"\nPlayer {i+1} would you like to hit? (y / n)\nYour hand is: {self.player_hands[i]['hand']}\n\nAnswer: ")

            if (hit == 'y'):
                self.hit_player(i)
                i += 1 
            else:
                i += 1 
                continue

        self.hit_dealer()

    def hit_player(self, indx):
        # For contextual clarity we'll set player = indx, denoting the position of the player
        player = indx

        # Set n = to the number of ranks left to be played
        n = len(self.card_to_value_map) - 1

        # Generate a random value to index the list of playing cards by, thus providing a random card
        value = randint(0, n)

        # Return the first key of the indexed dictionary, which is what we'll use to identify the card
        card = next(iter(self.card_to_value_map[value]))

        # Add the new card to the player's hand
        self.player_hands[player]['hand'].append(card)

        # Decrement the quantity of that card left in the deck
        self.card_to_value_map[value]['quantity'] = self.card_to_value_map[value]['quantity'] - 1

        # If a card has zero quantity left, remove it from the deck
        if self.card_to_value_map[value]['quantity'] == 0:
            del self.card_to_value_map[value]

        # Calculate the new value of the hand
        hand_value = self.calculate_value_of_hand(self.player_hands[player]['hand'])

        # If the value of the player's hand is greater than 21, their hand has busted, so remove them from the list of players
        if (hand_value > 21):
            print(f"\nYour hand is: {self.player_hands[player]['hand']}")
            print(f"\nPlayer {player +1} your hand has busted.\n")
            del self.player_hands[player]
            return

        # If the value of the player's hand equals 21, they've won and can play no further, so remove them from the list of players
        if (hand_value == 21):
            print(f"\nYour hand is: {self.player_hands[player]['hand']}")
            print(f"\nPlayer {player +1} you've recieved 21. Congrats!\n")
            del self.player_hands[player]
            return

        # If player == the position of the player we care about, calculate odds of "busting" upon receiving another card
        if player == self.my_position:
            self.calculate_chance_of_busting(self.player_hands[player]['hand'])

        # If none of the above conditions are met, and the player has a chance to continue, ask them if they want to hit again
        print(f"Your current hand value is: {hand_value}")
        hit_again = input(f"\nWould you like to hit again? (y / n)\nYour hand is: {self.player_hands[player]['hand']}\n\nAnswer: ")

        # As long as the player wants to hit, and his hand neither exceeds nor equals 21, run this function recursively
        if (hit_again == 'y'):
            return self.hit_player(player)
        else:
            return

    def calculate_value_of_hand(self, player_hand):
        hand_value = 0
        Ace_card = False
        for c in player_hand:
            if c in ['J', 'Q', 'K']:
                c = 10
            if c == 'A':
                Ace_card = True
                c = 1
            hand_value += int(c)

        if hand_value > 21 and Ace_card == True:
            hand_value = (hand_value - 11) + 1

        return hand_value

    def hit_dealer(self):
        dealer_hand_value = self.calculate_value_of_hand(
            self.player_hands[-1]['hand'])

        bust = False
        if (dealer_hand_value >= 17 or dealer_hand_value > 21):
            print(f"\nDealer's final hand is: {self.player_hands[-1]['hand']}")
            if dealer_hand_value > 21:
                bust = True
            self.list_players_wins_losses(dealer_hand_value, bust)
            return

        print("\nHitting dealer ...")
        # Set n = to the number of ranks left to be played
        n = len(self.card_to_value_map) - 1

        # Generate a random value to index the list of playing cards by, thus providing a random card
        value = randint(0, n)

        # Return the first key of the indexed dictionary, which is what we'll use to identify the card
        card = next(iter(self.card_to_value_map[value]))

        self.player_hands[-1]['hand'].append(card)

        hand_value = self.calculate_value_of_hand(
            self.player_hands[-1]['hand'])
        print(f"\nDealer's hand is: {self.player_hands[-1]['hand']}")

        self.hit_dealer()

    def list_players_wins_losses(self, dealer_hand_value, bust):
        if (bust == True):
            print(f"Dealer has busted.\n")
            for i in range(len(self.player_hands) -1):
                print(f"Players {i + 1} has won.")
            return

        hand_value = 0

        for i in range(len(self.player_hands) -1):
            player_hand = self.player_hands[i]['hand']

            hand_value = self.calculate_value_of_hand(player_hand)
                
            if (hand_value < dealer_hand_value):
                print(f"\n{self.player_hands[i]}")
                print(f"Player {i + 1} you loss.")
        
            if (hand_value == dealer_hand_value):
                print(f"\n{self.player_hands[i]}")
                print(f"Player {i + 1} you pushed.")

            if (hand_value > dealer_hand_value):
                print(f"\n{self.player_hands[i]}")
                print(f"Player {i + 1} you won!")

            hand_value = 0

    def calculate_chance_of_busting(self, player_hand):
        self.calculate_cards_in_play()
        self.calculate_n_cards_to_cause_bust(player_hand)

    def calculate_cards_in_play(self):
        cards = 0
        for i in range(len(self.card_to_value_map)):
            cards += self.card_to_value_map[i]['quantity']

        self.cards_left_in_deck = self.init_deck_quantity - (self.init_deck_quantity - cards)

    def calculate_n_cards_to_cause_bust(self, player_hand):
        hand_value = self.calculate_value_of_hand(player_hand)
        bust_value = (21 - hand_value) + 1
        bust_cards_quantity = 0

        for i in range(len(self.card_to_value_map)):
            if list(self.card_to_value_map[i].values())[0] >= bust_value:
                bust_cards_quantity += self.card_to_value_map[i]['quantity']

        chance_of_busting = (bust_cards_quantity / self.cards_left_in_deck)

        print(f"\nYour chance of busting is: {chance_of_busting}")

game = BlackJack(1, 4, 3)
game.begin_game()
