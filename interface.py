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
        button_img = pygame.image.load("button.png").convert_alpha()
        title_img = pygame.image.load("title.png").convert_alpha()
    except pygame.error as e:
        print(f"Erreur : Impossible de charger une image. {e}")
        sys.exit()

    # Scale assets
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    img_left = pygame.transform.scale(img_left, (200, 400))
    img_right = pygame.transform.scale(img_right, (200, 400))
    button_img = pygame.transform.scale(button_img, (200, 80))
    title_img = pygame.transform.scale(title_img, (400, 100))  # Adjust title size as needed

    # Button position
    button_rect = button_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))

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
                if button_rect.collidepoint(event.pos):
                    # Start the game when the button is clicked
                    main()
                    running = False

        # Draw the interface
        screen.blit(background, (0, 0))
        screen.blit(title_img, title_rect)  # Draw the title
        screen.blit(img_left, (50, HEIGHT // 2 - 200))
        screen.blit(img_right, (WIDTH - 250, HEIGHT // 2 - 200))
        screen.blit(button_img, button_rect)

        pygame.display.flip()

if __name__ == "__main__":
    run_interface()
