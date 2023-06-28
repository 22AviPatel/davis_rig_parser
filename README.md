

# Davis Rig Parser

This module is for preprocessing and parsing brief access task data from the Med Associates gustometer, also known as the "Davis Rig."

## Installation

The `davis_rig_parser` module can be installed using pip. It's hosted on PyPI, so you can install it directly from there.

First, you need to make sure you have Python installed on your machine. `davis_rig_parser` was written in Python 3.7.6, but it should work with many other versions. However, if you encounter errors, you can check your Python version by running the following command in your command prompt:

```bash
python --version
```
If your Python version is causing trouble when running the code, try running it with Python 3.7.6.

After setting up Python, you can install davis_rig_parser using pip. Run the following command in your command prompt:

```bash

pip install davis_rig_parser

```
If you're working in a Jupyter notebook, you can run the same command in a code cell with an exclamation mark at the beginning:

```python

!pip install davis_rig_parser
```
You're now ready to use davis_rig_parser in your projects!

## Usage

```python
import davis_rig_parser


# This just creates a .df file in the same folder as the text folder selected in the first "Choose Directory" pop-up.
# The created .df file will be called '/chosen_directory/27_06_2023_grouped_dframe.df' 
# where '27_06_2023_' is the current date in the form day_month_year.
davis_rig_parser.create_df()

# Returns a pandas dataframe variable & creates a .df file in the folder same as the text folder.
pandas_dataframe = davis_rig_parser.create_df()

# Also returns a pandas dataframe + creates a .df file, but passing these variables avoids having to select
# the directories manually.
pandas_dataframe = davis_rig_parser.create_df(
    dir_name = "/your_path_to_the/Data", 
    detail_name = '/your_path_to_the/Animal_Info') # the supplementary animal info.

# If you don't have supplementary animal info, and don't want to see the gui pop-up every time, pass None into detail_name.
pandas_dataframe = davis_rig_parser.create_df(
    dir_name = "/your_path_to_the/Data", 
    detail_name = None) # pass None here

```

## License

This project is licensed under the terms of the GNU General Public License v3.0.

The GNU General Public License is a free, copyleft license for software and other kinds of works. The GNU General Public License is intended to guarantee your freedom to share and change all versions of a program--to make sure it remains free software for all its users.

For more details, please check the [LICENSE](./LICENSE) file in the repository, or read the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).

## Credits

Published by:
Avi Patel

Authors:
Avi Patel
Dr. Bradly T. Stone

Maintainers:
Avi Patel (avipnea@gmail.com)
Daniel Svedberg (dan.ake.svedberg@gmail.com)

last updated: 06/28/2023
