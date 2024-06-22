# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 12:35:12 2022

@author: Ed.Morris
"""

# import modules
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from mplsoccer import Pitch, VerticalPitch
import streamlit as st
from PIL import Image
import os
import random

st.set_page_config(page_title = 'Wyscout: Serie A Match Analysis', page_icon = Image.open('Serie_A_logo.jpg'), initial_sidebar_state = 'expanded')

font1 = font_manager.FontProperties(family = 'Tahoma')
font = {'fontname':'Tahoma'}

# Set wd path
#rfp_path = r"C:\Users\ed.morris\Documents\Python Scripts\Wyscout"
#os.chdir(rfp_path)

# Read in json to variable 'data'
with open('Sample event data.txt') as json_file:
    data = json.load(json_file)
    
# Convert dictionary to df
df = pd.DataFrame.from_dict(data['events'], orient = 'columns')

# Filter for pass data
pass_df = df[['minute','second','type','location','player','team','pass']]
pass_df = pass_df.rename(columns = {'minute':'minute','second':'second','type':'type','location':'location','player':'player','team':'team','pass':'pass_info'})

# Pull out all relevant data from various columns containing dictionaries
team = [t.get('name') for t in pass_df.team]
x_location = [x.get('x') for x in pass_df.location]
y_location = [y.get('y') for y in pass_df.location]
player = [p.get('name') for p in pass_df.player]
player_pos = [pos.get('position') for pos in pass_df.player]
action = [a.get('primary') for a in pass_df.type]
desc = [d.get('secondary') for d in pass_df.type]

# Add these coords as new cols
pass_df['team'] = team
pass_df['start_x'] = x_location
pass_df['start_y'] = y_location
pass_df['player_name'] = player
pass_df['player_position'] = player_pos
pass_df['action'] = action
pass_df['description'] = desc

# Filter action col for appropriate dataset
passes = pass_df.loc[pass_df.action == 'pass'].reset_index(drop=True)
shots = pass_df.loc[pass_df.action == 'shot'].reset_index(drop=True)

# Pull out pass info now 'None' have been removed from pass_info['accurate']
acc_pass = [e.get('accurate') for e in passes.pass_info]
recipient = [r.get('recipient') for r in passes.pass_info]
end = [end.get('endLocation') for end in passes.pass_info]

# Add pass info as columns
passes['accurate_pass'] = acc_pass
passes['recipient_data'] = recipient
passes['end_coords'] = end

# Pull recipients and coords from dictionaries
recipients = [r.get('name') for r in passes.recipient_data]
x_end = [x.get('x') for x in passes.end_coords]
y_end = [y.get('y') for y in passes.end_coords]

# Add recipient and end coordinates to df
passes['recipient'] = recipients
passes['end_x'] = x_end
passes['end_y'] = y_end

# Drop redundant columns
passes = passes.drop(columns = ['type','location','player','pass_info','end_coords','recipient_data']).reset_index(drop=True)

# Filter for completed passes
completed = passes.loc[passes.accurate_pass == True]

# Unique player list
player_list = completed.player_name.unique()

# Shot data manipulation

# Filter for relevant columns
shot_df = df[['minute','second','type','location','player','team','shot','possession']]
action = [a.get('primary') for a in shot_df.type]
shot_df['action'] = action
shot_data = shot_df.loc[shot_df.action == 'shot']

# Extract all data from dictionaries
x_location = [x.get('x') for x in shot_data.location]
y_location = [y.get('y') for y in shot_data.location]
player_name = [player.get('name') for player in shot_data.player]
desc = [d.get('secondary') for d in shot_data.type]
body_part = [bd.get('bodyPart') for bd in shot_data.shot]
is_goal = [g.get('isGoal') for g in shot_data.shot]
on_target = [ot.get('bodyPart') for ot in shot_data.shot]
xg = [xg.get('xg') for xg in shot_data.shot]
psxg = [psxg.get('postShotXg') for psxg in shot_data.shot]
team = [team.get('name') for team in shot_data.team]

# Assign extracted data to columns 
shot_data['start_x'] = x_location
shot_data['start_y'] = y_location
shot_data['player'] = player_name
shot_data['team'] = team
shot_data['description'] = desc
shot_data['body_part'] = body_part
shot_data['is_goal'] = is_goal
shot_data['on_target'] = on_target
shot_data['xG'] = xg
shot_data['PSxG'] = psxg

# Drop redundant cols
shot_data = shot_data.drop(columns = ['type','shot','location','possession']).reset_index(drop=True)

# Filter goal vs non-goal shots
goals = shot_data.loc[shot_data.is_goal == True]
non_goals = shot_data.loc[shot_data.is_goal == False]

# Create variables for each team
team1, team2 = passes.team.unique()

# Split data to create xG chart across the match
shot_data = shot_data.reset_index(drop = True)


#######################################################################
# Plotting functions
#######################################################################

# Draw passmap using mplsoccer library
def passmap_plot(team,player):
    pitch = Pitch(pitch_type='wyscout', pitch_color = '#1E4966', line_color = '#c7d5cc')
    fig, axs = pitch.grid(endnote_height = 0.03, 
                          endnote_space = 0, 
                          figheight = 16, 
                          title_height = 0.06, 
                          title_space = 0, 
                          grid_height = 0.86, 
                          axis = False)
    fig.set_facecolor('#1E4966')
    
    plt.gca().invert_yaxis()
    
    if player == 'All':
        passes_filtered = passes.loc[passes.team == team].reset_index(drop=True)
    else:
        passes_filtered = passes.loc[(passes.team == team) & (passes.player_name == player)].reset_index(drop=True)
    
    pitch.arrows(passes_filtered.loc[passes_filtered.accurate_pass == True].start_x, passes_filtered.loc[passes_filtered.accurate_pass == True].start_y, passes_filtered.loc[passes_filtered.accurate_pass == True].end_x, passes_filtered.loc[passes_filtered.accurate_pass == True].end_y, 
                 width = 2, 
                 headwidth = 10, 
                 headlength = 10, 
                 color = 'aquamarine', 
                 ax = axs['pitch'],
                 label = 'Başarılı')

    pitch.arrows(passes_filtered.loc[passes_filtered.accurate_pass == False].start_x, passes_filtered.loc[passes_filtered.accurate_pass == False].start_y, passes_filtered.loc[passes_filtered.accurate_pass == False].end_x, passes_filtered.loc[passes_filtered.accurate_pass == False].end_y, 
                 width = 2, 
                 headwidth = 6, 
                 headlength = 5, 
                 headaxislength = 12, 
                 color = 'tomato', 
                 ax = axs['pitch'],
                 label = 'Başarısız')
                
    if player == 'All':
        #plt.title(f'Juventus vs Sampdoria 20/09/2020: {team} pass map', color = 'white', size = 30)
        axs['title'].text(0.5, 0.5, f'Juventus vs Sampdoria 20/09/2020: \n {team} passes', color='#dee6ea',
                  va='center', ha='center', fontsize=25)
    else:
        #plt.title(f'Juventus vs Sampdoria 20/09/2020: {player} pass map', color = 'white', size = 30)
        axs['title'].text(0.5, 0.5, f'Juventus vs Sampdoria 20/09/2020: \n {player} passes', color='#dee6ea',
                  va='center', ha='center', fontsize=25)
    
    legend = axs['pitch'].legend(facecolor = '#01153E', handlelength = 5, edgecolor = 'None', loc = 'upper left', prop = {'size':25})
    frame = legend.get_frame()
    frame.set_facecolor('white')
    frame.set_edgecolor('white')
    
    axs['endnote'].text(1,0.25,'@kanalfutbol | www.kanalfutbol.com.tr',color='white',alpha=0.5,va='center',ha='right',fontsize=20,)
    
    st.pyplot(fig)
    
#passmap_plot('Juventus','A. Ramsey')
    

# Draw shotmap using mplsoccer library
def shotmap_plot(team,player):
    pitch = VerticalPitch(pad_bottom = 0.5,  # pitch extends slightly below halfway line
                      half = True,  # half of a pitch
                      goal_type = 'box',
                      goal_alpha = 0.8,
                      pitch_type = 'wyscout',
                      pitch_color = '#1E4966',
                      line_color = '#c7d5cc')  # control the goal transparency
    fig, ax = pitch.draw(figsize = (12,10))
    
    if team == team1:
        if player == 'All':
            non_goals_filtered = non_goals.loc[non_goals.team == team1]
            goals_filtered = goals.loc[goals.team == team1]
        if player != 'All':
            non_goals_filtered = non_goals.loc[(non_goals.team == team1) & (non_goals.player == player)]
            goals_filtered = goals.loc[(goals.team == team1) & (goals.player == player)]
            
    if team == team2:
        if player == 'All':
            non_goals_filtered = non_goals.loc[non_goals.team == team2]
            goals_filtered = goals.loc[goals.team == team2]
        if player != 'All':
            non_goals_filtered = non_goals.loc[(non_goals.team == team2) & (non_goals.player == player)]
            goals_filtered = goals.loc[(goals.team == team2) & (goals.player == player)]
    
    # Plot non-goal shots with hatches
    scat_1 = pitch.scatter(non_goals_filtered.start_x,non_goals_filtered.start_y,
                           # Size varies based on xG
                           s = (non_goals_filtered.xG * 1900) + 100,
                           edgecolors = '#b94b75', # Give markers a charcoal border
                           c = 'None', # No facecolours for the markers
                           hatch = '///', # hatched pattern for the markers
                           marker = 'o',
                           ax = ax)
    
    scat_2 = pitch.scatter(goals_filtered.start_x,goals_filtered.start_y,
                           # Size varies based on xG
                           s = (goals_filtered.xG * 1900) + 100,
                           edgecolors = '#b94b75',
                           #linewidth = 0.6,
                           c = 'white',
                           marker = 'football',
                           ax = ax)
    
    ax.text(45.8, 82.6, '@kanalfutbol | www.kanalfutbol.com.tr', color = 'white', alpha = 0.5)
    
    if player == 'All':
        txt = ax.text(x = 50, y = 65, s = f'Juventus vs Sampdoria 20/09/2020:\n {team} shot map', fontname = 'Tahoma', size = 20, va = 'center', ha = 'center', color = 'white')
    if player != 'All':
        txt = ax.text(x = 50, y = 65, s = f'Juventus vs Sampdoria 20/09/2020:\n {player} shot map', fontname = 'Tahoma', size = 20, va = 'center', ha = 'center', color = 'white')
    
    st.pyplot(fig)

#shotmap_plot('Juventus','All')

# Create new df for xG and mins, create actual minute col (minute + 1) and filter for each team
xG_vs_mins = shot_data[['minute','second','team','xG']]
xG_vs_mins['actual_minute'] = xG_vs_mins.minute + 1
juve_xg = xG_vs_mins.loc[xG_vs_mins['team'] == 'Juventus'].reset_index(drop=True)
sampd_xg = xG_vs_mins.loc[xG_vs_mins['team'] == 'Sampdoria'].reset_index(drop=True)
print(juve_xg)


# Create xG per minute for Juventus
xg_to_plot1 = [0]
j = 0
for min in range(1,91):
    if min == juve_xg['actual_minute'][j]:
        if j == len(juve_xg.actual_minute) - 1:
            xg_to_plot1.append(juve_xg['xG'][j] + xg_to_plot1[min-1])
        elif j < len(juve_xg) - 1:
            if juve_xg['actual_minute'][j] == juve_xg['actual_minute'][j+1]:
                xg_to_plot1.append(juve_xg['xG'][j] + juve_xg['xG'][j+1] + xg_to_plot1[min-1])
                j += 2
            else:
                xg_to_plot1.append(juve_xg['xG'][j] + xg_to_plot1[min-1])
                j += 1
    else:
        xg_to_plot1.append(xg_to_plot1[min-1])
        
print(xg_to_plot1)
print(len(xg_to_plot1))

# Create xG per minute for Sampdoria
xg_to_plot2 = [0]
j = 0
for min in range(1,91):
    if min == sampd_xg['actual_minute'][j]:
        if j == len(sampd_xg.actual_minute) - 1:
            xg_to_plot2.append(sampd_xg['xG'][j] + xg_to_plot2[min-1])
        elif j < len(sampd_xg) - 1:
            if sampd_xg['actual_minute'][j] == sampd_xg['actual_minute'][j+1]:
                xg_to_plot2.append(sampd_xg['xG'][j] + sampd_xg['xG'][j+1] + xg_to_plot2[min-1])
                j += 2
            else:
                xg_to_plot2.append(sampd_xg['xG'][j] + xg_to_plot2[min-1])
                j += 1
    else:
        xg_to_plot2.append(xg_to_plot2[min-1])

print(xg_to_plot2)
print(len(xg_to_plot2))

x = 0
for i in range(0,14):
    x += juve_xg.xG[i]

print(x) # 2.2507932


# xG chart
def xg_chart():
    fig, ax = plt.subplots(1,1)
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    plt.plot(np.linspace(0,90,num=91),xg_to_plot1,label = 'Juventus xG', color = 'white')
    plt.plot(np.linspace(0,90,num=91),xg_to_plot2,label = 'Sampdoria xG', color = 'purple')
    ax = plt.gca()
    ax.set_facecolor('#1E4966')
    ax.spines['left'].set_color('white') 
    ax.spines['bottom'].set_color('white') 
    ax.spines['right'].set_color('white')
    ax.spines['top'].set_color('#1E4966')
    ax.tick_params(axis='x', colors='white')    #setting up X-axis tick color to red
    ax.tick_params(axis='y', colors='white', labelright = True)
    ax.text(40,2.5,'@kanalfutbol | www.kanalfutbol.com.tr', color = 'white', alpha = 0.5, size = 8)
    fig.patch.set_facecolor('#1E4966')
    plt.xticks(np.arange(0,90+1,5))
    plt.xlabel('Minute', color = 'white',**font)
    plt.ylabel('xG', color = 'white',**font)
    plt.title(f'Juventus [{round(juve_xg.xG.sum(),2)}] vs [{round(sampd_xg.xG.sum(),2)}] Sampdoria:\nxG generated over match', color = 'white',**font)
    plt.legend(prop = font1)
    plt.rcParams['figure.dpi'] = 800
    st.pyplot(fig)




# ==========================================================
# Dashboard configuration
# ==========================================================

add_sidebar = st.sidebar.selectbox('Select Page', ('Intro','xG Flow Chart','Shot maps','Pass maps','tbl'))

if add_sidebar == 'Intro':
    st.header("""
             Serie A Match Analysis: Juventus 3 - 0 Sampdoria (10/09/2020)
             \n By Ed Morris
             """)
    st.markdown("""
                **Navgating the dashboard:** 
                \n- Use the arrow in the top left to open the sidebar
                \n- Select a page from the drop-down bar to move between analyses
                \n**Aims of this dashboard:**
                \n- This is a brief dashboard demonstrating Wyscout event data manipulation and corresponding data visualisations using the free Wyscout event data for the Serie A match Juventus - Sampdoria on 10th September 2020.
                \n- Here, I hope to demonstrate my ability to use this event data to create visually appealing graphics that can be used to analyse individual player performance, team performance and provide data-driven metrics where appropriate.
                \nThe data used for this can be found here: https://footballdata.wyscout.com/download-samples/
                """)


if add_sidebar == 'xG Flow Chart':
    st.title('xG Flow Chart')
    xg_chart()
    st.caption('xG flow chart showing xG generated across the course of the match. Commentary below.')
    st.markdown("""
                - This xG flow chart shows how the shooting opportunities created by each team varied over the course of the match.
                \n- Juventus were the team on the offensive for the majority of the match, due to the continuously bumpy xG line showing they created shooting opportunities (even if only small) fairly frequently.
                \n- Also clear to see Sampdoria were the defensive/counter-attacking team for large periods of the match due to long periods of a stagnant xG line. 
    - This shows that they were only creating shooting opportunities fairly infrequently, for example having 0 xG generated for the first 25 minutes of the match.
                \n- Can possibly infer from this chart a question over the fitness/concentration of the Sampdoria defence towards the end of the match. 
    - Between the 75th and 80th minutes of the match, Juventus were able to generate over 1 xG in this 5 minute period, which could be due to a lack of fitness or concentration in the later stages of the match. 
    - Alternatively, this could demonstrate the superior fitness of the Juventus attackers, or positive substitutions made to attack a tiring Sampdoria defence.
                \n- It is important to note however that a sample size of one match is not adequate to draw such large conclusions, we would need to see this pattern occurring over 10s of matches to be able to conclude any hard insights from this type of graphic.
                """)
    
if add_sidebar == 'Shot maps':
    st.title('Shot map plots (by team/player)')
    teams = tuple(xG_vs_mins.team.unique())
    teams_select = st.selectbox('Select a team', (teams))
    
    if teams_select == 'Juventus':
        players = tuple(np.append('All', shot_data.loc[shot_data.team == 'Juventus']['player'].unique()))
        players_select = st.selectbox('Select a player', (players))
        shotmap_plot(teams_select, players_select)
        st.markdown("""
                    The graphic above shows that Juventus created xG opportunities from 15 different shots, scoring 3 goals (shown by the football shapes on the diagram).
                    \n 
                    """)
        col13, col14, col15 = st.columns(3)
        col13.metric(label = '% shots in box', value = f"{11/15:.0%}")
        col14.metric(label = 'Total xG created', value = f"{round(xg_to_plot1[90],2)}")
        col15.metric(label = 'Largest xG created (1 event)', value = f"{round(juve_xg.xG.max(),2)}")

    if teams_select == 'Sampdoria':
        players = tuple(np.append('All', shot_data.loc[shot_data.team == 'Sampdoria']['player'].unique()))
        players_select = st.selectbox('Select a player', (players))
        shotmap_plot(teams_select, players_select)
        st.markdown("""
                    The graphic above shows that Sampdoria created xG opportunities from 13 different shots, scoring 0 goals (shown by no football shapes on the diagram).
                    """)
        col10, col11, col12 = st.columns(3)
        col10.metric(label = '% shots in box', value = f"{7/13:.0%}")
        col11.metric(label = 'Total xG created', value = f"{round(xg_to_plot2[90],2)}")
        col12.metric(label = 'Largest xG created (1 event)', value = f"{round(sampd_xg.xG.max(),2)}")


if add_sidebar == 'Pass maps':
    st.title('Pass map plots (by player/team)')
    teams1 = tuple(xG_vs_mins.team.unique())
    teams1_select = st.selectbox('Select a team', (teams1))
    
    if teams1_select == 'Juventus':
        players1 = tuple(np.append('All', passes.loc[passes.team == 'Juventus']['player_name'].unique()))
        players1_select = st.selectbox('Select a player', (players1))
        passmap_plot(teams1_select, players1_select)
        st.markdown("""
                    These pass maps can be used to highlight passing patterns on a individual or team basis.
                    \nFurther developments upon this interactive passing page could be:
                    \n- Segment the pitch into channels or dangerous sectors, collating pass data to these areas of the pitch to draw insights regarding dangerous passes
                    \n- Create passing networks to understand passing patterns across the team between players
    - This can demonstrate relationships between players on the pitch and where these can be improved to implement coaching tactics more effectively
                    \n- Highlight progressive passes (based on varying defintions by data provider or "in-club" definition of progressive pass)
                    
                    """)

    if teams1_select == 'Sampdoria':
        players2 = tuple(np.append('All', passes.loc[passes.team == 'Sampdoria']['player_name'].unique()))
        players2_select = st.selectbox('Select a player', (players2))
        passmap_plot(teams1_select, players2_select)


if add_sidebar == 'tbl':
    dftable = pd.DataFrame(
        {
            "name": ["Roadmap", "Extras", "Issues"],
            "url": ["https://roadmap.streamlit.app", "https://extras.streamlit.app", "https://issues.streamlit.app"],
            "stars": [random.randint(-1000, 1000) for _ in range(3)],
            "views_history": [[random.randint(0, 5000) for _ in range(30)] for _ in range(3)],
        }
    )
    props = 'font-family: "Times New Roman", Times, serif; color: #e83e8c; font-size:1.3em;'
    st.table(
        dftable.style.set_table_styles([{'selector': 'td.col1', 'props': props}]),
        #column_config={
        #    "name": "App name",
        #    "stars": st.column_config.NumberColumn(
        #        "Github Stars",
        #        help="Number of stars on GitHub",
        #        format="%d ⭐",
        #    ),
        #    "url": st.column_config.LinkColumn("App URL"),
        #    "views_history": st.column_config.LineChartColumn(
        #        "Views (past 30 days)", y_min=0, y_max=5000
        #    ),
        #},
        #hide_index=True,
    )




