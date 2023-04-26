import pandas as pd
from scipy.optimize import minimize
from numdifftools import Jacobian, Hessian
from time import process_time

def objective_fcn(eff, games, map, num_teams):
    total_error = 0
    for index, row in games.iterrows():
        total_error += (row["Home Rtg"]*2 - eff[map[row["Home"]]] - eff[num_teams+map[row["Away"]]])**2
        total_error += (row["Away Rtg"]*2 - eff[map[row["Away"]]] - eff[num_teams+map[row["Home"]]])**2
    return (total_error)

def gradient_calc(efficiency_scores, help, map, rev_map, num_teams):
    gradient = []
    for i in range(2*num_teams):
        if (i < num_teams):
            sum_def_scores = 0
            games_played = len(help[rev_map[i]]["Opponents"])
            if (games_played == 0):
                gradient.append(0)
                continue
            for opp in help[rev_map[i]]["Opponents"]:
                sum_def_scores += efficiency_scores[num_teams + map[opp]]
            gradient.append(2*(games_played*efficiency_scores[i]+sum_def_scores) - 4*help[rev_map[i]]["Off Sum"])
        else:
            sum_off_scores = 0
            games_played = len(help[rev_map[i-num_teams]]["Opponents"])
            if (games_played == 0):
                gradient.append(0)
                continue
            for opp in help[rev_map[i-num_teams]]["Opponents"]:
                sum_off_scores += efficiency_scores[map[opp]]
            gradient.append(2*(games_played*efficiency_scores[i]+sum_off_scores) - 4*help[rev_map[i-num_teams]]["Def Sum"])
    return (gradient)
    
def gradient_descent_iter(efficiency_scores, gradient):
    for i in range(len(efficiency_scores)):
        efficiency_scores[i] -= gradient[i]*0.005
    return (efficiency_scores)

def gradient_descent(efficiency_scores, help, map, rev_map, num_teams, print_ = False):
    gradient = gradient_calc(efficiency_scores, help, map, rev_map, num_teams)
    while (max([abs(min(gradient)),abs(max(gradient))]) > 0.2):   
        efficiency_scores = gradient_descent_iter(efficiency_scores, gradient)
        gradient = gradient_calc(efficiency_scores, help, map, rev_map, num_teams)
        if (print_):
            print (efficiency_scores)
            print (gradient)
    return (efficiency_scores)

def basic_efficiency():
    df = pd.read_csv("./efficiency_stats.csv", encoding = "ISO-8859-1")
    teams = df["Home"].unique().tolist()
    for x in df["Away"].unique():
        if (x not in teams):
            teams.append(x)
    num_teams = len(teams)
    team_map = {}
    rev_team_map = {}
    gradient_helper = {}
    efficiency_scores = []
    gradient = []
    for i in range(len(teams)):
        team_map[teams[i]] = i
        rev_team_map[i] = teams[i]
        gradient_helper[teams[i]] = {"Opponents":[],"Off Sum":0,"Def Sum":0}
        efficiency_scores.append(90)
        efficiency_scores.append(90)
        gradient.append(0)
        gradient.append(0)
    for index, row in df.iterrows():
        gradient_helper[row["Home"]]["Opponents"].append(row["Away"])
        gradient_helper[row["Home"]]["Off Sum"] += row["Home Rtg"]
        gradient_helper[row["Home"]]["Def Sum"] += row["Away Rtg"]
        gradient_helper[row["Away"]]["Opponents"].append(row["Home"])
        gradient_helper[row["Away"]]["Off Sum"] += row["Away Rtg"]
        gradient_helper[row["Away"]]["Def Sum"] += row["Home Rtg"]
        if (index % 10 == 1):
            print (index)
            if (index == 801):
                print (efficiency_scores)
                print (gradient_calc(efficiency_scores,gradient_helper,team_map,rev_team_map,num_teams))
            t1 = process_time()
            efficiency_scores = gradient_descent(efficiency_scores,gradient_helper,team_map,rev_team_map,num_teams)
            t2 = process_time()
            print (t2-t1)
    print (efficiency_scores)
    


basic_efficiency()