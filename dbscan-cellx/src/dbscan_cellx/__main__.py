# __main__.py

import argparse
from dbscan_cellx import dbscan_cellx


def main(files, save,
         pixel_ratio, size_x, size_y, edge_mode, angel_paramter, save_paramter, keep_uncorrected):
    """Read the Real Python article feed"""

    dbscan_cellx.main(files, save,
                      pixel_ratio, size_x, size_y, edge_mode, angel_paramter, save_paramter, keep_uncorrected)
    
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description='')
    parser.add_argument('-f', '--files', help='Add path to files.',
                        default=[],
                        nargs='*')
 
    parser.add_argument('-sa', '--save', help='Specify path to save output csv',
                        default='C:/Users/Pascal/Master/Graw/')
    parser.add_argument('-p', '--pixel_ratio', help='Pixel', type=float,
                        default=2.8986)
    parser.add_argument('-x', '--size_x', help='X', type=float,
                        default=938.40)
    parser.add_argument('-y', '--size_y', help='Y', type=float,
                        default=565.80)
    parser.add_argument('-e', '--edge_mode', help='Y', type=int,
                        default=1)
    parser.add_argument('-a', '--angel_paramter', help='Y', type=int,
                        default=140)
    parser.add_argument('-sp', '--save_paramter', help='Y', type=int,
                        default=1)
    parser.add_argument('-ku', '--keep_uncorrected', help='Y', type=int,
                        default=1)

    args = parser.parse_args()
    main(**vars(args))

