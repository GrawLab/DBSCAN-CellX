
import pandas as pd
from scipy.spatial import distance_matrix
import numpy as np
import operator
from sklearn import cluster
from sklearn.cluster import DBSCAN
import argparse
import csv
import warnings
import time

warnings.filterwarnings("ignore")

X_var = "X"
Y_var = "Y"

def get_cluster_labels(table, pixel_list):
    cell_nr = len(table)
    # get covered area
    size_X = pixel_list[0]
    size_Y = pixel_list[1]
    pixel = pixel_list[2]
    # first, count cells per 20x20 µm square
    x_steps = np.arange(0, size_X*pixel, 20*pixel)
    y_steps = np.arange(0, size_Y*pixel, 20*pixel)
    hist, xedges, yedges = np.histogram2d(table[X_var], table[Y_var], bins=(
        x_steps, y_steps), range=[[0, size_X], [0, size_Y]])
    # set threshold: Count all squares with at least one cell
    over_threshold = np.transpose(hist) > 0
    covered_squares = sum(over_threshold.flatten())
    # determine epsilon
    global epsilon
    #formula was fitted to pixel --> to convert, term is divided by pixel
    epsilon = (22301.17*np.exp((cell_nr/covered_squares)
               * -6.35) + 93.42) * (pixel/2.8986)

    min_samples = round(-8.87*np.exp((cell_nr/covered_squares)*-1.13) + 8.11)
    char_lables = np.empty(cell_nr, dtype=np.dtype('U100'))
    position_array = np.column_stack((table[X_var], table[Y_var]))
    clustering = DBSCAN(
        eps=epsilon, min_samples=min_samples).fit(position_array)
    char_lables[:] = 'edge'
    char_lables[clustering.labels_ == -1] = 'noise'
    char_lables[clustering.core_sample_indices_] = 'center'
    table['cluster_position'] = char_lables
    table['Cluster_ID'] = clustering.labels_
    table["Cells_in_Image"] = cell_nr
    return(min_samples, epsilon)

# The following three functions are used in the correct_cluster_label function.

# First, create unit vectors of difference of center point to each of its neigbors


def create_vectors(p1, points):
    vectors = np.zeros((len(points), 2))
    for count, point in enumerate(points):
        v1 = [point[0] - p1[0], point[1] - p1[1]]
        unit_v1 = v1 / np.linalg.norm(v1)
        vectors[count] = unit_v1
    return(vectors)
# Second, calculate angles of vectors to one reference vector


def calc_angles(vectors):
    reference_vector = [1, 0]
    angles = []
    counter = 0
    for i in vectors:
        angle = np.arctan2(i[1], i[0])
        angle = round(angle * 180 / np.pi)
        if angle < 0:
            angle = 360 + angle
        angles.append(angle)
    return(angles)
# Third, calcualte angles between two neighboring vectors.
# If one angle is bigger than 180°, all neighboring cells are on one side of center cell


def dif_angles(angles,angel_paramter):
    angles = np.sort(angles)
    one_step = np.append([angles[1:]], [angles[0]+360])
    differences = angles - one_step
    one_side = np.any(differences <= -angel_paramter)
    return(one_side)

# This function gets every center point with their neighboring cells that are within epsilon neighborhood
# Then, functions above are used to check if neighbors are all on one side
# If yes, 'corrected_cluster' contains new cluster label


def correct_cluster_label(table, angel_paramter):
    center_cells = table.index[table['cluster_position'] == 'center'].tolist()
    #center_cells = np.asarray(center_cells) - first_index
    position = table[[X_var, Y_var]].to_numpy()
    distance = distance_matrix(position, position)
    actual_edge = []
    rows, cols = np.where(distance[center_cells] < epsilon)
    for counter, j in enumerate(center_cells):
        p = [table[X_var][j], table[Y_var][j]]
        neighbor_index = cols[np.where(rows == counter)]
        neighbors = len(neighbor_index) - 1
        if neighbors > 1:
            neighbor_list = np.zeros((neighbors, 2))
            counter = 0
            for index in neighbor_index:
                if index != j:
                    neighbor_list[counter] = [
                        table[X_var][index], table[Y_var][index]]
                    counter += 1
            vectors = create_vectors(p, neighbor_list)
            angles = calc_angles(vectors)
            result = dif_angles(angles, angel_paramter)
        else:
            #result == True
            print('somethings worng')
        if result == True:
            actual_edge.append(j)
    # new column is set on df with corrected cluster positions
    table['corrected_cluster'] = table['cluster_position']
    table.loc[actual_edge, 'corrected_cluster'] = 'edge'
    return(table)

"""
def count_neighborhood_cluster(table, radius_list, filter_column, option_list, distance, pixel_list):
    pixel = pixel_list[2]
    for radius in radius_list:
        for option in option_list:
            cells = table[filter_column] == option
            rows, cols = np.where(
                (distance[:, cells] < radius) & (distance[:, cells] != 0))
            column = np.bincount(rows)
            if len(column) != len(table):
                column = np.append(column, np.zeros(
                    len(table) - len(column))).astype(int)
            new_colname = str(round(radius/pixel)) + 'µm_neighbors_' + option
            table[new_colname] = column
        total_colname = str(round(radius/pixel)) + 'µm_neighbors_total'
        table[total_colname] = (table[str(round(radius/pixel)) + 'µm_neighbors_' + option_list[0]] +
                                table[str(round(radius/pixel)) + 'µm_neighbors_' + option_list[1]] + table[str(round(radius/pixel)) + 'µm_neighbors_' + option_list[2]])
"""
"""
def dist_to_edge(table, distance):
    clusters = np.sort(table['cluster'].unique())
    cluster_dict = dict()
    distances_edge = np.zeros((len(table), 3))
    edge_indices = table.index[table['cluster_position'] == 'edge']
    for i in clusters:
        #Get indices of each edge cluster cells

        cluster_dict[i] = table.index[(table['cluster'] == i) & (
            table['cluster_position'] == 'edge')].tolist()
    for index, row in table.iterrows():
        cluster_position = row['cluster_position']
        if cluster_position != 'edge':
            cluster = row['cluster']
            if cluster != -1:
                dist_to_own_edges = distance[index, cluster_dict[cluster]]
                try:
                    distances_edge[index] = [dist_to_own_edges.min(
                    ), dist_to_own_edges.max(), dist_to_own_edges.mean()]
                except ValueError:
                    pass
            elif cluster == -1:
                dist_to_edges = distance[index, edge_indices]
                try:
                    distances_edge[index] = [
                        dist_to_edges.min(), dist_to_edges.max(), dist_to_edges.mean()]
                except ValueError:
                    pass
    table['min_dist_to_edge'] = distances_edge[:, 0]
    table['max_dist_to_edge'] = distances_edge[:, 1]
    table['mean_dist_to_edge'] = distances_edge[:, 2]
"""

def edge(table, pixel_list, angel_paramter):
    df = table
    edge_degrees = pd.DataFrame()
    k = 1

    edge_list = []
    for i in df["Nucleus number_x"]:
        ind = np.array(df["Nucleus number_x"] == i)
        x = np.where(ind == True)
        if df["corrected_cluster"][np.min(x)] == "edge":
            edge_list.append(i)
    noise_list = []
    for i in df["Nucleus number_x"]:
        ind_2 = np.array(df["Nucleus number_x"] == i)
        x2 = np.where(ind_2 == True)
        if df["corrected_cluster"][np.min(x2)] == "noise":
            noise_list.append(i)

    leftover_noise = pd.DataFrame({"Ind": df.loc[df['Nucleus number_x'].isin(noise_list)]["Nucleus number_x"],
                                   "Edge_Degree": np.repeat(0, len(df.loc[df['Nucleus number_x'].isin(noise_list)]))})
    
    new_df = df.loc[df['Nucleus number_x'].isin(
        edge_list), ["corrected_cluster"]]
    new_df["Ind"] = edge_list
    new_df["Edge_Degree"] = k
    new_df = new_df.drop(columns=["corrected_cluster"])
    edge_degrees = pd.concat([edge_degrees, new_df])
   
    k = k+1

    df = df.loc[~df['Nucleus number_x'].isin(edge_list)]
    df = df.loc[~df['Nucleus number_x'].isin(noise_list)]

    n = df.groupby("Cluster_ID").count()["X"]
    try:
        n = max(n)
    except:
        n = 0
    df = df[df.columns[0:9]]

    leftover = pd.DataFrame()
    while(n > 5):


        position = df[[X_var, Y_var]].to_numpy()

        distance = distance_matrix(position, position)
        get_cluster_labels(df, pixel_list)

        clustersizes = df.groupby('Cluster_ID').count()['Nucleus number_x']

        df = df.merge(clustersizes, on='Cluster_ID')
        df = df.rename(columns={"Label_y": "Hallo"})
        df = df.rename(columns={"Nucleus number_x_x": "Nucleus number_x"})
       
        #dist_to_edge(df, distance)

        df = correct_cluster_label(df, angel_paramter)

        df.loc[df['corrected_cluster'] == "noise",
               ["corrected_cluster"]] = 'edge'

        edge_list = []
        for i in df["Nucleus number_x"]:
            ind = np.array(df["Nucleus number_x"] == i)
            x = np.where(ind == True)
            if df["corrected_cluster"][np.min(x)] == "edge":
                edge_list.append(i)
        
        new_df = df.loc[df['Nucleus number_x'].isin(
            edge_list), ["corrected_cluster"]]
        new_df["Ind"] = edge_list

        new_df["Edge_Degree"] = k
        new_df = new_df.drop(columns=["corrected_cluster"])
        edge_degrees = pd.concat([edge_degrees, new_df])


        df =  df.loc[~df['Nucleus number_x'].isin(edge_list)]
        n = df.groupby("Cluster_ID").count()["X"]
        df = df[df.columns[0:9]]

        try:
            n = max(n)
        except:
            n = 0
   
        k = k+1

        edge.cnt = k
    leftover = pd.DataFrame({"Ind": df["Nucleus number_x"],
                            "Edge_Degree": np.repeat(k, len(df["Nucleus number_x"]))})
    edge_degrees = pd.concat([edge_degrees, leftover, leftover_noise])
    table = pd.merge(table, edge_degrees,
                     left_on='Nucleus number_x', right_on='Ind', how='left')
    return(table)


def edit_table(files, save, pixel_list, edge_mode, angel_parameter, save_parameter, keep_uncorr):
    for j in files:
  
        with open(j, newline='') as csvfile:
            sniffer = csv.Sniffer().sniff(csvfile.readline())
            delimiter = sniffer.delimiter
        table_all = pd.read_csv(j, sep=delimiter)
       
        table_all.columns.values[1] = "Nucleus number"
        table_all.columns.values[0] = "ImageNumber"
        cols = list(table_all.columns)
        cols = [col.upper() for col in cols]
        table_all.columns.values[cols.index("X")] = "X"
        table_all.columns.values[cols.index("Y")] = "Y"


        df_list = []
        para_df = pd.DataFrame()

        for i in table_all["ImageNumber"].unique():
            table = table_all[table_all["ImageNumber"] == i]

            position = table[[X_var, Y_var]].to_numpy()
            distance = distance_matrix(position, position)
            paramter_output = get_cluster_labels(table, pixel_list)
          
            parameters = (i,) + paramter_output
          
            para_df = para_df.append(pd.DataFrame([parameters], columns=["ImageNumber","Nmin", "Epsilon"]))

            


            clustersizes = table.groupby('Cluster_ID').count()['Nucleus number']

            table = table.merge(clustersizes, on='Cluster_ID')
            table = table.rename(columns={"Label_y": "Hallo"})

            table = correct_cluster_label(table, angel_parameter)

            if edge_mode == 1:
                table = edge(table, pixel_list, angel_parameter)
                table = table.drop('Ind', axis=1)
            #name = j[:j.find(str("test_data_"))+11]
            delimiter_path = save[-1]
            name_stem = j.split(delimiter_path)[-1]
            name_stem = name_stem[:-4]

            savepath =  save + name_stem + '_DBSCAN_CELLX_output.csv'
            if save_parameter == 1:
                savepath_para = save + name_stem + "_paramter_list.csv"
                para_df.to_csv(savepath_para, sep=';', index=False)
            df_list.append(table)
            
        
        df_list = pd.concat(df_list, ignore_index=True)
        df_list = df_list.rename(
            columns={"Nucleus number_x": "Cell_ID", "Nucleus number_y": "Cells_in_Cluster", "corrected_cluster" : "Cluster_Position", "cluster_position": "Uncorrected_Cluster_Position" })
        if keep_uncorr != 1:
            df_list.drop(df_list.columns.difference(
                ['ImageNumber', 'Cell_ID', "X", "Y", "Cluster_ID", "Cells_in_Image", "Cells_in_Cluster", "Cluster_Position", "Edge_Degree"]), 1, inplace=True)
        else:
            df_list.drop(df_list.columns.difference(
                ['ImageNumber', 'Cell_ID', "X", "Y", "Cluster_ID", "Cells_in_Image", "Cells_in_Cluster", "Cluster_Position", "Edge_Degree", "Uncorrected_Cluster_Position"]), 1, inplace=True)
        df_list.to_csv(savepath, sep=';', index=False)
        


def main(files, save, pixel_ratio, size_x, size_y, edge_mode = 1, angel_parameter = 140, save_parameter = 1, keep_uncorr = 1):
    st = time.time()
    print('Data will be analyzed: \n')
    print(files)

    pixel = pixel_ratio
    pixel = 1/pixel
    X = size_x
    Y = size_y
    pixel_list = [X, Y, pixel]
    edit_table(files,save,
               pixel_list, edge_mode, angel_parameter, save_parameter, keep_uncorr)
    et = time.time()
    elapsed = et-st
    print("Thats it! Thanks for using DBSCAN-CellX!")
    print("It took you : --- %s seconds ---" % (elapsed))

    
