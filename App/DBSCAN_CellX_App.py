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
from dbscan_cellx import dbscan_cellx
from PIL import Image
from os import listdir
matplotlib.use('Agg')
#dirname = None
#file_name = None
st.set_page_config(layout="wide")

#Overall Structure Call
def main():
    # Register your pages
    pages = {
        "Homepage": home,
        "Input Data": page_data,
        "Settings": page_settings,
        "Test Area": page_test,
        "Run DBSCAN-CellX": page_run,
        "Visualization": second_page,
    }

    st.sidebar.title("App with pages")

    # Widget to select your page, you can choose between radio buttons or a selectbox
    page = st.sidebar.selectbox("Select your page", tuple(pages.keys()))
 

    # Display the selected page with the session state
    pages[page]()

#Home Page
def home():
    st.title("DBSCAN-CellX - Homepage")
    imagelogo = Image.open('./Images/Logo.jpg')
    st.image(imagelogo,  width=300)

    st.markdown('DBSCAN-CellX is a clustering and positional classification tool espacially designed for cell cultures (Quelle).'
                "This tool utilzes the original DBSCAN algorithm from Sander, J., et. al (Sander, J. et al., 1998) to determine unique clusters a given cell population."
                "Additional algorithms allow a clear and robust classification of noise, edge and center cells."
                )

    st.subheader("Data Requirments")
    st.markdown("To fully utilze DBSCAN-CellX thorugh this application certain data structure reqeuirments have to be met. The table has to consits of at least 4 columns depicting, a unique Image_ID, Cell ID, X and Y position."
    "Each row represents a unique cell. The columns of Image_ID refers to a unique ID for each image remaining unchaged for each cell i a given image. The Cell ID is a unique ID for each cell in a given image."
                "Both Image ID and Cell ID begin at 1 incrementing by 1 by each row. The data strucutre is comparable to the data output of CellProfiler (Stirling DR; 2021).")
    
    image = Image.open('./Images/Data_structure.PNG')
    st.image(image, caption='Required Data Structure')

    st.subheader("Using this App")
    st.markdown("Is App is a easy to use GUI to simplify the usage of the Python package DBSCAN-CellX and to directly visualize the output, while also providing the users possibilieties to change paramters on the fly."
    " The next pages of this App can be found in the sidebar. The page Running DBSCAN-CellX is the main part of the App. As the name suggests it allows the user to input theri data and run DBSCAN-CellX."
    "It furhtermore allows to run a seperate test-run of DBSCAN-CellX to ensure that the given input parameters output satifying results."
    "The last page called Visualization allows the user to directly visualize the output data in a image wise depiction of cell positions in a cathersian grid, while also allowing the customazation of the vsiulaization.")

    st.subheader("Data Output")
    st.markdown("DBSCAN-CellX outputs a .csv file with the same name as the input file and the file name extension DBSCAN_CellX_output. The main output results in four addtional columns and if the user specified the Edge Detection a fith column is generated. "
                "Please find furhter information on the Github-Page (https://github.com/PasLukas/DBSCAN-CellX)")
    image2 = Image.open('./Images/Data_output.PNG')
    st.image(image2, caption='Output  Data Structure')


def page_data():
    st.title('Run DBSCAN-CellX')
    st.markdown("This is the main part of the DBSCAN-CellX App. This page provides the user to input their data, run a Test-Run and change selected paramters.")

#Adress Data Directory
    def picker_data():
        if "text" not in st.session_state:
            st.session_state.text = "Data Path"
        data_path = st.text_input('Data input', st.session_state.text)
        st.session_state.text = data_path
        return st.session_state.text
#Adress Save Directory
    def picker_save():
        if "text2" not in st.session_state:
            st.session_state.text2 = "Save Path"
        save_path = st.text_input('Save input', st.session_state.text2)
        st.session_state.text2 = save_path
        return st.session_state.text2

#Call the Adress Directory Functions
    col1, col2  = st.columns([2,3])
    with col1:
        st.subheader('Folder Picker')   
        picker_data()
        picker_save()
    with col2:



        st.subheader("Data input")
        st.markdown("Please input a TEST file. This file can be a single input file in .csv format structured as mentioned before."
        "The user can input the file via Drag and Drop or browse it youself.")
        if "uploaded_file" not in st.session_state:
            st.session_state.uploaded_file = "Leer"
        
        uploaded_file = st.file_uploader(
            "Choose a file")

        st.session_state.uploaded_file = uploaded_file

        if "file" not in st.session_state:
            st.session_state.file = "Leer"
        if "last_file" not in st.session_state:
            st.session_state.last_file = "Leer"



        if st.session_state.uploaded_file is not None:
            last_file = uploaded_file.name
    
            st.write("Last Input:",last_file)
            st.header("Input Data")
    if st.session_state.uploaded_file is not None:
        if "df" not in st.session_state:
            st.session_state.df = "Leer"
        st.session_state.df = pd.read_csv(
            st.session_state.uploaded_file, sep=";")
        df = st.session_state.df
        tab1, tab2 = st.tabs(["Visualize Data", "Table"])
        with tab1:
            col1, col2, col3 = st.columns([1,2,1])

            with col2:
                if "input_data_options" not in st.session_state:
                    st.session_state.input_data_options = 1
                st.session_state.input_data_options = st.selectbox(
                                'Image Number',
                                (list(set(df.iloc[:,0]))), key="Input_data_options")
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

        file_name = st.session_state.uploaded_file.name
        st.session_state.file = file_name

 


    

def page_settings():
    st.subheader("Changing Paramters")
    st.markdown("In this part the user can change and input paramters. The three input paramters Pixel-Ratio, Pixels in X-Direction and Pixels in Y-Direction must be input by the user."
                " The user also has to define if the measurments are provided as Microns or Pixels."
                "       "
                "The option Correction Angle refers to the exclusion angle which determines when edge cells are still considered edge or center."
                "The user can also allow a seperate Edge-Degree detection (Causing higher computational times) and if a parameter list of the calculated paramters n_min and Epsilon should be saved in the save folder.")

    
    def pixel_input():
        if "pixel_rat" not in st.session_state:
            st.session_state.pixel_rat = 0.01
        if "X" not in st.session_state:
            st.session_state.X = 0.01
        if "Y" not in st.session_state:
            st.session_state.Y = 0.01
        pixel_rat = st.number_input(
            'Please enter Pixel/Microns Ratio', value=st.session_state.pixel_rat)
        size_X = st.number_input(
            'Please enter total pixels/microns in X direction', value=st.session_state.X)
        size_Y = st.number_input(
            'Please enter total pixels/microns in Y direction', value=st.session_state.Y)
        clicked2 = st.button('Submit')
        if clicked2:
            st.session_state.pixel_rat = pixel_rat
            st.session_state.X = size_X
            st.session_state.Y = size_Y
        return (st.session_state.pixel_rat, st.session_state.X, st.session_state.Y)

    def parameter_input():
        if "angel" not in st.session_state:
            st.session_state.angel = 140

        angel = st.number_input(
            'Please enter the correction angle', value=st.session_state.angel)
        st.session_state.angel = angel
        angle = st.session_state.angel

        return (st.session_state.angel)

    sett_tab1, sett_tab2 = st.tabs(["Settings", "Advanced Settings"])
    with sett_tab1:
        col1, col2,col3  = st.columns([1,1,1])
        with col1:
            pixel_input()
            st.write("Data:", st.session_state.X)
            pixel_rat = st.session_state.pixel_rat
            size_X = st.session_state.X
            size_Y = st.session_state.Y


        with col2:
            pixel_kind = st.radio(
                "Please enter if image resolution was measured in microns or pixels",
                ('Microns', 'Pixel'))

            if pixel_kind == "Pixel":
                size_X = size_X*pixel_rat
                size_Y = size_Y*pixel_rat

        with sett_tab2:
            col1,col2 = st.columns([1,2])
            with col1:
                parameter_input()
                if "edge_mode" not in st.session_state:
                    st.session_state.edge_mode = 0
                if "save_para" not in st.session_state:
                    st.session_state.save_para = 0
                if "agree_log_save" not in st.session_state:
                    st.session_state.agree_log_save = 0
                if "keep_uncorr" not in st.session_state:
                    st.session_state.keep_uncorr = 0

                agree_edge = st.checkbox(
                    'Allow Edge Degree Detection?', st.session_state.edge_mode)
                if agree_edge:
                    st.session_state.edge_mode = 1
                else:
                    st.session_state.edge_mode = 0
                    
                agree_edge = st.session_state.edge_mode

                agree_para_save = st.checkbox(
                    'Save a seperate Parameter-List?', st.session_state.save_para)
                if agree_para_save:
                    st.session_state.save_para = 1
                else:
                    st.session_state.save_para = 0

                agree_log_save = st.checkbox(
                    'Keep Log-Files of Parameters?', st.session_state.agree_log_save)
                if agree_log_save:
                    st.session_state.agree_log_save = 1
                else:
                    st.session_state.agree_log_save = 0
                agree_log_save = st.session_state.agree_log_save

                agree_kepp_uncorr = st.checkbox(
                    'Show uncorrected Cluster Positions?', st.session_state.keep_uncorr)
                if agree_kepp_uncorr:
                    st.session_state.keep_uncorr = 1
                else:
                    st.session_state.keep_uncorr = 0
                agree_kepp_uncorr = st.session_state.keep_uncorr


            with col2:
                with st.expander("See explanation"):
                    st.write("**Explanation**")
                    st.write("*Correction Angle:* Changes the exclusion angle for the edge correction.")
                    st.write("*Edge Detection:* Provides an discrete value of a cell's distance to edge")
                    st.write("*Paramter List:* Allow seperate output of calculated Epsilon and n_min")
                    st.write("*Log Files:* Allow seperate output of input parameters")
                    st.write("*Uncorrected Cluster Positions:* Allow output of uncorrected Culster Postions in DBSCAN-CellX Output File")

def page_test():
    @st.cache
    def run_DBSCAN(data, save, pixel_ratio, X, Y, edge_mode, angle_paramter, save_para, keep_uncorr):
        dbscan_cellx.main([data], save, pixel_ratio, X,
                          Y, edge_mode, angle_paramter, save_para, keep_uncorr)
    st.subheader("Test Run")
    st.write("Note: Running a Test Run creates and saves a seperate *test_data* file and *DBSCAN_CellX_output* basedon the input data in the save directory. Depending on the chosen Advanced Setting furhter files may be created.")
    if "test_run_counter" not in st.session_state:
            st.session_state.test_run_counter = 0
    if st.button('Run Test'):
        df = st.session_state.df
        st.session_state.test_run_counter = st.session_state.test_run_counter+1
        df_sub = df[df.iloc[:, 0] == st.session_state.input_data_options]
        save_path = str(st.session_state.text2) + st.session_state.file[:-4] + "_test_data_"+str(
            st.session_state.test_run_counter) + ".csv"
        st.write(save_path)
        df_sub.to_csv(save_path, sep=';', index=False)
        st.write('Run DBSCAN-CellX')
        run_DBSCAN(save_path, st.session_state.text2,
                   st.session_state.pixel_rat, st.session_state.X, st.session_state.Y, st.session_state.edge_mode, st.session_state.angel, st.session_state.save_para, st.session_state.keep_uncorr)
        if st.session_state.agree_log_save == 1:
            log_df = pd.DataFrame({"Pixel Ratio": [st.session_state.pixel_rat], "X-Dimension":[st.session_state.X],
                                   "Y-Dimension": [st.session_state.Y], "Edge-Degree Detection": [st.session_state.edge_mode], "Correction Angle": [st.session_state.keep_uncorr], "Uncorrected_Cluster_Positions": [st.session_state.keep_uncorr]})
            output_name_log = save_path[:save_path.find(str(st.session_state.test_run_counter))-1] + '_log_files_' + \
                str(st.session_state.test_run_counter) + ".csv"
            log_df.to_csv(output_name_log, sep=';', index=False)
  
    
    if st.session_state.test_run_counter != 0:
        st.subheader("Compare Test Results")
        st.write("Choose between different options to compare test results to.")
        st.write("Use the Dropdown-Menu to choose a specific Test-File. If a Log-File was created it will show the log-file table.")
        save_path = str(st.session_state.text2) + st.session_state.file[:-4] + "_test_data_"+str(
            st.session_state.test_run_counter) + ".csv"
        output_name = save_path[:-4] + '_DBSCAN_CELLX_output.csv'

        col1, col2,col3  = st.columns([1,2,1])
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
                        stem_parameter_list.append(stem + "_test_data_log_files_" + file[-25] + ".csv")
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
                (pd.DataFrame(test_data_list)[1][index_bol1].tolist()[0]), key="2")
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
            col1,col2,col3 = st.columns([1,2,1])
            with col1:
                if not selec_log_file1:
                    st.write("No Parameter List available")
                else:
                    st.write("Parameter List:")
                    st.dataframe(selec_log_file_df1.T)

            with col2:
                #df_sub_output = pd.read_csv(output_name, sep=";")
                fig = px.scatter(x=selec_test_data_df1["X"],
                                 y=selec_test_data_df1["Y"],
                                 color=selec_test_data_df1["Cluster_Position"])
                st.plotly_chart(fig, use_container_width=True)


        with test_tab2:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if not selec_log_file1:
                    st.write("No Parameter List available")
                else:
                    st.write("Parameter List:")
                    st.dataframe(selec_log_file_df1.T)
            with col2:
                st.dataframe(selec_test_data_df1)

        with test_tab3:

            col1, col2,  = st.columns(2)
            if "Uncorrected_Cluster_Position" in selec_test_data_df1.columns:
                with col1:
                    st.write("Uncorrected Cluster Positions")
                    fig = px.scatter(x=selec_test_data_df1["X"],
                                     y=selec_test_data_df1["Y"],
                                     color=selec_test_data_df1["Uncorrected_Cluster_Position"])
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    st.write("Corrected Cluster Positions")
                    fig = px.scatter(x=selec_test_data_df1["X"],
                                     y=selec_test_data_df1["Y"],
                                     color=selec_test_data_df1["Cluster_Position"])
                    st.plotly_chart(fig, use_container_width=True)

            else:
                st.write(
                    "This Files does not have a *Uncorrected Cluster Classification*. Please enable it inthe Advanced Settings")
            

        with test_tab4:
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
                        (pd.DataFrame(test_data_list)[1][index_bol1].tolist()[0]),key="8")
                    selec_test_data1 = st.session_state.text2 + \
                        pd.DataFrame(test_data_list)[2][index_bol1].tolist()[
                            0][option_test_num1-1]
                    selec_log_file1 = st.session_state.text2 + \
                        pd.DataFrame(test_data_list)[3][index_bol1].tolist()[
                            0][option_test_num1-1]
                    selec_test_data_df1 = pd.read_csv(selec_test_data1, sep=";")
                    if not pd.DataFrame(test_data_list)[3][index_bol1].tolist()[
                            0][option_test_num1-1]:
                        st.write("No Parameter List available")
                    else:
                        selec_log_file_df1 = pd.read_csv(selec_log_file1, sep=";")
                        fig1 = px.scatter(x=selec_test_data_df1["X"],
                                          y=selec_test_data_df1["Y"],
                                          color=selec_test_data_df1["Cluster_Position"])
                        st.plotly_chart(fig1, use_container_width=True)
                        st.dataframe(selec_log_file_df1)



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
                                          color=selec_test_data_df2["Cluster_Position"])
                    st.plotly_chart(fig2, use_container_width=True)
                    st.dataframe(selec_log_file_df2)
            else:
                st.write("To compare different paramters please enable *Keep Log-Files of Parameters* in the Advanced Settings")

    

        with test_tab5:
            st.subheader("Overlaying Microscopy Data")
            st.markdown("If the test run was succesfull the user has the option to overlay the output DBSCAN classification with the original microscopy image file."
            " The image file can for example be a brightfield image of the original cell culture. To input the image file just upload the corresponding image file.")
            agree = st.checkbox('Overlay Microscopy Image')
            if agree:
                uploaded_file2 = st.file_uploader(
                    "Choose a file", key="Uploader_Microscopy")
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
                    plt.margins(x=0, y=0)
                    colors = {'edge': 'red', 'center': 'green',
                              'noise': 'blue'}
                    plt.scatter(selec_test_data_df1["X"],
                                selec_test_data_df1["Y"], s=10, c=selec_test_data_df1["Cluster_Position"].map(colors))
                    st.pyplot(fig, use_container_width=True)

def page_run():
    st.subheader("Running DBSCAN-CellX")
    st.markdown("If the user is happy with the test results, the user can now run DBSCAN-CellX on all the desired files. The input paramters used are the ones submitted before."
    " If the user wants to change the paramters for the full run, just change the paramters and submit them. After the upload the user can run DBSCAN-CellX and is greeted with an animation if the run was succesfull.")
    agree2 = st.checkbox('Run Full')
    if "first_file" not in st.session_state:
        st.session_state.first_file = None
    if agree2:
        uploaded_file3 = st.file_uploader(
            "Choose a file", key="Uploader_All_Files",accept_multiple_files = True)
        if uploaded_file3 is not None:
            file_names = []
            for i in uploaded_file3:
                name_file = i.name
                full_name = st.session_state.text + name_file
                file_names.append(str(full_name))
    if st.button('Run DBSCAN-CellX'):
        for i in file_names:
            run_DBSCAN(i, st.session_state.text2,
                       st.session_state.pixel_rat, st.session_state.X, st.session_state.Y, st.session_state.edge_mode, angle_paramter, st.session_state.save_para)
        first_file = file_names[0]
        st.session_state.first_file = first_file[:-4] + "DBSCAN_CELLX_output.csv"
        st.write("DBSCAN-CELLX was successfull!")
        st.balloons()


            



def second_page ():
    st.title('Visualize Data')
    st.markdown("This is the last page of the App. Here the user can fully visualize the output generated by DBSCAN-CellX."
    " If a test run or a full DBSCAN-CellX run was performed beforehand a example file, which is the first file generated in the beforehand DBSCAN-CellX run, is opened."
    " If the user wishes to visualize a differet file just upload one single file. the user can choose to filter the output files by column and also change the appearance by changing the coloring paramter.")
    if st.session_state.first_file is not None:
        df_IFN_all = pd.read_csv(st.session_state.first_file, sep=";")
        st.dataframe(df_IFN_all)
        df_IFN_all_sub = df_IFN_all


    uploaded_file = st.file_uploader("Choose a file")
    #uploaded_file
    if uploaded_file is not None:
        df_IFN_all = pd.read_csv(uploaded_file, delimiter=";")
        st.dataframe(df_IFN_all)
        #df_IFN_all_sub = df_IFN_all[["ImageNumber", "X", "Y",
        #                             "Cell_ID", "Cell_in_Image", "Cluster_Position", "Edge_Degree", "Cells_in_Cluster"]]


        df_IFN_all_sub = df_IFN_all
        options = st.multiselect(
            'Set Filters',
            list(df_IFN_all_sub.columns),
            ["ImageNumber"])

        st.write('You selected:', options)
        color_option = st.selectbox(
                'Selecet Color Code',
                ("Cluster_Position", "Edge_Degree", "Cells_in_Cluster"))

        col1, col2, col3, col4, = st.columns(4)

        try:
            with col1:
                id = np.where(df_IFN_all_sub.columns == options[0])
                numers = list(
                    df_IFN_all_sub[list(df_IFN_all_sub.columns)[int(id[0])]].unique())
                numers.sort()
                option1 = st.selectbox(
                    'Selecet Single Fitler Value',
                    numers)

            with col2:
                id = np.where(df_IFN_all_sub.columns == options[1])
                numers = list(
                    df_IFN_all_sub[list(df_IFN_all_sub.columns)[int(id[0])]].unique())
                numers.sort()
                option2 = st.selectbox(
                    'Selecet Single Fitler Value',
                    numers)

            with col3:
                id = np.where(df_IFN_all_sub.columns == options[2])
                numers = list(
                    df_IFN_all_sub[list(df_IFN_all_sub.columns)[int(id[0])]].unique())
                numers.sort()
                option3 = st.selectbox(
                    'Selecet Single Fitler Value',
                    numers)

            with col4:
                id = np.where(df_IFN_all_sub.columns == options[3])
                numers = list(
                    df_IFN_all_sub[list(df_IFN_all_sub.columns)[int(id[0])]].unique())
                numers.sort()
                option4 = st.selectbox(
                    'Selecet Single Fitler Value',
                    numers)
        except:
            print("")

        if len(options) == 4:
            df_4 = df_IFN_all_sub[(df_IFN_all_sub[options[0]] == option1) & (df_IFN_all_sub[options[1]] == option2)
                                  & (df_IFN_all_sub[options[2]] == option3) & (df_IFN_all_sub[options[3]] == option4)]
            fig = px.scatter(x=df_4["X"],
                             y=df_4["Y"],
                             color=df_4[color_option])
        elif len(options) == 3:
            df_3 = df_IFN_all_sub[(df_IFN_all_sub[options[0]] == option1) & (df_IFN_all_sub[options[1]] == option2)
                                  & (df_IFN_all_sub[options[2]] == option3)]
            fig = px.scatter(x=df_3["X"], y=df_3["Y"], color=df_3[color_option])
        elif len(options) == 2:
            df_2 = df_IFN_all_sub[(df_IFN_all_sub[options[0]] == option1) & (
                df_IFN_all_sub[options[1]] == option2)]
            fig = px.scatter(x=df_2["X"],
                             y=df_2["Y"],
                             color=df_2[color_option])
        else:
            df_1 = df_IFN_all_sub[(df_IFN_all_sub[options[0]] == option1)]
            fig = px.scatter(x=df_1["X"],
                             y=df_1["Y"],
                             color=df_1[color_option])


        st.plotly_chart(fig, use_container_width=True)





if __name__ == "__main__":
    main()
