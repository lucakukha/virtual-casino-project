import pygame
import time
import sys
import random
import os
import math

def resource_path(relative_path):
    """ Get the absolute path to the resource. Works for development and PyInstaller. """
    try:
        # PyInstaller stores data files in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def format_balance(balance):
    return f"£{balance:.2f}"

# Initialize Pygame
pygame.init()
# Define fonts
title_font = pygame.font.SysFont("Calibri Light", 45)  # Larger font for the title
menu_font = pygame.font.SysFont("Arial", 32)  # Standard font for menu items

player_balance = 1000
width, height = 60, 30

game_active = False

# Constants for the display
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BACKGROUND_COLOR = (30, 80, 27)  # Dark green
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
GRAY = (192, 192, 192)
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (105, 105, 105)
YELLOW = (255, 255, 0)
SILVER = (192, 192, 192)

# Setup display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Blackjack")


def main_menu():
    global player_balance
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    blackjack_main()
                elif event.key == pygame.K_2:
                    show_welcome_screen()
                    roulette_game_loop()
                elif event.key == pygame.K_3:
                    slots_game()
                elif event.key == pygame.K_4:
                    horse_racing_game()  # This would call the main function of your horse racing game
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        screen.fill(BACKGROUND_COLOR)
        
        # Menu Text Entries
        menu_text = [
            "1 For Blackjack",
            "2 For Roulette",
            "3 for Slots",
            "4 for Horse Racing",
            "ESC to Exit"
        ]

        # Displaying the title
        title_text = "Welcome to Hit on 19 Casino!"
        title_surface = title_font.render(title_text, True, GOLD)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH / 2, 100))
        screen.blit(title_surface, title_rect)

        # Displaying the balance just below the title
        balance_text = title_font.render(format_balance(player_balance), True, SILVER)
        balance_rect = balance_text.get_rect(center=(SCREEN_WIDTH / 2, 150))
        screen.blit(balance_text, balance_rect)

        # Displaying each line of the menu
        y_offset = 200
        for line in menu_text:
            text_surface = menu_font.render(line, True, WHITE)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH / 2, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += 50  # Consistent spacing for menu items

        pygame.display.flip()


# Load card images
def load_card_images():
    card_images = {}
    card_folder = resource_path('Cards')  # Updated to use resource_path
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']

    card_width = 90  # Adjust width as needed
    card_height = 140  # Adjust height as needed

    for suit in suits:
        for rank in ranks:
            filename = f"{rank.lower()}_of_{suit.lower()}.png"
            filepath = os.path.join(card_folder, filename)
            card_key = f"{rank} of {suit}"
            try:
                original_image = pygame.image.load(filepath).convert_alpha()
                scaled_image = pygame.transform.scale(original_image, (card_width, card_height))
                card_images[card_key] = scaled_image
            except pygame.error as e:
                print(f"Error loading image: {filepath} - {e}")
    return card_images

# Card values
card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10,
    'jack': 10, 'queen': 10, 'king': 10, 'ace': 11
}

# Simple function to draw text on the screen
def draw_text(text, position, font_size=12, color=(255, 255, 255)):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

# Create a deck of cards
def create_deck():
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
    return [f"{rank} of {suit}" for suit in suits for rank in ranks]

# Shuffle the deck
def shuffle_deck(deck):
    random.shuffle(deck)
    return deck

# Deal a card from the deck
def deal_card(deck, hand):
    card = deck.pop()
    hand.append(card)
    return card

# Calculate the value of a hand
def calculate_hand_value(hand):
    value = 0
    aces = 0
    for card in hand:
        rank = card.split(' of ')[0]
        value += card_values[rank]
        if rank == 'ace':
            aces += 1
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

# Draw the hands
def draw_hands(player_hand, dealer_hand, card_images):
    y_offset = 400
    for card in player_hand:
        card_image = card_images[card]
        x_offset = player_hand.index(card) * 60
        screen.blit(card_image, (100 + x_offset, y_offset))
    
    y_offset = 100
    for card in dealer_hand:
        card_image = card_images[card]
        x_offset = dealer_hand.index(card) * 60
        screen.blit(card_image, (100 + x_offset, y_offset))

# Start a new game with betting
def new_game(deck, player_balance):
    bet, bet_confirmed = get_bet_graphically(player_balance)
    if not bet_confirmed:  # If the bet was not confirmed, return a signal to not proceed with the game
        return [], [], deck, 0, player_balance, False

    player_hand = []
    dealer_hand = []
    deck = shuffle_deck(create_deck())
    deal_card(deck, player_hand)
    deal_card(deck, dealer_hand)
    deal_card(deck, player_hand)
    deal_card(deck, dealer_hand)
    player_balance -= bet
    return player_hand, dealer_hand, deck, bet, player_balance, True


def get_bet_graphically(player_balance):
    bet = 0
    betting = True
    bet_confirmed = False  # Add a flag to indicate bet confirmation
    while betting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                betting = False
                bet_confirmed = False  # Handle quitting during betting
                break  # Exit the loop
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and bet < player_balance:
                    bet += 10
                elif event.key == pygame.K_DOWN and bet > 0:
                    bet -= 10
                elif event.key == pygame.K_RETURN:
                    betting = False
                    bet_confirmed = True  # Confirm bet
                elif event.key == pygame.K_ESCAPE:
                    betting = False
                    bet = 0
                    bet_confirmed = False  # Bet canceled
                
        screen.fill(BACKGROUND_COLOR)
        draw_text("Place your bet", (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 60), 36)
        draw_text(f"Bet: £{bet}", (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2), 36)
        draw_text("Use UP/DOWN arrows to adjust, ENTER to confirm, ESC to cancel.", (SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 + 60), 24)
        pygame.display.flip()

    return bet, bet_confirmed

def draw_blackjack_instructions():
    instructions = [
        "Press 'H' to Hit",
        "Press 'S' to Stand",
        "Press ESC to Return to Menu"
    ]
    y_position = 40  # Start drawing instructions from the top
    for instruction in instructions:
        draw_text(instruction, (500, y_position), 24, WHITE)
        y_position += 30  # Adjust spacing between each line


def blackjack_main():
    global player_balance
    card_images = load_card_images()
    deck = create_deck()  # Starting balance
    
    running = True
    while running:
        game_over = False
        # Start a new game or round with betting
        player_hand, dealer_hand, deck, bet, player_balance, bet_confirmed = new_game(deck, player_balance)
        
        
        if not bet_confirmed:
            running = False
            break  

        while not game_over and running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_h:  # Hit
                        deal_card(deck, player_hand)
                        if calculate_hand_value(player_hand) > 21:
                            game_over = True
                    elif event.key == pygame.K_s:  # Stand
                        while calculate_hand_value(dealer_hand) < 17:
                            deal_card(deck, dealer_hand)
                        game_over = True

            # Clear the screen and redraw
            screen.fill(BACKGROUND_COLOR)
            draw_hands(player_hand, dealer_hand, card_images)
            draw_text(f"Player: {calculate_hand_value(player_hand)}", (100, 370), 36)
            draw_text(format_balance(player_balance), (600, 10), 24)
            draw_blackjack_instructions()
            
            if game_over:
                # Determine winner
                dealer_score = calculate_hand_value(dealer_hand)
                player_score = calculate_hand_value(player_hand)
                draw_text(f"Dealer: {dealer_score}", (100, 70), 36)
                if player_score > 21 or (dealer_score <= 21 and dealer_score > player_score):
                    winner = "Dealer"
                elif dealer_score > 21 or player_score > dealer_score:
                    winner = "Player"
                    player_balance += bet * 2
                elif player_score == dealer_score:
                    winner = "No one"
                    player_balance += bet
                    
                draw_text(f"{winner} Wins", (300, SCREEN_HEIGHT // 2), 48)
                pygame.display.flip()
                pygame.time.wait(2000)  # Wait for 2 seconds before proceeding
                break  # Exit the loop to start a new game or end based on your game design.

            pygame.display.flip()
    
    main_menu()

# Screen dimensions and setup
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Roulette Simulation")


# Game variables
bet_amount = 50
bet_type = None
bet_choice = None
winning_number = None
angle = 0
ball_position = (0, 0)
current_speed = 0
game_state = 'betting'
winning_text = ""
bet_placed = False
input_text = ""

# Define red and black numbers
red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
black_numbers = set(range(1, 37)) - red_numbers

# Initialize wheel segments
wheel_segments = [
    (GREEN, '0'), *[(RED if n in red_numbers else BLACK, str(n)) for n in range(1, 37)]
]

# Wheel and ball parameters
wheel_radius = 150
wheel_center = (400, 300)
num_segments = 37  # Including 0
segment_angle = 360 / num_segments
ball_radius = 8



def show_welcome_screen():
    welcome_running = True
    while welcome_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Press space to continue to the game.
                    welcome_running = False
        
        screen.fill(BACKGROUND_COLOR)
        # Instructions text
        instructions_text = [
            "Welcome to Roulette!",
            "Press 'R' to bet on Red.",
            "Press 'B' to bet on Black.",
            "Press 'H' to bet on House.",
            "Press 'O' to bet on Odd.",
            "Press 'E' to bet on Even.",
            "Use UP and DOWN arrows to adjust bet amount.",
            "Press SPACE to start playing.",
            "Press ESC to return to menu"
        ]
        
        y_offset = 100
        for line in instructions_text:
            text_surface = font.render(line, True, WHITE)
            text_rect = text_surface.get_rect(center=(screen_width / 2, y_offset))
            screen.blit(text_surface, text_rect)
            y_offset += 30  # Adjust spacing as needed
        
        pygame.display.flip()
        pygame.time.wait(100)


def draw_wheel():
    for i, (color, number) in enumerate(wheel_segments):
        start_angle = (360 / num_segments) * i - 90
        end_angle = start_angle + (360 / num_segments)
        pygame.draw.polygon(screen, color, [
            wheel_center,
            (wheel_center[0] + wheel_radius * math.cos(math.radians(start_angle)), wheel_center[1] + wheel_radius * math.sin(math.radians(start_angle))),
            (wheel_center[0] + wheel_radius * math.cos(math.radians(end_angle)), wheel_center[1] + wheel_radius * math.sin(math.radians(end_angle)))
        ])
        angle_mid = start_angle + (360 / num_segments) / 2
        x = wheel_center[0] + (wheel_radius - 20) * math.cos(math.radians(angle_mid))
        y = wheel_center[1] + (wheel_radius - 20) * math.sin(math.radians(angle_mid))
        text = font.render(number, True, WHITE)
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)

def handle_key_events():
    global bet_amount, game_state, current_speed, bet_placed, input_text, bet_choice, bet_type, player_balance
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:

            if game_state == "betting":
                if event.key == pygame.K_RETURN and game_state == 'betting' and input_text:
                    process_bet_input()
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_UP:
                    bet_amount += 10
                    update_bet_display()
                elif event.key == pygame.K_DOWN:
                    bet_amount = max(10, bet_amount - 10)
                    update_bet_display()
                elif event.key in (pygame.K_r, pygame.K_b, pygame.K_h, pygame.K_o, pygame.K_e):
                    input_text = {'r': 'red', 'b': 'black', 'h': 'house', 'o': 'odd', 'e': 'even'}[pygame.key.name(event.key)]
                    process_bet_input()
                elif event.key == pygame.K_ESCAPE:
                        return False


                 

def process_bet_input():
    global bet_amount, game_state, current_speed, bet_placed, input_text, bet_choice, bet_type, player_balance
    valid_bets = {'red', 'black', 'house', 'odd', 'even'}
    if input_text in valid_bets and player_balance >= bet_amount:
        bet_choice = input_text
        bet_type = 'number' if input_text == 'house' else 'color' if input_text in ['red', 'black'] else 'evenodd'
        player_balance -= bet_amount
        bet_placed = True
        game_state = 'spinning'
        speed_min = 10
        speed_max = 15
        current_speed = random.uniform(speed_min, speed_max)
        input_text = ""  # Clear input after processing

def draw_current_bet():
    if bet_placed:
        bet_text = f"Bet: {bet_choice.upper()} - Amount: £{bet_amount}"
    else:
        bet_text = "No bet placed"
    bet_info_text = font.render(bet_text, True, WHITE)
    bet_info_rect = bet_info_text.get_rect(left=10, top=20)
    screen.blit(bet_info_text, bet_info_rect)
    balance_text = font.render(format_balance(player_balance), True, WHITE)
    balance_rect = balance_text.get_rect(left=10, top=40)
    screen.blit(balance_text, balance_rect)
    
def draw_ball():
    global ball_position
    pygame.draw.circle(screen, WHITE, ball_position, ball_radius)

def spin_wheel():
    global angle, ball_position, current_speed, game_state, winning_number, winning_text
    if game_state != 'spinning':
        return

    angle += current_speed
    if current_speed > 0:
        dec_min = 0.95
        dec_max = 0.999
        deceleration = random.uniform(dec_min, dec_max)
        current_speed *= deceleration  # Deceleration effect
    if current_speed <= 0.15 and current_speed > 0:
        current_speed = 0
        # Normalize the stopping angle of the wheel considering the -90 degrees offset when the segments are drawn
        normalized_angle = (angle + 90) % 360
        # Find the index of the segment where the ball has stopped
        segment_index = int(normalized_angle / segment_angle)
        # Adjust index based on wheel layout, if necessary
        # Use a lookup here if the numbers are not sequential
        winning_number = segment_index
        color = "Red" if winning_number in red_numbers else "Black" if winning_number != 0 else "Green"
        winning_text = f"Winning number is {color} {winning_number}"
        #print(f"Debug: Angle: {angle}, Index: {segment_index}, Number: {winning_number}")
        game_state = 'result'
        display_result()  # Call display_result to show the winning number
    rad_angle = math.radians(angle)
    ball_position = (
        int(wheel_center[0] + math.cos(rad_angle) * (wheel_radius - ball_radius)),
        int(wheel_center[1] + math.sin(rad_angle) * (wheel_radius - ball_radius)))



def draw_bet_amount():
    bet_text = f"Current Bet: £{bet_amount}"
    bet_display = font.render(bet_text, True, WHITE)
    bet_rect = bet_display.get_rect(left=10, top=60)  # Position it on the screen as needed
    screen.blit(bet_display, bet_rect)


def update_bet_display():
    bet_text = f"Current Bet: £{bet_amount}"
    screen.fill(BACKGROUND_COLOR)
    bet_display = font.render(bet_text, True, WHITE)
    bet_rect = bet_display.get_rect(left=10, top=60)
    screen.blit(bet_display, bet_rect)
    pygame.display.flip()


def update_balance_and_reset():
    global player_balance, winning_number, bet_type, bet_choice, bet_amount, game_state
    if bet_placed:
        won = False
        if bet_type == 'color' and ((bet_choice == 'red' and winning_number in red_numbers) or (bet_choice == 'black' and winning_number in black_numbers)):
            won = True
        elif bet_type == 'evenodd' and ((bet_choice == 'even' and winning_number % 2 == 0) or (bet_choice == 'odd' and winning_number % 2 != 0)):
            won = True
        elif bet_type == 'number' and bet_choice == str(winning_number):
            won = True

        if won:
            if bet_type == 'number':
                winnings = bet_amount * 35  # Paying 35 to 1 for straight-up bet
            else:
                winnings = bet_amount * 2  # Paying 1 to 1 for color or even/odd bet
            player_balance += winnings  # Adding winnings and refunding the initial bet amount
            result_text = f"You won £{winnings}!"
        else:
            result_text = "You lost!"  # No need to deduct bet_amount as it was already deducted

        result_text = font.render(result_text, True, WHITE)
        result_rect = result_text.get_rect(center=(screen_width / 2, screen_height / 2 + 30))
        screen.blit(result_text, result_rect)
        pygame.display.flip()
        pygame.time.wait(2000)

    reset_game()


def reset_game():
    global angle, player_balance, bet_amount, bet_type, bet_choice, game_state, current_speed, bet_placed, winning_text
    player_balance = player_balance
    bet_amount = 50
    bet_type = None
    bet_choice = None
    game_state = 'betting'
    current_speed = 0
    angle = 0
    bet_placed = False
    winning_text = ""


def display_result():
    if game_state == 'result':
        # Redraw the ball in final position
        draw_ball()  # Ensure the ball is drawn in its final position

        # Display the result text
        result_text = font.render(winning_text, True, WHITE)
        result_rect = result_text.get_rect(center=(screen_width / 2, screen_height / 2))
        screen.blit(result_text, result_rect)
        pygame.display.flip()

        # Pause to allow players to see the result
        pygame.time.wait(2000)

        # Update the balance and reset the game
        update_balance_and_reset()


def roulette_game_loop():
    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)
        handle_key_events()
        draw_wheel()
        draw_current_bet()
        draw_bet_amount()
        if game_state == 'spinning':
            spin_wheel()
            draw_ball()
        elif game_state == 'result':
            display_result()
        elif handle_key_events() == False:
            main_menu()
            running = False


        pygame.display.flip()
        pygame.time.wait(10)

# Screen dimensions and setup
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Define symbol sizes and load images, resizing them
SYMBOL_SIZE = (80, 120)  # Desired width and height of symbol images
symbols_images = {
    name: pygame.transform.scale(pygame.image.load(resource_path(f"PNGS/{name}.png")), SYMBOL_SIZE)
    for name in ["banana", "cherry", "orange", "apple", "seven"]
}


# Define slots and positions
slot_positions = [
    (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 100),
    (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 - 100),
    (SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT // 2 - 100),
]

# Payouts and player balance
payouts = {"banana": 50, "cherry": 250, "orange": 1000, "apple": 1800, "seven": 1000000}


# Initial last spun symbols
last_spin_symbols = [None, None, None]
outcome_message = ""

def spin_reels():
    symbols = ["banana", "cherry", "orange", "apple", "seven"]
    weights = [40, 30, 20, 10, 1]  # banana is most common, seven is rarest
    return [random.choices(symbols, weights)[0] for _ in range(3)]

def calculate_payout(symbols):
    if len(set(symbols)) == 1:
        return payouts[symbols[0]]
    return 0

def draw_slot_machine(spin_active):
    # Main body of the slot machine
    pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 150, 300, 300))
    pygame.draw.rect(screen, DARK_GRAY, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 - 140, 280, 280))

    # Slots for symbols
    for x, y in slot_positions:
        pygame.draw.rect(screen, WHITE, (x, y, SYMBOL_SIZE[0], SYMBOL_SIZE[1]))

    # Control panel
    pygame.draw.rect(screen, LIGHT_GRAY, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 160, 300, 30))
    button_color = GREEN if spin_active else RED
    pygame.draw.circle(screen, button_color, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 175), 15)
    text_surface = font.render("Press to Spin!", True, WHITE)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200))
    screen.blit(text_surface, text_rect)

def check_button_pressed(pos):
    button_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 175)
    distance = ((pos[0] - button_center[0]) ** 2 + (pos[1] - button_center[1]) ** 2) ** 0.5
    return distance <= 15

def display_balance_and_symbols():
    # Display player balance
    balance_text = font.render(format_balance(player_balance), True, WHITE)
    screen.blit(balance_text, (10, 10))
    # Display outcome message
    outcome_text = font.render(outcome_message, True, YELLOW)
    screen.blit(outcome_text, (10, 40))
    # Display symbols
    for i, symbol in enumerate(last_spin_symbols):
        if symbol:
            symbol_img = symbols_images[symbol]
            screen.blit(symbol_img, slot_positions[i])

def animate_reels():
    global last_spin_symbols, outcome_message, player_balance, spin_active
    spin_active = True  # Ensure spin_active is set to True at the start
    symbols_list = list(symbols_images.keys())
    for _ in range(10):  # Simulate the spinning frames
        for i in range(3):
            last_spin_symbols[i] = random.choice(symbols_list)
        display_balance_and_symbols()
        pygame.display.flip()
        time.sleep(0.1)  # Delay to simulate the spinning animation

    # Perform the final spin to determine the outcome
    last_spin_symbols = spin_reels()
    payout = calculate_payout(last_spin_symbols)
    if payout > 0:
        outcome_message = f"You Win! Payout: £{payout}"
        player_balance += payout
    else:
        outcome_message = "You Lose!"

    spin_active = False  # Set back to False after finishing

def slots_game():
    global player_balance, last_spin_symbols, outcome_message, spin_active
    running = True
    spin_active = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if check_button_pressed(pygame.mouse.get_pos()) and not spin_active:
                    if player_balance >= 20:
                        player_balance -= 20
                        animate_reels()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not spin_active:
                    running = False
                    main_menu()

        screen.fill(BLACK)
        draw_slot_machine(spin_active)
        display_balance_and_symbols()
        pygame.display.flip()

    pygame.quit()
    sys.exit()


skull_img = pygame.image.load(resource_path('PNGS/skull.png')).convert_alpha()
skull_img = pygame.transform.scale(skull_img, (width, height))


class Horse:
    def __init__(self, adjective, noun, colour, x, y):
        self.adjective = adjective
        self.noun = noun
        self.win_probability = random.uniform(0.01, 0.99)
        self.visual_horse = VisualHorse(colour, x, y)
        self.dead = False

    def calculate_odds(self):
        self.odds = 1 / self.win_probability

def create_horses(start_y=50,gap=50):
    adjectives = ["Colourful", "Swift", "Vibrant", "Playful", "Mysterious", "Graceful", "Dynamic", "Energetic", "Captivating", "Whimsical", "Magical", "Prolific", "Noble", "Furious", "Careful", "Corach", "Velvet", "Flimsy", "Long", "Tiny", "Wise", "Artificial", "Rushed", "Angry", "Powerful", "Tricky", "Bling", "Large", "Spontaneous", "Stupid", "Goofy", "Welsh", "Georgian", "Scouse", "Cockney", "Fashionable", "Sweaty", "Chatty", "Rambunctious", "Beaten", "Ferocious", "Naked"]

    nouns = ["Sunshine", "Moonlight", "Ocean", "Forest", "Mountain", "Adventure", "Dream", "Harmony", "Serenity", "Voyage", "Byron", "Kai", "Sigurd", "Loki", "Intelligence", "Yeats", "Rambler", "Dog", "Fella", "Geezer", "Lad", "Aswell", "Work", "Beach", "Elvis", "John", "Sea", "Bird", "Lady" ,"Harry", "Adam", "Luca", "Al", "Jasper", "XL Bully", "Maggie Thatcher", "Lizzie"]

    colours = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255,128,0),(255,255,0), (128,255,0), (0,255,128), (0,255,255), (0,128,255), (128,0,255), (255,0,255), (255,0,128), (128,128,128), (0,0,0), (255,255,255)]

    random.shuffle(adjectives)
    random.shuffle(nouns)
    random.shuffle(colours)
    horses = []
    x = 50

    for i in range(10):

        y = start_y + i * gap  # Calculate Y position based on a starting point and a gap
        colour = colours[i % len(colours)]
        horse = Horse(adjectives[i % len(adjectives)], nouns[i % len(nouns)], colour, x, y)
        horse.calculate_odds()
        horses.append(horse)
        
    return horses


class VisualHorse:
    def __init__(self, color, x, y, width=60, height=30, radius=15):
        self.color = color
        self.rect = pygame.Rect(x, y, width, height)  # Keep the rectangle for the alive state
        self.radius = radius  # Radius for the dead state circle
        self.skull_img = skull_img
    
    def draw(self, surface, dead=False):
        if not dead:
            # Draw the horse as a rectangle if it's alive
            pygame.draw.rect(surface, self.color, self.rect)
        else:
            # Draw the horse as a circle if it's dead
            # The circle's center is the center of the rectangle
            ##center = self.rect.center
            skull_x = self.rect.centerx - self.skull_img.get_width() / 2
            skull_y = self.rect.centery - self.skull_img.get_height() / 2
            surface.blit(self.skull_img, (skull_x, skull_y))
            
            ##pygame.draw.circle(surface, self.color, center, self.radius)

def simulate_race_visual(horses, screen, font, betting_agent, bet_horse):
    global player_balance
    finish_line = screen.get_width() - 100  # Finish line position
    font = pygame.font.Font(None, 36)
    
    race_over = False
    winner = None

    while not race_over:
        screen.fill(BACKGROUND_COLOR)  # Desired background color

        # Draw the finish line
        pygame.draw.line(screen, (255, 0, 0), (finish_line + 60, 0), (finish_line + 60, screen.get_height()), 5)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
        for horse in horses:
            if not horse.dead:
                # Adjust variance for each horse based on its win probability
                # Higher win probability (favorites) results in less variance, and vice versa
                variance_factor = random.uniform(0.01, 1.99 - horse.win_probability)  #variance to boost unfavourites, if horse has 0.99 win probability the most variance can be is 1
                variance = random.uniform(0.5, 1.5 + (variance_factor*0.5))
                base_movement = 3 + (horse.win_probability * 3)
                movement = base_movement * (1.2 * (variance**2))  # Base movement adjusted by variance
                
                deathchance = random.randint(1, int(1000*(horse.odds/2)))
                if deathchance == 1:
                    horse.dead = True 
                if horse.noun == "Maggie Thatcher":
                    horse.dead = True
                
                ###movement = horse.win_probability * 5 + random.randint(1, 3)
                ###horse.visual_horse.rect.x += movement
    
                horse.visual_horse.rect.x += movement
                horse.visual_horse.draw(screen, dead=horse.dead)
    
                if horse.visual_horse.rect.x >= finish_line and not winner:
                    winner = horse
                    race_over = True
                    
            else:
                
                horse.visual_horse.draw(screen, dead=horse.dead)
                

        pygame.display.flip()
        pygame.time.delay(100)

    if winner:
        net_winnings = betting_agent.check_results(winner)  # Get net winnings and update balance
        screen.fill(BACKGROUND_COLOR)  # Maintain background color consistency
        # Re-draw the finish line to keep it visible
        pygame.draw.line(screen, (255, 0, 0), (finish_line + 60, 0), (finish_line + 60, screen.get_height()), 5)
        
        messages = [
            f"The winner is: {winner.adjective} {winner.noun}!",
            f"Your net winnings: {'£{:.2f}'.format(net_winnings)}",
            f"Updated balance: {'£{:.2f}'.format(player_balance)}"
        ]
        for i, message in enumerate(messages):
            text = font.render(message, True, (255, 255, 255))
            screen.blit(text, (100, 100 + i * 30))
        
        pygame.display.flip()
        pygame.time.delay(5000)


class Bookies:
    def __init__(self):
        self.bets = {}
        self.bet_amount = 0  # Track the amount bet for the current race

    def place_bet(self, horse, amount):
        global player_balance
        self.bets[horse] = amount
        self.bet_amount = amount
        player_balance -= amount  # Deduct the bet amount from global balance

    def check_results(self, winner):
        global player_balance
        if winner in self.bets:
            winnings = self.bets[winner] * winner.odds
            player_balance += winnings
            return winnings - self.bet_amount  # Return net winnings
        else:
            return -self.bet_amount  # Lost the bet, already deducted earlier

            

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Horse Racing Game")

# Initialize the font for text rendering
pygame.font.init()
font = pygame.font.SysFont(None, 24)

# Function to create and display horses for selection
def display_horses(horses, screen):
    screen.fill((0, 0, 0))
    y_start = 20
    for index, horse in enumerate(horses):
        text = font.render(f"{index + 1}. {horse.adjective} {horse.noun}: Odds - {horse.odds:.2f}", True, (255, 255, 255))
        screen.blit(text, (20, y_start + (index * 30)))
    pygame.display.flip()
    
def get_betting_amount(screen, font, betting_amount):
    input_str = str(betting_amount)  # Convert initial amount to string
    input_active = True

    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False  # Exit loop when Enter is pressed
                elif event.key == pygame.K_BACKSPACE:
                    input_str = input_str[:-1]  # Remove last character
                elif event.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                    input_str += event.unicode  # Add character to input_str
                # Optionally, handle other keys (e.g., to allow decimal points or clear the input)
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    main_menu()

        screen.fill((BACKGROUND_COLOR))  # Clear screen (or set a specific background)
        prompt_text = font.render("Enter your bet amount and press Enter:", True, (WHITE))
        ESC_text = font.render("Or press ESC to return to main menu.", True, (WHITE))
        input_text = font.render(input_str, True, (WHITE))
        screen.blit(prompt_text, (50, 100))
        screen.blit(input_text, (50, 150))
        screen.blit(ESC_text, (50, 200))
        pygame.display.flip()

    return int(input_str) if input_str.isdigit() else 0
    
    
    
def display_horses_for_betting(horses, screen, font):
    y_start = 50
    gap = 40
    selected_horse = None
    betting_amount = 100  # Example fixed bet amount, could be made dynamic

    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)  # Clear screen with background color

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_horse = max(0, selected_horse - 1) if selected_horse is not None else 0
                elif event.key == pygame.K_DOWN:
                    selected_horse = min(len(horses) - 1, selected_horse + 1) if selected_horse is not None else 0
                elif event.key == pygame.K_RETURN and selected_horse is not None:
                    betting_amount = get_betting_amount(screen, font, betting_amount)
                    running = False  # Proceed to bet on the selected horse

        for index, horse in enumerate(horses):
            color_text = "Selected" if index == selected_horse else "Not Selected"
            horse_text = f"{index + 1}. {horse.adjective} {horse.noun} - Odds: {horse.odds:.2f} - {color_text}"
            text_surface = font.render(horse_text, True, (255, 255, 255))
            screen.blit(text_surface, (50, y_start + index * gap))

            # Draw a color block for each horse
            pygame.draw.rect(screen, horse.visual_horse.color, pygame.Rect(10, y_start + index * gap, 30, 20))

        pygame.display.flip()

    # Return the selected horse and betting amount
    return horses[selected_horse], betting_amount

def end(screen, font):
    screen.fill(BACKGROUND_COLOR)
    
    # Display options
    play_again_text = font.render("Press 'P' to play again or 'C' to cash out and exit.", True, (255, 255, 255))
    text_rect = play_again_text.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))
    screen.blit(play_again_text, text_rect)
    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return True  # User chose to play again
                elif event.key == pygame.K_c:
                    return False  # User chose to cash out

def bankrupt(screen, font):
    message = "Well done! You've lost the mortgage, the wife and kids have left'. Press any key to exit."
    text = font.render(message, True, (255, 255, 255))
    screen.fill(BACKGROUND_COLOR)  # Clear the screen or set to a game over background
    screen.blit(text, (100, screen_height // 2))
    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN):
                waiting_for_input = False

# Main game function
def horse_racing_game():
    global player_balance
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Horse Racing Game")
    font = pygame.font.SysFont(None, 24)

    running = True
    betting_agent = Bookies()

    while running:
        horses = create_horses()
        horses = sorted(horses, key=lambda x: x.odds, reverse=False)# Assuming this returns a list of horse objects properly initialized

        chosen_horse, bet_amount = display_horses_for_betting(horses, screen, font)
        betting_agent.place_bet(chosen_horse, bet_amount)

        simulate_race_visual(horses, screen, font, betting_agent, chosen_horse)
        
        if player_balance <= 0:
            print("Game over! You've lost the mortgage and the wife and kids have left.")
            bankrupt(screen, font)  # Assume end_game is a function that handles game over scenario
            break  # Exit the game loop
        
        play_again = end(screen,font)
        if not play_again:
            print(f"Final balance: £{player_balance:.2f}")
            running = False

if __name__ == "__main__":
    main_menu()