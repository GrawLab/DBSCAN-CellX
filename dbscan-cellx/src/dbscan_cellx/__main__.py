# __main__.py

import argparse
from dbscan_cellx import dbscan_cellx


def main(files, save,
         pixel_ratio,cell_size,  size_x, size_y, edge_mode, angel_parameter, save_parameter, keep_uncorrected):
    """Read the Real Python article feed"""

    dbscan_cellx.main(files, save,
                      pixel_ratio, cell_size, size_x, size_y, edge_mode, angel_parameter, save_parameter, keep_uncorrected)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='')
    parser.add_argument('-f', '--files', help='Add path to files in .csv format.',
                        default=[],
                        nargs='*')
    parser.add_argument('-sa', '--save', help='Specify path to directory where outputf files should be saved. Note: path should end with "/" in unix based systems or with "\ " in Windows systems.',
                        default='C:/Users/Pascal/Master/Graw/')
    parser.add_argument('-p', '--pixel_ratio', help='Plese specify the pixel edge size in microns (micron to pixel ratio)', type=float,
                        default=2.8986)
    parser.add_argument('-c', '--cell_size', help='Plese specify the estimated cell size in  microns', type=float,
                        default=20)
    parser.add_argument('-x', '--size_x', help='Please enter image size in microns in X direction', type=float,
                        default=938.40)
    parser.add_argument('-y', '--size_y', help='Please enter image size in microns in Y direction', type=float,
                        default=565.80)
    parser.add_argument('-e', '--edge_mode', help='Specify if edge degree should be detected. Enter 1 if edge degree is desired, 0 if it is not.', type=int,
                        default=1)
    parser.add_argument('-a', '--angel_parameter', help='Please specify the the threshold angle for edge correction in degrees. The smaller the angle, the more cells will be labeled as edge cells.', type=int,
                        default=140)
    parser.add_argument('-sp', '--save_parameter', help='Allow seperate output of calculated Epsilon and n_min. Enter 1 if output is desired, 0 if it is not.', type=int,
                        default=1)
    parser.add_argument('-ku', '--keep_uncorrected', help='Allow output of uncorrected cluster postions in DBSCAN-CellX output file in addition to corrected cluster positions. Enter 1 if output is desired, 0 if it is not.', type=int,
                        default=1)

    args = parser.parse_args()
    main(**vars(args))
