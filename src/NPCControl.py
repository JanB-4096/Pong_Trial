'''
Created on 06.03.2020

@author: JanB-4096
'''
from src import GameConfig
import pygame
import numpy as np


class NPCControl():
    
    def __init__(self, p1, p2, p1_difficulty, p2_difficulty):
        self.settings = {'p1': {'mode': p1, 'difficulty': p1_difficulty}, \
                         'p2': {'mode': p2, 'difficulty': p2_difficulty}}

    def translate_keyboard(self, events, change_position_p1, change_position_p2):
        
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    change_position_p1 = -1*GameConfig.change_bar_vertical
                elif event.key == pygame.K_s:
                    change_position_p1 = 1*GameConfig.change_bar_vertical
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w or event.key == pygame.K_s:
                    change_position_p1 = 0  
                                        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    change_position_p2 = -1*GameConfig.change_bar_vertical
                elif event.key == pygame.K_DOWN:
                    change_position_p2 = 1*GameConfig.change_bar_vertical
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    change_position_p2 = 0
                    
        return change_position_p1, change_position_p2
    
    def calc_linear_npc(self, position_p, position_ball, change_ball, player):
        change_position_p = 0
        
        if self.settings[player]['difficulty'] == 'middle':
            if position_p + 2*GameConfig.bar_hight/5 >= position_ball[1]:
                change_position_p = -1*GameConfig.change_bar_vertical
            elif position_p + 3*GameConfig.bar_hight/5 <= position_ball[1]:
                change_position_p = GameConfig.change_bar_vertical
        elif self.settings[player]['difficulty'] == 'easy':
            if position_p >= position_ball[1]:
                change_position_p = -1*GameConfig.change_bar_vertical
            elif position_p + GameConfig.bar_hight <= position_ball[1]:
                change_position_p = GameConfig.change_bar_vertical
        elif self.settings[player]['difficulty'] == 'very_hard':
            timesteps_until_hit = 0
            
            if change_ball[0] > 0 and player == 'p2': #going right
                timesteps_until_hit = np.abs((position_ball[0] - GameConfig.startpoint_bar_p2[0]) / (change_ball[0]))
            elif change_ball[0] < 0 and player == 'p1':
                timesteps_until_hit = np.abs((position_ball[0] - GameConfig.startpoint_bar_p1[0] + GameConfig.bar_width) / (change_ball[0]))
            
            if timesteps_until_hit != 0:    
                predicted_y_ball = position_ball[1] + change_ball[1]*timesteps_until_hit
                if predicted_y_ball > GameConfig.display_hight:
                    predicted_y_ball = 2*GameConfig.display_hight - predicted_y_ball
                elif predicted_y_ball < 0:
                    predicted_y_ball *= -1
                if position_p  + GameConfig.bar_hight/5 >= predicted_y_ball:
                    change_position_p = -1*GameConfig.change_bar_vertical
                elif position_p + 4*GameConfig.bar_hight/5 <= predicted_y_ball:
                    change_position_p = GameConfig.change_bar_vertical
            if change_ball[0] > 0 and player == 'p1' or change_ball[0] < 0 and player == 'p2': #go back to middle position if ball was hit
                distance_to_center = GameConfig.display_hight/2 - (position_p + GameConfig.bar_hight/2)
                change_position_p = np.sign(distance_to_center) * GameConfig.change_bar_vertical * int((np.abs(distance_to_center) > GameConfig.change_bar_vertical))
                
        else: 
            timesteps_until_hit = 0
            if change_ball[0] > 0 and player == 'p2': #going right
                timesteps_until_hit = np.abs((position_ball[0] - GameConfig.startpoint_bar_p2[0]) / (change_ball[0]))
            elif change_ball[0] < 0 and player == 'p1':
                timesteps_until_hit = np.abs((position_ball[0] - GameConfig.startpoint_bar_p1[0] + GameConfig.bar_width) / (change_ball[0]))
            if timesteps_until_hit != 0:    
                predicted_y_ball = position_ball[1] + change_ball[1]*timesteps_until_hit
                if predicted_y_ball > GameConfig.display_hight:
                    predicted_y_ball = 2*GameConfig.display_hight - predicted_y_ball
                elif predicted_y_ball < 0:
                    predicted_y_ball *= -1
                if position_p  + GameConfig.bar_hight/5 >= predicted_y_ball:
                    change_position_p = -1*GameConfig.change_bar_vertical
                elif position_p + 4*GameConfig.bar_hight/5 <= predicted_y_ball:
                    change_position_p = GameConfig.change_bar_vertical
                   
        return change_position_p
    
    def calc_ai_p1(self, position_p, position_ball, change_ball, species):
        output_nn = species.calculate_output_to_input([position_p, position_ball[0], position_ball[1], change_ball[0], change_ball[1]])
        if output_nn[0] > output_nn[1]: #up
            return -1*GameConfig.change_bar_vertical
        else: #down
            return GameConfig.change_bar_vertical
