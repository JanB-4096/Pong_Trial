'''
Created on 06.03.2020

@author: JanB-4096
'''
display_width = 800
display_hight = 600

bar_width = 10
bar_hight = 80
ball_radius = 6

distance_to_side = 40

color_black = (0,0,0)
color_white = (255,255,255)
color_red = (255,0,0)

text_font = 'freesansbold.ttf'

startpoint_bar_p1 = [distance_to_side, 0.5*display_hight-bar_hight/2] # top left corner of bar, absolute in pixel
startpoint_bar_p2 = [display_width-distance_to_side-bar_width,0.5*display_hight-bar_hight/2]
startpoint_ball = [0.5*display_width,0.5*display_hight] # center of ball

startvelocity_ball = [5,0] #pixel
acceleration_ball = [1,1] #pixel/iteration

change_bar_vertical = 5 # pixel

bar_p1_center_x = startpoint_bar_p1[0] + bar_width/2
bar_p2_center_x = startpoint_bar_p2[0] + bar_width/2

difficulties = ['easy', 'medium', 'hard', 'very_hard']