'''
Created on 06.03.2020

@author: JanB-4096
'''
import pygame
from src import GameConfig
import time
import numpy as np
from src.NPCControl import NPCControl


pygame.init()
GameDisplay = pygame.display.set_mode(size=(GameConfig.display_width, GameConfig.display_hight))
pygame.display.set_caption('PONG!')
game_clock = pygame.time.Clock()


def place_bar(player,y):
    if player is 'p1':
        pygame.draw.rect(GameDisplay, GameConfig.color_white, (GameConfig.startpoint_bar_p1[0],y,\
                                                               GameConfig.bar_width,GameConfig.bar_hight))
    elif player is 'p2':
        pygame.draw.rect(GameDisplay, GameConfig.color_white, (GameConfig.startpoint_bar_p2[0],y,\
                                                               GameConfig.bar_width,GameConfig.bar_hight))
        
def place_ball(position):
    pygame.draw.circle(GameDisplay, GameConfig.color_white, (int(position[0]), int(position[1])), \
                       GameConfig.ball_radius, 0)
    
def check_boundaries_bar(position_y):
    if position_y + GameConfig.bar_hight > GameConfig.display_hight:
        position_y = GameConfig.display_hight - GameConfig.bar_hight
    elif position_y < 0:
        position_y = 0
    return position_y

def check_boundaries_ball(position, velocity):
    result = 0
    if position[1] + GameConfig.ball_radius > GameConfig.display_hight:
        position[1] = GameConfig.display_hight - GameConfig.ball_radius
        velocity[1] *= -1
    elif position[1] < 0:
        position[1] = 0
        velocity[1] *= -1
    if position[0] + GameConfig.ball_radius > GameConfig.display_width:
        result = 1
    elif position[0] < 0:
        result = 2
    return position, velocity, result

def check_hit(position, velocity, position_p1, position_p2, hit_count):
    # check x position for player 1, either ball in first 3 pixel of the bar or 
    if (GameConfig.bar_p1_center_x <= position[0] and \
        GameConfig.bar_p1_center_x >= position[0] + velocity[0]):
        
        # check y position
        if position[1] + GameConfig.ball_radius >= position_p1 and\
            position[1] - GameConfig.ball_radius <= position_p1 + GameConfig.bar_hight:
            hit_count += 1
            if hit_count % 5 == 0:
                velocity[0] = -1*velocity[0] + GameConfig.acceleration_ball[1]
                position[0] = GameConfig.bar_p1_center_x + GameConfig.bar_width/2 + GameConfig.ball_radius
            else:
                velocity[0] *= -1
                position[0] = GameConfig.bar_p1_center_x + GameConfig.bar_width/2 + GameConfig.ball_radius
            
            # specify y position and add extra y velocity
            if position[1] <= position_p1 + GameConfig.bar_hight/3:
                velocity[1] -= GameConfig.acceleration_ball[1]
            elif position[1] >= position_p1 + 2*GameConfig.bar_hight/3:
                velocity[1] += GameConfig.acceleration_ball[1]
            
    # check x position for player 2      
    elif (GameConfig.bar_p2_center_x >= position[0] + GameConfig.ball_radius and \
        GameConfig.bar_p2_center_x <= position[0] + GameConfig.ball_radius + velocity[0] ):
        
        # check y position
        if position[1] + GameConfig.ball_radius >= position_p2 and\
            position[1] - GameConfig.ball_radius <= position_p2 + GameConfig.bar_hight:
            hit_count += 1
            if hit_count % 5 == 0:
                velocity[0] = -1*velocity[0] - GameConfig.acceleration_ball[1]
                position[0] = GameConfig.bar_p2_center_x - GameConfig.bar_width/2 - GameConfig.ball_radius
            else:
                velocity[0] *= -1
                position[0] = GameConfig.bar_p2_center_x - GameConfig.bar_width/2 - GameConfig.ball_radius
            
            # specify y position and add extra y velocity
            if position[1] <= position_p2 + GameConfig.bar_hight/3:
                velocity[1] -= GameConfig.acceleration_ball[1]
            elif position[1] >= position_p2 + 2*GameConfig.bar_hight/3:
                velocity[1] += GameConfig.acceleration_ball[1]
            
    return position, velocity, hit_count

def text_objects(text, font, color):
    TextSurface = font.render(text, True, color)
    return TextSurface, TextSurface.get_rect()

def display_message_center(text, font_size):
    text_font = pygame.font.Font(GameConfig.text_font, font_size)
    TextSurface, TextRectangle = text_objects(text, text_font, GameConfig.color_white)
    TextRectangle.center = ((GameConfig.display_width/2), (GameConfig.display_hight/2))
    GameDisplay.fill(GameConfig.color_black)
    GameDisplay.blit(TextSurface, TextRectangle)
    
def display_message_top(text, font_size):
    text_font = pygame.font.Font(GameConfig.text_font, font_size)
    TextSurface, TextRectangle = text_objects(text, text_font, GameConfig.color_white)
    TextRectangle.center = ((GameConfig.display_width/2), font_size/2)
    GameDisplay.fill(GameConfig.color_black)
    GameDisplay.blit(TextSurface, TextRectangle)
    
def display_instructions():
    display_message_top('Player 1 (left) keys: W - S   |   Player 2 (right) keys: Up - Down', 10)
    
def display_winner(player):
    display_message_center('Player ' + str(player) + ' wins!', 100)
    
def initialise_gamefield():
    # initialise game field
    GameDisplay.fill(GameConfig.color_black)
    position_p1 = GameConfig.startpoint_bar_p1[1]
    position_p2 = GameConfig.startpoint_bar_p2[1]
    position_ball = [int(GameConfig.startpoint_ball[0]),int(GameConfig.startpoint_ball[1])]
    place_bar('p1', position_p1)
    place_bar('p2', position_p2)
    place_ball(position_ball)                 
    change_position_p1 = 0
    change_position_p2 = 0
    change_position_ball = [(np.random.randint(0,2)-0.5)*2*GameConfig.startvelocity_ball[0], \
                            (np.random.randint(0,2)-0.5)*2 + GameConfig.startvelocity_ball[1]] # go to random direction
    
    return position_p1, position_p2, position_ball, change_position_p1, change_position_p2, change_position_ball

def game_loop(training_mode = False, p1 = 'human', p2 = 'human', difficulty_p1 = 'easy', difficulty_p2 = 'easy'):

    # initialise game field
    position_p1, position_p2, position_ball, change_position_p1, change_position_p2, change_position_ball = \
        initialise_gamefield()
        
    # initialise player controls
    npc = NPCControl(p1, p2, difficulty_p1, difficulty_p2)

    # actual loop to run the game
    result = 0
    hit_count = 0
    while result == 0:
        
        # check for inputs - even with no human player quitting should be possible
        change_position_p1, change_position_p2 = \
            npc.translate_keyboard(pygame.event.get(), change_position_p1, change_position_p2)
            
        if npc.settings['p1']['mode'] == 'NPC':
            change_position_p1 = npc.calc_linear_npc(position_p1, position_ball, change_position_ball, 'p1')
        
        if npc.settings['p2']['mode'] == 'NPC':
            change_position_p2 = npc.calc_linear_npc(position_p2, position_ball, change_position_ball, 'p2')
        
        # change the position            
        position_p1 += change_position_p1
        position_p1 = check_boundaries_bar(position_p1)
        position_p2 += change_position_p2
        position_p2 = check_boundaries_bar(position_p2)
        position_ball = np.add(position_ball, change_position_ball)
        position_ball, change_position_ball, result = check_boundaries_ball(position_ball, change_position_ball)
        position_ball, change_position_ball, hit_count = \
            check_hit(position_ball, change_position_ball, position_p1, position_p2, hit_count)
                
        # update game screen
        GameDisplay.fill(GameConfig.color_black)
        display_instructions()
        place_bar('p1', position_p1)
        place_bar('p2', position_p2)
        place_ball(position_ball)         
        
        # check for a winner
        if result == 1 and not training_mode:
            display_winner(1)  
            pygame.display.update()
            time.sleep(2)
        elif result == 2 and not training_mode:
            display_winner(2)  
            pygame.display.update()
            time.sleep(2)
        else:   
            pygame.display.update()
        
        game_clock.tick(60)
        
        # restart or end the game
        if result != 0:
            display_message_center('Restart? [y/n]', 50)
            pygame.display.update()
            while True:
                event = pygame.event.wait()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_y:
                        game_loop(training_mode, p1, p2, difficulty_p1, difficulty_p2)
                    elif event.key == pygame.K_n:
                        pygame.quit()
                        quit() 
                elif event.type == pygame.QUIT:
                        pygame.quit()
                        quit()            
        