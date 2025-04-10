import pygame
import sys
from minmaxEnhanced import main  # Import the main game function

def run_interface():
    pygame.init()

    # Screen dimensions
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Breakthrough Interface")

    # Load assets
    try:
        background = pygame.image.load("background.png").convert()
        img_left = pygame.image.load("imgLeft.png").convert_alpha()
        img_right = pygame.image.load("imgRight.png").convert_alpha()
        button_easy = pygame.image.load("buttonEasy.png").convert_alpha()
        button_mid = pygame.image.load("buttonMid.png").convert_alpha()
        button_hard = pygame.image.load("buttonHard.png").convert_alpha()
        button_human_vs_human = pygame.image.load("buttonHumanVsHuman.png").convert_alpha()
        title_img = pygame.image.load("title.png").convert_alpha()
    except pygame.error as e:
        print(f"Erreur : Impossible de charger une image. {e}")
        sys.exit()

    # Scale assets
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    img_left = pygame.transform.scale(img_left, (200, 400))
    img_right = pygame.transform.scale(img_right, (200, 400))
    button_easy = pygame.transform.scale(button_easy, (200, 110))
    button_mid = pygame.transform.scale(button_mid, (200, 110))
    button_hard = pygame.transform.scale(button_hard, (200, 110))
    button_human_vs_human = pygame.transform.scale(button_human_vs_human, (200, 110))
    title_img = pygame.transform.scale(title_img, (500, 150))  # Adjust title size as needed

    # Button positions
    button_rect_easy = button_easy.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
    button_rect_mid = button_mid.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
    button_rect_hard = button_hard.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    button_rect_human_vs_human = button_human_vs_human.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))

    # Update button rectangles to match scaled images
    button_rect_easy.size = button_easy.get_size()
    button_rect_mid.size = button_mid.get_size()
    button_rect_hard.size = button_hard.get_size()
    button_rect_human_vs_human.size = button_human_vs_human.get_size()

    # Title position
    title_rect = title_img.get_rect(center=(WIDTH // 2, 100))

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect_easy.collidepoint(event.pos):
                    main(mode="AI", difficulty="easy")
                    running = False
                elif button_rect_mid.collidepoint(event.pos):
                    main(mode="AI", difficulty="medium")
                    running = False
                elif button_rect_hard.collidepoint(event.pos):
                    main(mode="AI", difficulty="hard")
                    running = False
                elif button_rect_human_vs_human.collidepoint(event.pos):
                    main(mode="HumanVsHuman")
                    running = False

        # Draw the interface
        screen.blit(background, (0, 0))
        screen.blit(title_img, title_rect)  # Draw the title
        screen.blit(img_left, (50, HEIGHT // 2 - 120))
        screen.blit(img_right, (WIDTH - 250, HEIGHT // 2 - 120))
        screen.blit(button_easy, button_rect_easy.topleft)
        screen.blit(button_mid, button_rect_mid.topleft)
        screen.blit(button_hard, button_rect_hard.topleft)
        screen.blit(button_human_vs_human, button_rect_human_vs_human.topleft)

        pygame.display.flip()

if __name__ == "__main__":
    run_interface()
