import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import csv

fnc_co_factor_dict = {}

def co_factor(var, fn):
    fn_split = fn.split("+")
    fn_list = []
    for i in fn_split:
        fn_list.append(list(i))
    if var.isupper():                                        
        var_com = var.lower()
    else:
        var_com = var.upper()
    flag = 0
    f = ""
    no_of_cubes = len(fn_list)
    for cube in range(0, no_of_cubes):
        if fn_list[cube-flag] == [var]:
            fn_list = ["1"]
            break
        elif var in fn_list[cube-flag]:
            fn_list[cube-flag].remove(var)
        elif var_com in fn_list[cube-flag]:
            fn_list.remove(fn_list[cube-flag])
            flag = flag + 1
        elif fn_list[cube-flag] == []:
            fn_list.remove(fn_list[cube-flag])
            flag = flag + 1
    if fn_list == []:
        fn_list = [["0"]]
        
    fn_list_upd = []
    no_of_cubes = len(fn_list)
    flag = 0
    for cube in range(0, no_of_cubes):
        if fn_list[cube-flag] not in fn_list_upd:
            fn_list_upd.append(fn_list[cube-flag])
        else:
            continue
        if (fn_list[cube] == 2):
            if fn_list[cube][0] == fn_list[cube][1].upper() or fn_list[cube][0].lower() == fn_list[cube][1]:
                fn_list[cube] = '1'

    temp_list = sorted(fn_list_upd,key=len)
    for k in range(len(temp_list)):
        for l in range(len(temp_list)-1,k,-1): 
            if set(temp_list[k]).issubset(temp_list[l]):
                temp_list.pop(l)

    fn_list_upd = temp_list

    upd_no_of_cubes = len(fn_list_upd)
    for cube in range(0, upd_no_of_cubes):
        for var in range(0, len(fn_list_upd[cube])):
            f = f + fn_list_upd[cube][var]
        if cube != upd_no_of_cubes - 1:
            f = f + "+"

    return f

def co_factor_dict(var, fnc):
    pos_co_factor = co_factor(var, fnc)
    neg_co_factor = co_factor(var.upper(), fnc)
    fnc_co_factor_dict[fnc] = [var, neg_co_factor, pos_co_factor]
    
    # return(fnc_co_factor_dict)

def robdd_write(order, fnc):
    order = order.split("<")
    co_factor_dict(order[0], fnc)
    for i in range(1,len(order)):
        var = order[i]
        for key in list(fnc_co_factor_dict.keys()):
            if fnc_co_factor_dict[key][0] == order[i-1]:
                fnc_neg = fnc_co_factor_dict[key][1]
                fnc_pos  =fnc_co_factor_dict[key][2]
                co_factor_dict(var, fnc_neg)
                co_factor_dict(var, fnc_pos)
    
    robdd_dict = {}
    for key in fnc_co_factor_dict:
        if fnc_co_factor_dict[key][1] != fnc_co_factor_dict[key][2]:
            robdd_dict[key] = fnc_co_factor_dict[key]
        else:
            for key1 in fnc_co_factor_dict:
                if fnc_co_factor_dict[key1][1] == key:
                    fnc_co_factor_dict[key1][1] = fnc_co_factor_dict[key][1]
                elif fnc_co_factor_dict[key1][2] == key:
                    fnc_co_factor_dict[key1][2] = fnc_co_factor_dict[key][1]
    print(robdd_dict)

    temp_dict = {}
    for var in order:   
        for key in robdd_dict:
            if var == robdd_dict[key][0]:
                temp_dict[key] = robdd_dict[key]

    robdd_dict = temp_dict

    return robdd_dict

def node_list_mod(node_list):
    node_list_mod = []
    count_dict = {}
    for item in node_list:
        if item in count_dict:
            count_dict[item] += 1
            node_list_mod.append(f"{item}{count_dict[item]}")
        else:
            count_dict[item] = 1
            node_list_mod.append(item)
            
    return node_list_mod
    

def robdd_plotter(robdd_data_frame, order):
    robdd = nx.DiGraph()

    main_node_list = []
    neg_node_list = []
    pos_node_list = []
    node_list = []
    rows = len(robdd_data_frame)
    for item in range(0, rows):
        main_node_list.append(robdd_data_frame.at[item, 'Pointer'] + " , " + robdd_data_frame.at[item, 'Main node'])
        neg_node_list.append(robdd_data_frame.at[item, '0 Pointer'] + " , " + robdd_data_frame.at[item, '0 Node'])
        pos_node_list.append(robdd_data_frame.at[item, '1 Pointer'] + " , " + robdd_data_frame.at[item, '1 Node'])
    
    for item in range(0, rows):
        if main_node_list[item] not in node_list:
            node_list.append(main_node_list[item])
        elif neg_node_list[item] not in node_list:
            node_list.append(neg_node_list[item])
        elif neg_node_list[item] not in node_list:
            node_list.append(neg_node_list[item])
    node_list.append('0 , 0')
    node_list.append('1 , 1')

    for item in range(0, len(node_list)):
        if node_list[item] == '0 , 0' or node_list[item] == '1 , 1':
            robdd.add_node(node_list[item], level = 0)
        else:
            var = node_list[item][len(node_list[item]) - 1]
            index = order.index(var)
            robdd.add_node(node_list[item], level = (len(order) - index))
    
    for item in range(0, rows):
        robdd.add_edges_from([(main_node_list[item], neg_node_list[item])], weight = 0)
        robdd.add_edges_from([(main_node_list[item], pos_node_list[item])], weight = 1)
        
    edge_labels = dict([((u,v,),d['weight'])
                for u,v,d in robdd.edges(data=True)])
    
    pos = nx.multipartite_layout(robdd, subset_key = "level", align = "horizontal")

    nx.draw_networkx_nodes(robdd, pos, node_size = 1000, alpha = 0.2, edgecolors = 'b')
    nx.draw_networkx_labels(robdd, pos)
    nx.draw_networkx_edges(robdd, pos, edge_color = 'black', arrowsize = 15, node_size = 1000, arrows = True, connectionstyle = "arc3, rad = 0.115")
    nx.draw_networkx_edge_labels(robdd, pos, edge_labels = edge_labels, font_size = 12)
    plt.show()

def robdd_data_frame(robdd_dict):
    robdd_data_frame_dict = {'Pointer': [], 'Main node': [], '0 Pointer': [], '0 Node': [], '1 Pointer': [], '1 Node': []}
    data_keys = list(robdd_dict.keys())
    for key in data_keys:
        robdd_data_frame_dict['Pointer'].append(key)
        robdd_data_frame_dict['Main node'].append(robdd_dict[key][0])
        robdd_data_frame_dict['0 Pointer'].append(robdd_dict[key][1])
        neg_co_factor = robdd_dict[key][1]
        if neg_co_factor == '1': 
            robdd_data_frame_dict['0 Node'].append('1')
        elif neg_co_factor == '0': 
            robdd_data_frame_dict['0 Node'].append('0')
        else: 
            robdd_data_frame_dict['0 Node'].append(robdd_dict[neg_co_factor][0])
        robdd_data_frame_dict['1 Pointer'].append(robdd_dict[key][2])
        pos_co_factor = robdd_dict[key][2]
        # print(pos_co_factor)
        if pos_co_factor == '1': robdd_data_frame_dict['1 Node'].append('1')
        elif pos_co_factor == '0': robdd_data_frame_dict['1 Node'].append('0')
        else: robdd_data_frame_dict['1 Node'].append(robdd_dict[pos_co_factor][0])
    
    robdd_data_frame = pd.DataFrame(robdd_data_frame_dict)

    return robdd_data_frame

def robdd_csv(robdd_data_frame):
    with open("robdd.csv", 'w+', newline='') as file:
        writer = csv.writer(file)
        heading = ['Pointer', 'Main node', '0 Pointer', '0 Node', '1 Pointer', '1 Node']
        writer.writerow(heading)
        for row in range(len(robdd_data_frame)):
            temp_list = robdd_data_frame.iloc[row].tolist()
            writer.writerow(temp_list)

print("For uncomplemented literal, represent using lower case and for complemented literal, represent using upper case.")
fnc = input("Enter fnc: ")
order = input("Enter order. Eg: a<b<c<d: ")
robdd_dict = robdd_write(order, fnc)
print(robdd_dict)
robdd = robdd_data_frame(robdd_dict)
print(robdd)
robdd_csv(robdd)
robdd_plotter(robdd, order)