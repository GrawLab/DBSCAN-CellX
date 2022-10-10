from os.path import isfile, join
import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px
import numpy as np
import csv
import subprocess
from pathlib import Path
import os
from persist import persist, load_widget_state
from skimage import io
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from dbscan_cellx import dbscan_cellx
from PIL import Image
from os import listdir
matplotlib.use('Agg')
#dirname = None
#file_name = None
st.set_page_config(layout="wide")

#Overall Structure Call

def pager (pages,page):
    pages[page]()

def main():
    # Register your pages
    pages = {
        "Homepage": home,
        "Test DBSCAN-CellX": page_data,
        #"Settings": page_settings,
        #"Test Area": page_test,
        "Run DBSCAN-CellX": page_run,
        "Visualization": second_page,
    }
    st.session_state.pages = pages
    st.sidebar.image('./Images/Logo.jpg', width=200)
    st.sidebar.title("DBSCAN-CellX App")

    # Widget to select your page, you can choose between radio buttons or a selectbox
    page = st.sidebar.selectbox("Select your page", tuple(pages.keys()), key = "main")

    # Display the selected page with the session state
    pager(pages,page)
    #pages[page]()
#Home Page


def home():

    st.title("DBSCAN-CellX - Homepage")
    imagelogo = Image.open('./Images/Logo.jpg')
    st.image(imagelogo,  width=300)

    st.markdown("DBSCAN-CellX is a clustering and positional classification tool especially designed for cell culture experiments(Quelle). This tool relies on the original DBSCAN algorithm from Sander, J., et. al (1996) to determine individual clusters. Additionally, it performs a robust classification of cells as noise, edge and center cells, depending on their relative location within the clusters.")
    st.subheader("Data Requirements")
    st.markdown("To run DBSCAN-CellX on your data, the input file has to consist of a table with at least 4 columns depicting, (1) a unique Image_ID (*ImageNumber*), (2) a unique *Cell ID*, as well as (3) the *X*- and *Y*-position of the cell. Both *ImageNumber* and *CellID* are integers. The data structure is analogous to the output provided by CellProfiler (Stirling DR; 2021) or other image analysis tools.")

    image = Image.open('./Images/Data_structure.PNG')
    st.image(image, caption='Required Data Structure')

    st.subheader("Using this App")
    st.markdown("The App provides a user-friendly GUI to simplify the usage of the Python package DBSCAN-CellX."
                "The App consists of several pages. On the *Input Data* page, the user can upload single files, which will be used for preliminary testing."
                " The *Settings* page allows the user to input (mandatory) about the data files, as well as change parameters of the DBSCAN-CellX package."
                " On the *Test Area* page, the user can now run a preliminary test run of DBSCAN-CellX and compare different results."
                " *Run DBSCAN-CellX* and *Visualization* allow a complete run of DBSCAN-CellX and the following data visualization."
                " Further information and details can be found at https://github.com/PasLukas/DBSCAN-CellX")

    st.subheader("Data Output")
    st.markdown("DBSCAN-CellX returns a .csv file with the same name as the input file and the file name extension DBSCAN_CellX_output. The main output results in four addtional columns and if the user specified the Edge Detection a fith column is generated. "
                "Please find further information on the Github-Page (https://github.com/PasLukas/DBSCAN-CellX)")
    image2 = Image.open('./Images/Data_output.PNG')
    st.image(image2, caption='Output Data Structure')



def run_DBSCAN(data, save, pixel_ratio,cell_size, X, Y, edge_mode, angle_paramter, save_para, keep_uncorr):
    dbscan_cellx.main([data], save, pixel_ratio,cell_size, X,
                      Y, edge_mode, angle_paramter, save_para, keep_uncorr)

def picker_data():
        if "text" not in st.session_state:
            st.session_state.text = "Input data directory"
        data_path = st.text_input(
            'Path to data input directory. *', st.session_state.text)
        st.session_state.text = data_path
        return st.session_state.text

def picker_save():
        if "text2" not in st.session_state:
            st.session_state.text2 = "Output data directory"
        save_path = st.text_input(
            'Path to data output directory. *', st.session_state.text2)
        st.session_state.text2 = save_path
        return st.session_state.text2

def page_data():
    st.title('Test DBSCAN-CellX')
    st.markdown("This is the testing area of the DBSCAN-CellX App. This page allows the user to input their data, run a test run and change selected parameters.")

#Adress Data Directory

#Adress Save Directory


#Call the Adress Directory Functions
    col1, col2 = st.columns([3, 3])
    with col1:
        st.subheader('Folder Picker')
        picker_data()
        picker_save()
        st.markdown('*Hint: Directory paths must end with "/" in Unix-based systems or "\ " in Windows systems.')
    with col2:

        st.subheader("Data input")
        st.markdown("Please input a preliminary test file."
                    "Files can be added via Drag and Drop or browsing through the system.")
        if "uploaded_file" not in st.session_state:
            st.session_state.uploaded_file = "empty"

        uploaded_file = st.file_uploader(
            "Choose a file")

        st.session_state.uploaded_file = uploaded_file

        if "df" not in st.session_state:
            st.session_state.df = None
        if "file" not in st.session_state:
            st.session_state.file = "empty"
        if st.session_state.uploaded_file is not None:
            st.session_state.file_name = st.session_state.uploaded_file.name
            file_name = st.session_state.uploaded_file.name
            st.session_state.file = file_name
            with open(st.session_state.text + st.session_state.file, newline='') as csvfile:
                sniffer = csv.Sniffer().sniff(csvfile.readline())
                delimiter = sniffer.delimiter
            st.session_state.df = pd.read_csv(
                st.session_state.uploaded_file, sep = str(delimiter))
            st.session_state.file_name = st.session_state.uploaded_file.name
            file_name = st.session_state.uploaded_file.name
            st.session_state.file = file_name
        

            #file_name = st.session_state.uploaded_file.name
        
            st.session_state.file = file_name
        st.write("Last Uplodaded File:",st.session_state.file)
        if "file" not in st.session_state:
            st.session_state.file = "empty"
        if "last_file" not in st.session_state:
            st.session_state.last_file = "empty"

        #if st.session_state.uploaded_file is not None:
        #    last_file = uploaded_file.name

    st.header("Input Data")
    st.markdown("This panel can be used for easy data visualization. The chosen image file will be used of the preliminary test run.")
    if st.session_state.df is not None:

        
        df = st.session_state.df
        df.columns.values[1] = "Nucleus number"
        df.columns.values[0] = "ImageNumber"
        cols = list(df.columns)
        cols = [col.upper() for col in cols]
        df.columns.values[cols.index("X")] = "X"
        df.columns.values[cols.index("Y")] = "Y"
        tab1, tab2 = st.tabs(["Visualize Data", "Table"])
        with tab1:
            col1, col2, col3 = st.columns([1, 2, 1])

            with col2:
                if "input_data_options" not in st.session_state:
                    st.session_state.input_data_options = 1
                st.session_state.input_data_options = st.selectbox(
                    'Image ID',
                    (list(set(df.iloc[:, 0]))), key="Input_data_options", index=st.session_state.input_data_options-1)
                df_sub_IM = df[df["ImageNumber"] ==
                               st.session_state.input_data_options]
                fig0 = px.scatter(x=df_sub_IM["X"],
                                  y=df_sub_IM["Y"])
                st.plotly_chart(fig0, use_container_width=True, width=100)

        with tab2:
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.header("Input Data Table")
                st.dataframe(df)



        st.subheader("Changing Parameters")
    st.markdown("Please specify the analytical settings. The pixel edge size in microns(micron to pixel ratio), as well as the dimensions of the image in X - and Y-direction must be specified by the user. Please specify if measurements were provided in pixels or microns. The default threshold angle for performing edge-correction analysis is set to 140°. Please select if additional parameters should be set in the * Advanced Settings*.")
    st.markdown("**Note:** Always submit changes in the Settings with enter")

    sett_tab1, sett_tab2 = st.tabs(["Settings", "Advanced Settings"])
    with sett_tab1:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            #pixel_input()
            if "pixel_rat" not in st.session_state:
                st.session_state.pixel_rat = 0.01
            if "cell_size" not in st.session_state:
                st.session_state.cell_size = 0.01    
            if "X" not in st.session_state:
                 st.session_state.X = 0.01
            if "Y" not in st.session_state:
                 st.session_state.Y = 0.01
            pixel_rat = st.number_input(
                'Please enter pixel edge size in microns (micron to pixel ratio)', value=st.session_state.pixel_rat)
            cell_size = st.number_input(
                'Please enter the estimated cell size in microns', value=st.session_state.cell_size)
            size_X = st.number_input(
                 'Please enter total pixels or microns in X direction', value=st.session_state.X)
            size_Y = st.number_input(
                'Please enter total pixels or microns in Y direction', value=st.session_state.Y)
            #clicked2 = st.button('Submit')
            #if clicked2:
            st.session_state.pixel_rat = pixel_rat
            st.session_state.X = size_X
            st.session_state.Y = size_Y
            st.session_state.cell_size  = cell_size
            #st.write("Data:", st.session_state.X)
            #pixel_rat = st.session_state.pixel_rat
            #size_X = st.session_state.X
            #size_Y = st.session_state.Y

        with col2:
            pixel_kind = st.radio(
                "Please enter if image resolution was measured in microns or pixels",
                ('Microns', 'Pixel'))

            if pixel_kind == "Pixel":
                size_X = size_X*pixel_rat
                size_Y = size_Y*pixel_rat

        with sett_tab2:
            col1, col2 = st.columns([1, 2])
            with col1:
                #parameter_input()
                if "angel" not in st.session_state:
                 st.session_state.angel = 140

                angel = st.number_input(
                    'Please enter the correction angle in degrees', value=st.session_state.angel)
                st.session_state.angel = angel
                #st.session_state.angel = angle 

                if "edge_mode" not in st.session_state:
                    st.session_state.edge_mode = 0
                if "save_para" not in st.session_state:
                    st.session_state.save_para = 0
                if "agree_log_save" not in st.session_state:
                    st.session_state.agree_log_save = 0
                if "keep_uncorr" not in st.session_state:
                    st.session_state.keep_uncorr = 0

                agree_edge = st.checkbox(
                    'Allow edge degree detection?', st.session_state.edge_mode)
                if agree_edge:
                    st.session_state.edge_mode = 1
                else:
                    st.session_state.edge_mode = 0

                agree_edge = st.session_state.edge_mode
                st.session_state.edge_mode = agree_edge
                agree_para_save = st.checkbox(
                    'Save a seperate parameter list?', st.session_state.save_para)
                if agree_para_save:
                    st.session_state.save_para = 1
                else:
                    st.session_state.save_para = 0

                agree_log_save = st.checkbox(
                    'Keep log-files of parameters?', st.session_state.agree_log_save)
                if agree_log_save:
                    st.session_state.agree_log_save = 1
                else:
                    st.session_state.agree_log_save = 0
                agree_log_save = st.session_state.agree_log_save

                agree_kepp_uncorr = st.checkbox(
                    'Show uncorrected cluster positions?', st.session_state.keep_uncorr)
                if agree_kepp_uncorr:
                    st.session_state.keep_uncorr = 1
                else:
                    st.session_state.keep_uncorr = 0
                agree_kepp_uncorr = st.session_state.keep_uncorr

            with col2:
                st.write("**Explanation**")
                st.write(
                    "*Correction angle:* Changes the exclusion angle for the edge correction. The smaller the angle, the more cells will be labeled as edge cells.")
                st.write(
                    "*Edge degree detection:* Provides a discrete value of a cell's distance to edge.")
                st.write(
                    "*Parameter list:* Allow seperate output of calculated Epsilon and n_min (input parameters for DBSCAN).")
                st.write(
                    "*Log files:* Allow seperate output of input parameters.")
                st.write(
                    "*Uncorrected cluster positions:* Allow output of uncorrected cluster postions in DBSCAN-CellX output file in addition to corrected cluster positions.")

    st.subheader("Test Run")
    st.write("**Note:** Running a test run creates and saves a seperate *test_data* file and *DBSCAN_CellX_output* based on the input data in the save directory. Depending on the chosen *Advanced Settings* further files may be created.")
    if "test_run_counter" not in st.session_state:
        st.session_state.test_run_counter = 0
    if st.button('Run Test'):
        df = st.session_state.df
        st.session_state.test_run_counter = st.session_state.test_run_counter+1
        df_sub = df[df.iloc[:, 0] == st.session_state.input_data_options]
        save_path = str(st.session_state.text2) + st.session_state.file[:-4] + "_test_data_"+str(
            st.session_state.test_run_counter) + ".csv"
        df_sub.to_csv(save_path, sep=';', index=False)
        st.write('Run DBSCAN-CellX')
        run_DBSCAN(save_path, st.session_state.text2,
                   st.session_state.pixel_rat,st.session_state.cell_size, st.session_state.X, st.session_state.Y, st.session_state.edge_mode, st.session_state.angel, st.session_state.save_para, st.session_state.keep_uncorr)
        if st.session_state.agree_log_save == 1:
            if st.session_state.edge_mode:
                edge_mode = "Enabled"
            else:
                edge_mode = "Disabled"
            if st.session_state.keep_uncorr:
                keep_uncorr = "Enabled"
            else:
                keep_uncorr = "Disabled"

            log_df = pd.DataFrame({"Pixel Ratio": [str(st.session_state.pixel_rat)], "Cell Size": [str(st.session_state.cell_size)], "X-Dimension": [str(st.session_state.X)],
                                   "Y-Dimension": [str(st.session_state.Y)], "Edge-Degree Detection": [str(edge_mode)], "Correction Angle": [str(st.session_state.angel)], "Uncorrected_Cluster_Positions": [str(keep_uncorr)]})
            output_name_log = save_path[:save_path.find(str("test_data_"))+9] + '_log_files_' + \
                str(st.session_state.test_run_counter) + ".csv"
            log_df.to_csv(output_name_log, sep=';', index=False)

    if st.session_state.test_run_counter != 0:
        st.subheader("Compare Test Results")
        st.write("Choose between different options to compare test results to.")
        st.write("Use the dropdown-menu to choose a specific Test-File. ")
        save_path = str(st.session_state.text2) + st.session_state.file[:-4] + "_test_data_"+str(
            st.session_state.test_run_counter) + ".csv"
        output_name = save_path[:-4] + '_DBSCAN_CELLX_output.csv'

        col1, col2, col3 = st.columns([1, 2, 1])
        mypath = st.session_state.text2
        onlyfiles = [f for f in listdir(
            mypath) if isfile(join(mypath, f))]
        matches = []
        matches_sub = []
        test_data_list = []
        for match in onlyfiles:
            if "test" in match:
                matches.append(match)
                matches_sub.append(match[:match.find("_test")])
        unique_data = set(sorted(matches_sub, key=len))
        for stem in unique_data:
            counter = 0
            counter_stems = []
            stem_data_list = []
            stem_parameter_list = []
            test_file = []
            for file in matches:
                 if (stem+"_test_data_") in file and ("DB") in file:
                     counter = counter + 1
                     counter_stems.append(counter)
                     test_file.append(file)
                     if (stem + "_test_data_log_files_" + file[-25] + ".csv") in matches:
                        stem_parameter_list.append(
                            stem + "_test_data_log_files_" + file[-25] + ".csv")
                     else:
                        stem_parameter_list.append("")

            stem_data_list = [stem, counter_stems,
                               test_file, stem_parameter_list]
            test_data_list.append(stem_data_list)
        test_data_list = pd.DataFrame(test_data_list)
        with col2:
            option_test_stem1 = st.selectbox(
                'Dataset',
                (list(test_data_list[0])), key="1")
            index_bol1 = list(pd.DataFrame(test_data_list)[0].str.contains(
                option_test_stem1))
            option_test_num1 = st.selectbox(
                'Test Run Number',
                (pd.DataFrame(test_data_list)[1][index_bol1].tolist()[0]), key="2", index=max(pd.DataFrame(test_data_list)[1][index_bol1].tolist()[0])-1)
            selec_test_data1 = st.session_state.text2 + \
                pd.DataFrame(test_data_list)[2][index_bol1].tolist()[
                    0][option_test_num1-1]
            selec_log_file1 = pd.DataFrame(test_data_list)[3][index_bol1].tolist()[
                0][option_test_num1-1]
            st.write("File:", selec_test_data1)
            if not selec_log_file1:
                selec_test_data_df1 = pd.read_csv(selec_test_data1, sep=";")
            else:
                selec_log_file1 = st.session_state.text2 + \
                    pd.DataFrame(test_data_list)[3][index_bol1].tolist()[
                        0][option_test_num1-1]
                selec_test_data_df1 = pd.read_csv(
                    selec_test_data1, sep=";")
                selec_log_file_df1 = pd.read_csv(selec_log_file1, sep=";")

        test_tab1, test_tab2, test_tab3, test_tab4, test_tab5 = st.tabs(
            ["Test Results", "Test Data Table", "Compare Cluster Position Classification", "Compare Test Parameters", "Overlay Microscopy"])

        with test_tab1:
            st.subheader("Show DBSCAN-CellX Results")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                IM_num_test = selec_test_data_df1["ImageNumber"][0].astype(str)
                st.write("**ImageNumber:**", IM_num_test)
                if not selec_log_file1:
                    st.write("No Parameter List available")
                else:
                    st.write("**Parameter List:**")
                    logs = selec_log_file_df1.astype(str)
                    st.dataframe(logs.T)
                    keep_setting = st.button("Keep these Settings?")
                    if keep_setting:
                       st.session_state.pixel_rat = selec_log_file_df1.iloc[:,0] [0]
                       st.session_state.pixel_rat = selec_log_file_df1.iloc[:,1] [0]
                       st.session_state.X = selec_log_file_df1.iloc[:,2] [0]
                       st.session_state.Y = selec_log_file_df1.iloc[:,3] [0]
                       st.session_state.edge_mode = selec_log_file_df1.iloc[:,4] [0]
                       st.session_state.angel = selec_log_file_df1.iloc[:,5] [0]
                       st.session_state.keep_uncorr = selec_log_file_df1.iloc[:, 6][0]
                       st.experimental_rerun()

            with col2:
                #df_sub_output = pd.read_csv(output_name, sep=";")
                fig = px.scatter(x=selec_test_data_df1["X"],
                                 y=selec_test_data_df1["Y"],
                                 color=selec_test_data_df1["Cluster_Position"],
                                 color_discrete_map={
                    "noise": "#161616",
                    "edge": "#E77700",
                    "center": "#588E00"})
                st.plotly_chart(fig, use_container_width=True)

        with test_tab2:
            st.subheader("Show DBSCAN-CellX Results")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if not selec_log_file1:
                    st.write("No Parameter List available")
                else:
                    st.write("**Parameter List:**")
                    logs = selec_log_file_df1.astype(str)
                    st.dataframe(logs.T)

            with col2:
                st.dataframe(selec_test_data_df1)

        with test_tab3:
            st.subheader(
                "Show DBSCAN-CellX Results (Cluster Position Classification)")
            col1, col2,  = st.columns(2)
            if "Uncorrected_Cluster_Position" in selec_test_data_df1.columns:
                with col1:
                    st.write("**Uncorrected Cluster Positions**")
                    fig = px.scatter(x=selec_test_data_df1["X"],
                                     y=selec_test_data_df1["Y"],
                                     color=selec_test_data_df1["Uncorrected_Cluster_Position"],
                                     color_discrete_map={
                        "noise": "#161616",
                        "edge": "#E77700",
                        "center": "#588E00"})
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    st.write("**Corrected Cluster Positions**")
                    fig = px.scatter(x=selec_test_data_df1["X"],
                                     y=selec_test_data_df1["Y"],
                                     color=selec_test_data_df1["Cluster_Position"],
                                     color_discrete_map={
                        "noise": "#161616",
                        "edge": "#E77700",
                        "center": "#588E00"})
                    st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning(
                    "This Files does not have a *Uncorrected Cluster Classification*. Please enable it inthe Advanced Settings")

        with test_tab4:
            st.subheader("Show DBSCAN-CellX Results (Compare *Settings*)")
            col1, col2,  = st.columns(2)
            if st.session_state.agree_log_save == 1:

                with col1:
                    option_test_stem1 = st.selectbox(
                        'Dataset',
                        (list(test_data_list[0])), key="7")
                    index_bol1 = list(pd.DataFrame(test_data_list)[0].str.contains(
                        option_test_stem1))
                    option_test_num1 = st.selectbox(
                        'Test Run Number',
                        (pd.DataFrame(test_data_list)[1][index_bol1].tolist()[0]), key="8")
                    selec_test_data1 = st.session_state.text2 + \
                        pd.DataFrame(test_data_list)[2][index_bol1].tolist()[
                            0][option_test_num1-1]
                    selec_log_file1 = st.session_state.text2 + \
                        pd.DataFrame(test_data_list)[3][index_bol1].tolist()[
                            0][option_test_num1-1]
                    selec_test_data_df1 = pd.read_csv(
                        selec_test_data1, sep=";")
                    if not pd.DataFrame(test_data_list)[3][index_bol1].tolist()[
                            0][option_test_num1-1]:
                        st.write("No Parameter List available")
                    else:
                        selec_log_file_df1 = pd.read_csv(
                            selec_log_file1, sep=";")
                        fig1 = px.scatter(x=selec_test_data_df1["X"],
                                          y=selec_test_data_df1["Y"],
                                          color=selec_test_data_df1["Cluster_Position"],
                                          color_discrete_map={
                            "noise": "#161616",
                            "edge": "#E77700",
                            "center": "#588E00"})
                        st.plotly_chart(fig1, use_container_width=True)
                        st.write("Parameter List:")
                        logs = selec_log_file_df1.astype(str)
                        st.dataframe(logs.T)

                with col2:

                   option_test_stem2 = st.selectbox(
                       'Dataset',
                       (list(test_data_list[0])), key="9")
                   index_bol2 = list(pd.DataFrame(test_data_list)[0].str.contains(
                       option_test_stem2))
                   option_test_num2 = st.selectbox(
                       'Test Run Number',
                       (pd.DataFrame(test_data_list)[1][index_bol2].tolist()[0]), key="10")
                   selec_test_data2 = st.session_state.text2 + \
                       pd.DataFrame(test_data_list)[2][index_bol2].tolist()[
                           0][option_test_num2-1]
                   selec_log_file2 = st.session_state.text2 + \
                       pd.DataFrame(test_data_list)[3][index_bol2].tolist()[
                           0][option_test_num2-1]
                   selec_test_data_df2 = pd.read_csv(selec_test_data2, sep=";")
                   if not pd.DataFrame(test_data_list)[3][index_bol2].tolist()[
                           0][option_test_num2-1]:
                       st.write("No Parameter List available")
                   else:
                    selec_log_file_df2 = pd.read_csv(selec_log_file2, sep=";")

                    fig2 = px.scatter(x=selec_test_data_df2["X"],
                                      y=selec_test_data_df2["Y"],
                                      color=selec_test_data_df2["Cluster_Position"],
                                      color_discrete_map={
                        "noise": "#161616",
                        "edge": "#E77700",
                        "center": "#588E00"})
                    st.plotly_chart(fig2, use_container_width=True)
                    st.write("Parameter List:")
                    logs = selec_log_file_df2.astype(str)
                    st.dataframe(logs.T)
            else:
                st.warning(
                    "To compare different parameters, please enable *Keep Log-Files of Parameters* in the Advanced Settings")

        with test_tab5:
            st.subheader("Overlaying Microscopy Data")
            st.markdown("The user has the option to overlay the output DBSCAN classification with the original microscopy image data. The image file (i.e., original brightfield image in tiff, png, etc) corresponding to the test data set can be uploaded here.")
            uploaded_file2 = st.file_uploader(
                "Choose a file", key="Uploader_Microscopy")
            col1,col2,col3 = st.columns([1,3,1])
            if uploaded_file2 is not None:

                data = np.array(uploaded_file2)
                #save_path = st.session_state.text2 + \
                #    st.session_state.file[:-4] + "_test_data_"+".csv"
                #output_name = save_path[:-4] + 'DBSCAN_CELLX_output.csv'
                #df_sub_output = pd.read_csv(output_name, sep=";")
                fig, ax = plt.subplots(1)  # , figsize = (13,18))
                image = io.imread(uploaded_file2)
                plt.imshow(image, cmap='gray')
                plt.axis('on')
                #plt.margins(x=0, y=0)
                colors = {'edge': '#E77700', 'center': '#588E00',
                          'noise': '#161616'}
                plt.xlabel("X")
                plt.ylabel("Y")
                scatter = ax.scatter(selec_test_data_df1["X"],
                            selec_test_data_df1["Y"], s=10, c=selec_test_data_df1["Cluster_Position"].map(colors))
                classes = ["Edge", "Center", "Noise"]
                class_colours = ['#E77700', '#588E00', '#161616']
                recs = []
                for i in range(0, len(class_colours)):
                    recs.append(mpatches.Rectangle((0, 0), 1, 1, fc=class_colours[i]))
                plt.legend(recs, classes, bbox_to_anchor=(1.1, 1.05))
                with col2:
                    st.pyplot(fig, use_container_width=False)




@st.cache
def run_DBSCAN(data, save, pixel_ratio,cell_size, X, Y, edge_mode, angle_paramter, save_para, keep_uncorr):
    dbscan_cellx.main([data], save, pixel_ratio,cell_size, X,
                      Y, edge_mode, angle_paramter, save_para, keep_uncorr)

def page_run():
    st.subheader("Running DBSCAN-CellX")
    st.markdown("After validating the test run, the user apply DBSCAN-CellX to all files based on the *Settings*. If parameters need to be changed, please don't forget to submit them before starting the analysis. ")

    col1, col2 = st.columns([2, 3])
    with col1:
        st.subheader('Folder Picker')
        picker_data()
        picker_save()
        st.markdown(
            '*Hint: Directory paths must end with "/" in Unix-based systems or "\ " in Windows systems.')
    with col2:

        st.subheader("Data input")
        st.markdown("Please input a preliminary test file."
                    "Files can be added via Drag and Drop or browsing through the system.")
        if "uploaded_file3" not in st.session_state:
            st.session_state.uploaded_file3 = "Leer"

        uploaded_file3 = st.file_uploader(
            "Choose a file", accept_multiple_files= True)

        st.session_state.uploaded_file3 = uploaded_file3

        if "file_run" not in st.session_state:
            st.session_state.file_run = "Leer"
        #if st.session_state.uploaded_file3 is not None:
            #st.session_state.file_name = st.session_state.uploaded_file3.name
            #file_name = st.session_state.uploaded_file3.name
            #st.session_state.file_run = file_name

            #file_name = st.session_state.uploaded_file.name

            #st.session_state.file_run = file_name
        #st.write("Last Uplodaded File:", st.session_state.file_run)
    if uploaded_file3 is not None:
        file_names = []
        for i in uploaded_file3:
            name_file = i.name
            full_name = st.session_state.text + name_file
            file_names.append(str(full_name))
    log_df = pd.DataFrame({"Pixel Ratio": [str(st.session_state.pixel_rat)], "Cell Size": [str(st.session_state.cell_size)], "X-Dimension": [str(st.session_state.X)],
                           "Y-Dimension": [str(st.session_state.Y)], "Edge-Degree Detection": [str(st.session_state.edge_mode)], "Correction Angle": [str(st.session_state.angel)], "Uncorrected_Cluster_Positions": [str(st.session_state.keep_uncorr)]})
    
    col1,col2,col3 = st.columns ([1,3,1])
    with col2:
        st.write("**Current Settings**")
        log_df            

    with st.expander("Change Settings?"):
        sett_tab1, sett_tab2 = st.tabs(["Settings", "Advanced Settings"])
        with sett_tab1:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                #pixel_input()
                if "pixel_rat" not in st.session_state:
                    st.session_state.pixel_rat = 0.01
                if "cell_size" not in st.session_state:
                    st.session_state.cell_size = 0.01    
                if "X" not in st.session_state:
                     st.session_state.X = 0.01
                if "Y" not in st.session_state:
                     st.session_state.Y = 0.01
                pixel_rat = st.number_input(
                    'Please enter pixel edge size in microns (micron to pixel ratio)', value=st.session_state.pixel_rat)
                cell_size = st.number_input(
                    'Please enter the estimatedcell size in microns', value=st.session_state.cell_size)
                size_X = st.number_input(
                    'Please enter total pixels or microns in X direction', value=st.session_state.X)
                size_Y = st.number_input(
                'Please enter total pixels or microns in Y direction', value=st.session_state.Y)
                #clicked2 = st.button('Submit')
                #if clicked2:
                st.session_state.pixel_rat = pixel_rat
                st.session_state.X = size_X
                st.session_state.Y = size_Y
                st.session_state.cell_size  = cell_size

            with col2:
                pixel_kind = st.radio(
                    "Please enter if image resolution was measured in microns or pixels",
                    ('Microns', 'Pixel'))

                if pixel_kind == "Pixel":
                    size_X = size_X*pixel_rat
                    size_Y = size_Y*pixel_rat

            with sett_tab2:
                col1, col2 = st.columns([1, 2])
                with col1:
                    #parameter_input()
                    if "angel" not in st.session_state:
                     st.session_state.angel = 140

                    angel = st.number_input(
                        'Please enter the correction angle in degrees', value=st.session_state.angel)
                    st.session_state.angel = angel
                    #st.session_state.angel = angle

                    if "edge_mode" not in st.session_state:
                        st.session_state.edge_mode = 0
                    if "save_para" not in st.session_state:
                        st.session_state.save_para = 0
                    if "agree_log_save" not in st.session_state:
                        st.session_state.agree_log_save = 0
                    if "keep_uncorr" not in st.session_state:
                        st.session_state.keep_uncorr = 0

                    agree_edge = st.checkbox(
                        'Allow edge degree detection?', st.session_state.edge_mode)
                    if agree_edge:
                        st.session_state.edge_mode = 1
                    else:
                        st.session_state.edge_mode = 0

                    agree_edge = st.session_state.edge_mode
                    st.session_state.edge_mode = agree_edge
                    agree_para_save = st.checkbox(
                        'Save a seperate parameter list?', st.session_state.save_para)
                    if agree_para_save:
                        st.session_state.save_para = 1
                    else:
                        st.session_state.save_para = 0

                    agree_log_save = st.checkbox(
                        'Keep log files of parameters?', st.session_state.agree_log_save)
                    if agree_log_save:
                        st.session_state.agree_log_save = 1
                    else:
                        st.session_state.agree_log_save = 0
                    agree_log_save = st.session_state.agree_log_save

                    agree_kepp_uncorr = st.checkbox(
                        'Show uncorrected cluster positions?', st.session_state.keep_uncorr)
                    if agree_kepp_uncorr:
                        st.session_state.keep_uncorr = 1
                    else:
                        st.session_state.keep_uncorr = 0
                    agree_kepp_uncorr = st.session_state.keep_uncorr

                with col2:
                    st.write("**Explanation**")
                    st.write(
                        "*Correction angle:* Changes the exclusion angle for the edge correction. The smaller the angle, the more cells will be labeled as edge cells.")
                    st.write(
                        "*Edge degree detection:* Provides a discrete value of a cell's distance to edge.")
                    st.write(
                        "*Parameter list:* Allow seperate output of calculated Epsilon and n_min (input parameters for DBSCAN).")
                    st.write(
                        "*Log files:* Allow seperate output of input parameters.")
                    st.write(
                        "*Uncorrected cluster positions:* Allow output of uncorrected cluster postions in DBSCAN-CellX output file in addition to corrected cluster positions.")

    if st.button('Run DBSCAN-CellX'):
        for i in file_names:
            st.session_state.text2
            run_DBSCAN(i, st.session_state.text2,
                       st.session_state.pixel_rat,st.session_state.cell_size, st.session_state.X, st.session_state.Y, st.session_state.edge_mode, st.session_state.angel, st.session_state.save_para, st.session_state.keep_uncorr)
        first_file = file_names[0]
        if st.session_state.agree_log_save == 1:
            if st.session_state.edge_mode:
                edge_mode = "Enabled"
            else:
                edge_mode = "Disabled"
            if st.session_state.keep_uncorr:
                keep_uncorr = "Enabled"
            else:
                keep_uncorr = "Disabled"
            delimiter_path = st.session_state.text2[-1]
            name_stem = i.split(delimiter_path)[-1]
            save_path = st.session_state.text2 + name_stem
            log_df = pd.DataFrame({"Pixel Ratio": [str(st.session_state.pixel_rat)], "Cell Size": [str(st.session_state.cell_size)], "X-Dimension": [str(st.session_state.X)],
                                   "Y-Dimension": [str(st.session_state.Y)], "Edge-Degree Detection": [str(edge_mode)], "Correction Angle": [str(st.session_state.angel)], "Uncorrected_Cluster_Positions": [str(keep_uncorr)]})
            output_name_log = save_path[:-4] + "_log_files.csv"
            
            log_df.to_csv(output_name_log, sep=';', index=False)
        st.session_state.first_file = first_file[:-
                                                 4] + "_DBSCAN_CELLX_output.csv"
        st.write("DBSCAN-CELLX was successfull!")
        st.balloons()


def second_page():




    st.title('Visualize Data')
    st.markdown("Here, the user can visualize the output generated by DBSCAN-CellX in different ways. The user can choose to filter the output files by column and also change the appearance by changing the colouring parameter.")

    picker_save()
    st.markdown(
        '*Hint: Directory paths must end with "/" in Unix-based systems or "\ " in Windows systems.')
    if st.session_state.text2 != "Output data directory":
        mypath = st.session_state.text2
        onlyfiles = [f for f in listdir(
            mypath) if isfile(join(mypath, f))]
        matches = []
        matches_sub = []
        test_data_list = []
        for match in onlyfiles:
            if "_DBSCAN_CELLX_output.csv" in match and "_test_data_" not in match:
                matches.append(match)
                matches_sub.append(match[:-24])
        unique_data = set(sorted(matches_sub, key=len))
        if len(unique_data) == 0:
            st.warning("No DBSCAN-CellX output files in this directory.")
        else:    
            for stem in unique_data:
                stem_data_list = []
                stem_parameter_list = []
                test_file = []
                param_list = []
                for file in matches:
                        if (stem+"_DBSCAN_CELLX_output.csv") in file:
                            test_file.append(file)
                            if (stem + "_log_files.csv") in onlyfiles:
                                stem_parameter_list.append(
                                    stem + "_log_files.csv")
                            else:
                                stem_parameter_list.append("")
                            if (stem + "_paramter_list.csv") in onlyfiles:
                                param_list.append(
                                    stem + "_paramter_list.csv")
                            else:
                                param_list.append("")
                stem_data_list = [stem,
                                      test_file, stem_parameter_list, param_list]
                test_data_list.append(stem_data_list)
            test_data_list = pd.DataFrame(test_data_list)

            col1,col2,col3 = st.columns([1,2,1])
            with col2:

                option_test_stem1 = st.selectbox(
                    'Dataset',
                    (list(test_data_list[0])), key="3")
                index_bol1 = list(pd.DataFrame(test_data_list)[0].str.contains(
                    option_test_stem1))
                selec_test_data1 = st.session_state.text2 + \
                    pd.DataFrame(test_data_list)[1][index_bol1].tolist()[
                        0][0]
                selec_log_file1 = pd.DataFrame(test_data_list)[2][index_bol1].tolist()[
                    0][0]
                selec_param_file1 = pd.DataFrame(test_data_list)[3][index_bol1].tolist()[
                    0][0]
                #st.write("File:", selec_test_data1)
                if not selec_log_file1:
                    selec_test_data_df1 = pd.read_csv(selec_test_data1, sep=";")
                else:
                    selec_log_file1 = st.session_state.text2 + \
                        pd.DataFrame(test_data_list)[2][index_bol1].tolist()[
                            0][0]
                    selec_test_data_df1 = pd.read_csv(
                        selec_test_data1, sep=";")
                    selec_log_file_df1 = pd.read_csv(selec_log_file1, sep=";")
                if not selec_param_file1:
                    selec_test_data_df1 = pd.read_csv(selec_test_data1, sep=";")
                else:
                    selec_param_file1 = st.session_state.text2 + \
                        pd.DataFrame(test_data_list)[3][index_bol1].tolist()[
                            0][0]
                    selec_test_data_df1 = pd.read_csv(
                        selec_test_data1, sep=";")
                    selec_param_file1_df = pd.read_csv(selec_param_file1, sep=";")
                df_IFN_all_sub = selec_test_data_df1

                IM_ID = st.selectbox(
                            'Select Image ID',
                            (list(set(df_IFN_all_sub.iloc[:, 0]))), key="Input_data_options")
                df_sub_IM = df_IFN_all_sub[df_IFN_all_sub["ImageNumber"] ==
                                           IM_ID]
                color_option = st.selectbox(
                    'Selecet Color Code',
                    ("Cluster_Position", "Edge_Degree", "Cells_in_Cluster"))   


            col1,col2,col3 = st.columns([1,2,1])
            with col1:
                if not selec_log_file1:
                            st.write("No Parameter List available")
                else:
                            st.write("**Log List:**")
                            logs = selec_log_file_df1.astype(str)
                            st.dataframe(logs.T)
            with col2:
                fig = px.scatter(x=df_sub_IM["X"],
                                y=df_sub_IM["Y"],
                                     color=df_sub_IM[color_option],
                                     color_discrete_map={
                        "noise": "#161616",
                        "edge": "#E77700",
                        "center": "#588E00"})
                if color_option == "Cluster_Position":
                    fig.update_layout(legend_title_text='Cluster Position')
                    st.plotly_chart(fig, use_container_width=True)
                elif color_option == "Edge_Degree":
                    fig = fig.update_layout(legend_title_text='Edge Degree')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    fig = fig.update_layout(legend_title_text='Cells in Cluster')
                    st.plotly_chart(fig, use_container_width=True)
                #st.plotly_chart(fig, use_container_width=True)
            with col3:
                if not selec_param_file1:
                    st.write("No Parameter List available")
                else:
                    st.latex("Parameter List:")
                    selec_param_file1_df.iloc[IM_ID-1,
                                              2] = round(selec_param_file1_df.iloc[IM_ID-1, 2], 2)
                    params = selec_param_file1_df.astype(str)
                    eps = params.iloc[IM_ID-1,2]
                    nmin = params.iloc[IM_ID-1,1]
                    st.latex("\epsilon: "+eps)
                    st.latex("N_{min}: " + nmin)




if __name__ == "__main__":
    main()
