'''
Created on 06.03.2020

@author: JanB-4096
'''
import pygame
from src import GameConfig
import time
import numpy as np
from src.NPCControl import NPCControl
import src.NNTools as NNTools
import datetime

import os
import psutil


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

def check_hit(position, velocity, position_p1, position_p2, hit_count_p1, hit_count_p2):
    # check x position for player 1, either ball in first 3 pixel of the bar or 
    if (GameConfig.bar_p1_center_x <= position[0] and \
        GameConfig.bar_p1_center_x >= position[0] + velocity[0]):
        
        # check y position
        if position[1] + GameConfig.ball_radius >= position_p1 and\
            position[1] - GameConfig.ball_radius <= position_p1 + GameConfig.bar_hight:
            hit_count_p1 += 1
            if (hit_count_p1 + hit_count_p2) % 5 == 0:
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
            hit_count_p2 += 1
            if (hit_count_p1 + hit_count_p2) % 5 == 0:
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
            
    return position, velocity, hit_count_p1, hit_count_p2

def text_objects(text, font, color):
    TextSurface = font.render(text, True, color)
    return TextSurface, TextSurface.get_rect()

def display_message_center(text, font_size):
    text_font = pygame.font.Font(GameConfig.text_font, font_size)
    TextSurface, TextRectangle = text_objects(text, text_font, GameConfig.color_white)
    TextRectangle.center = ((GameConfig.display_width/2), (GameConfig.display_hight/2))
    GameDisplay.fill(GameConfig.color_black)
    GameDisplay.blit(TextSurface, TextRectangle)
    
def display_message_top(text, font_size, offset_hight = 0):
    text_font = pygame.font.Font(GameConfig.text_font, font_size)
    TextSurface, TextRectangle = text_objects(text, text_font, GameConfig.color_white)
    TextRectangle.center = ((GameConfig.display_width/2), font_size/2 + offset_hight)
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
        
    if npc.settings['p1']['mode'] == 'NPC' and npc.settings['p1']['difficulty'] == 'ai':
        species = NNTools.load_obj_from_file(GameConfig.nn_player_file)
        if species == None:
            npc.settings['p1']['difficulty'] = 'very_hard'

    # actual loop to run the game
    result = 0
    hit_count_p1 = 0
    hit_count_p2 = 0
    while result == 0:
        
        # check for inputs - even with no human player quitting should be possible
        change_position_p1, change_position_p2 = \
            npc.translate_keyboard(pygame.event.get(), change_position_p1, change_position_p2)
            
        if npc.settings['p1']['mode'] == 'NPC':
            if npc.settings['p1']['difficulty'] == 'ai':
                change_position_p1 = npc.calc_ai_p1(position_p1, position_ball, change_position_ball, species)
            else:
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
        position_ball, change_position_ball, hit_count_p1, hit_count_p2 = \
            check_hit(position_ball, change_position_ball, position_p1, position_p2, hit_count_p1, hit_count_p2)
                
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
                        
                        
def training_loop(p1 = 'NPC', p2 = 'NPC', difficulty_p1 = 'AI', difficulty_p2 = 'very_hard'):
    #initialize neuro evolution
    #ne = NNTools.NeuroEvolution(20, [5, 20, 25, 10, 2], ['sigmoid','sigmoid','sigmoid','softmax'])
    ne = NNTools.NeuroEvolution(50, [5, 20, 15, 2], ['sigmoid','sigmoid','softmax'])
    ne.fraction_mutation_activation = 1/ne.population.__len__()
    ne.check_next_gen_fractions()
    species_id = 0
    threshold = 10
    
    # initialise player controls
    npc = NPCControl(p1, p2, difficulty_p1, difficulty_p2)
    
    while True:
        species = ne.population[species_id]
    
        # initialise game field
        position_p1, position_p2, position_ball, change_position_p1, change_position_p2, change_position_ball = \
            initialise_gamefield()
            
        # actual loop to run the game
        result = 0
        hit_count_p1 = 0
        hit_count_p2 = 0
        while result == 0:
            
            # check for inputs - even with no human player quitting should be possible
            change_position_p1, change_position_p2 = \
                npc.translate_keyboard(pygame.event.get(), change_position_p1, change_position_p2)
                
            
            change_position_p1 = npc.calc_ai_p1(position_p1+GameConfig.bar_hight/2, position_ball, change_position_ball, species)
            
            change_position_p2 = npc.calc_linear_npc(position_p2, position_ball, change_position_ball, 'p2')
            
            # change the position            
            position_p1 += change_position_p1
            position_p1 = check_boundaries_bar(position_p1)
            position_p2 += change_position_p2
            position_p2 = check_boundaries_bar(position_p2)
            position_ball = np.add(position_ball, change_position_ball)
            position_ball, change_position_ball, result = check_boundaries_ball(position_ball, change_position_ball)
            position_ball, change_position_ball, hit_count_p1, hit_count_p2 = \
                check_hit(position_ball, change_position_ball, position_p1, position_p2, hit_count_p1, hit_count_p2)
                    
            # update game screen
            GameDisplay.fill(GameConfig.color_black)
            display_instructions()
            display_message_top('Generation: {}'.format(ne.generation), 10,15)
            display_message_top('Fitness: {}'.format(ne.fitness_list), 10, 25)
            place_bar('p1', position_p1)
            place_bar('p2', position_p2)
            place_ball(position_ball)   
            
            pygame.display.update()
            game_clock.tick(20000)
            
            # restart or end the game
            if result != 0:
                if result == 1:
                    hit_count_p1 *= 2
                ne.update_fitness(hit_count_p1, species_id)
                species_id += 1   
                
            if species_id >= len(ne.population):
                species_id = 0
                ne.generation_overview.update({ne.generation: ne.fitness_list})
                print("Generation: {} with fitness: {}".format(ne.generation, ne.generation_overview[ne.generation]))
                ne.generation += 1    
                
                if np.any(ne.fitness_list >= threshold):
                    # save nn and ne
                    threshold = ne.best_fitness + 1
                    idx_best_nn = np.where(ne.fitness_list == ne.best_fitness)
                    NNTools.save_obj_to_file(ne.population[idx_best_nn[0][0]], GameConfig.nn_player_file+'_'+str(ne.best_fitness)+'_'+str(datetime.date.today()))
                    if np.any(ne.fitness_list >= 50):
                        NNTools.save_obj_to_file(ne, GameConfig.ne_file+'_'+str(ne.best_fitness)+'_'+str(datetime.date.today()))
                        #quit()
                
                # mutation and crossover of the best
                ne.build_next_generation()
                ne.fitness_list = np.zeros(ne.population.__len__())
