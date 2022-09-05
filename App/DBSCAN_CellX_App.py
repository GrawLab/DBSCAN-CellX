import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px
import numpy as np
import csv
import subprocess
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import os
from persist import persist, load_widget_state
from skimage import io
import matplotlib.pyplot as plt
from dbscan_cellx import dbscan_cellx
from PIL import Image

#dirname = None
#file_name = None

def main():
    # Register your pages
    pages = {
        "Homepage": home,
        "Run DBSCAN-CellX": page_one,
        "Visualization": second_page,
    }

    st.sidebar.title("App with pages")

    # Widget to select your page, you can choose between radio buttons or a selectbox
    page = st.sidebar.selectbox("Select your page", tuple(pages.keys()))
    #page = st.sidebar.radio("Select your page", tuple(pages.keys()))

    # Display the selected page with the session state
    pages[page]()


def home():
    st.title("DBSCAN-CellX - Homepage")
    imagelogo = Image.open('./Images/Logo.jpg')
    st.image(imagelogo, caption='Logo')

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


def page_one():
    st.title('Run DBSCAN-CellX')
    st.markdown("This is the main part of the DBSCAN-CellX App. This page provides the user to input their data, run a Test-Run and change selected paramters.")


    st.subheader('Folder Picker')   
    def picker_data(initial_path=Path()):
        root = tk.Tk()
        root.withdraw()
        # Make folder picker dialog appear on top of other windows
        root.wm_attributes('-topmost', 1)

        if "text" not in st.session_state:
            st.session_state.text = initial_path.absolute()
        # Folder picker button
        
        st.write('Please select the data input folder:')
        clicked = st.button('Data Folder Picker')
        if clicked:
            text_int = st.text_input(
                'Selected folder:', filedialog.askdirectory(master=root))
            st.session_state.text = text_int + "/"
        return st.session_state.text

    def picker_save(initial_path2=Path()):
        root = tk.Tk()
        root.withdraw()
        # Make folder picker dialog appear on top of other windows
        root.wm_attributes('-topmost', 1)
        if "text2" not in st.session_state:
            st.session_state.text2 = initial_path2.absolute()
        # Folder picker button
        #st.title('Folder Picker')
        st.write('Please select a save folder:')
        clicked = st.button('Save Folder Picker')
        if clicked:
            text_int = st.text_input(
                'Selected folder:', filedialog.askdirectory(master=root))
            st.session_state.text2 = text_int + "/"
        return st.session_state.text2

    col1, col2,  = st.columns(2)
    with col1:
        picker_data()

    with col2:
        picker_save()

    st.write("This is your selected Data folder:", st.session_state.text)
    st.write("This is your selected Save Folder:", st.session_state.text2)

    st.subheader("Data input")
    st.markdown("Please input a TEST file. This file can be a single input file in .csv format structured as mentioned before."
    "The user can input the file via Drag and Drop or browse it youself.")
    uploaded_file = st.file_uploader("Choose a file")

    if "file" not in st.session_state:
        st.session_state.file = "Leer"

    if uploaded_file is not None:
        st.write("This table shows you the input data file. You can check if everything is as wished.")
        df = pd.read_csv(uploaded_file, sep=";")
        st.dataframe(df)
        file_name = uploaded_file.name
        st.session_state.file = str(st.session_state.text) + file_name[:-4]

 

    @st.cache
    def run_DBSCAN(data, save, pixel_ratio, X, Y, edge_mode, angle_paramter, save_para):
        dbscan_cellx.main([data], save, pixel_ratio, X,
                          Y, edge_mode, angle_paramter, save_para)

    st.subheader("Changing Paramters")
    st.markdown("In this part the user can change and input paramters. The three input paramters Pixel-Ratio, Pixels in X-Direction and Pixels in Y-Direction must be input by the user."
    " The user also has to define if the measurments are provided as Microns or Pixels."
    "       "
    "The option Correction Angle refers to the exclusion angle which determines when edge cells are still considered edge or center."
    "The user can also allow a seperate Edge-Degree detection (Causing higher computational times) and if a parameter list of the calculated paramters n_min and Epsilon should be saved in the save folder.")
    col1, col2,  = st.columns(2)

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

        return (st.session_state.angel)

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
            size_X = size_X/pixel_rat
            size_Y = size_Y/pixel_rat
        parameter_input()
        angle_paramter = st.session_state.angel
        agree_edge = st.checkbox('Allow Edge Degree Detection?')
        edge_mode = 0
        if agree_edge:
            edge_mode = 1
        agree_para_save = st.checkbox('Save a seperate Parameter-List?')
        save_para = 0
        if agree_para_save:
            save_para = 1

    st.markdown("Running the test will output a file with the file extension name _test_data."
    " If the run was succesful adepnending on the users input additional files will be saved, one being the DBSCAN output wit hthe file extension name DBSCAN-CellX output."
    "Also an example visualization of the DBSCAN-CellX output is generated, which depicts the first image according to the Image ID.")
    if st.button('Run Test'):
        df_sub = df[df["ImageNumber"] == 1]
        save_path = str(st.session_state.text2 ) + file_name[:-4] + "_test_data.csv"
        df_sub.to_csv(save_path, sep=';', index=False)
        st.write('Run DBSCAN-CellX')
        run_DBSCAN(save_path, st.session_state.text2,
                   pixel_rat, size_X, size_Y, edge_mode, angle_paramter, save_para)
        output_name = save_path[:-4] + 'DBSCAN_CELLX_output.csv'
        df_sub_output = pd.read_csv(output_name, sep=";")
        fig = px.scatter(x=df_sub_output["X"],
                         y=df_sub_output["Y"],
                         color=df_sub_output["Cluster_Position"])

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Overlaying Microscopy Data")
    st.markdown("If the test run was succesfull the user has the option to overlay the output DBSCAN classification with the original microscopy image file."
    " The image file can for example be a brightfield image of the original cell culture. To input the image file just upload the corresponding image file.")
    agree = st.checkbox('Overlay Microscopy Image')
    if agree:
        uploaded_file2 = st.file_uploader(
            "Choose a file", key="Uploader_Microscopy")
        if uploaded_file2 is not None:

            data = np.array(uploaded_file2)
            save_path = st.session_state.text2 + \
                file_name[:-4] + "_test_data.csv"
            output_name = save_path[:-4] + 'DBSCAN_CELLX_output.csv'
            df_sub_output = pd.read_csv(output_name, sep=";")
            fig, ax = plt.subplots(1)  # , figsize = (13,18))
            image = io.imread(uploaded_file2)
            plt.imshow(image, cmap='gray')
            plt.axis('on')
            plt.margins(x=0, y=0)
            colors = {'edge': 'red', 'center': 'green',
                      'noise': 'blue'}
            plt.scatter(df_sub_output["X"],
                        df_sub_output["Y"], s=10, c=df_sub_output["Cluster_Position"].map(colors))
            st.pyplot(fig, use_container_width=True)

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
                       pixel_rat, size_X, size_Y, edge_mode, angle_paramter, save_para)
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
