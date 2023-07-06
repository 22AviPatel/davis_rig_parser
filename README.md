

# Davis Rig Parser

This module is for preprocessing and parsing brief access task data from the Med Associates gustometer, also known as the "Davis Rig." It ajusts the raw inputs for  some artifacts created by the Davis Rig, including false licks (see Changing Parameters). 

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
You're now ready to use davis_rig_parser to create dataframes!

## Creating The Dataframe

### Setting Up the Text Files

Make sure you have a folder where the only .txt files are the Med Associates gustometer standardized output for the Davis Rig, you should put all .txt files you want to be turned into a dataframe in the same folder for ease. If you have a .txt file with supplemental animal info, put those in a separate folder. You should have two different folders. They don't have to be stored in adjacent folders, just different folders.

### Running the code

You can create the dataframe as a variable in your code and/or save it as a .df file. The first 2 examples will save a .df file in the same directory chosen (chosen in the pop up or passed as dir_name). The title of the .df file will be '/chosen_directory/27_06_2023_grouped_dframe.df' where 27_06_2023 is the current date in day_month_year format. 
```python
import davis_rig_parser

#Example 1
#just save a .df file
davis_rig_parser.create_df()

#Example 2
#save as a .df file and as a variable called "pandas_df"
pandas_df = davis_rig_parser.create_df()

#Example 3
#only save as variable called "pandas_df", no .df file will be created
pandas_df = davis_rig_parser.create_df(save_df=False)
```

All of the above examples will use pop up menus to choose the directory. If you don't want to click through them everytime, you can pass the directories to both folders (detailed in the Setting Up the Text Files section) in the create_df() function. 

```python
import davis_rig_parser 

#Example 4
#passing your directories as strings avoids having to select the directories manually.
pandas_dataframe = davis_rig_parser.create_df(
    dir_name = "/your_path_to_the/Data", 
    info_name = '/your_path_to_the/Animal_Info') # the supplementary animal info.


#Example 5
# If you don't have supplementary animal info, and don't want to see the pop-up every time, pass None into info_name.
pandas_dataframe = davis_rig_parser.create_df(
    dir_name = "/your_path_to_the/Data", 
    info_name = None) # pass None here
```
### Changing Parameters

The davis_rig_parser does a few things to the data to account for the possible artifacts created by the Davis Rig. Changing these parameters is optional.

#### Bout Size

If you would like to change the bout size you are using change the bout_pause parameter. It is 300 by default. 

```python
import davis_rig_parser

davis_rig_parser.create_df(bout_pause=300)
```
#### Minimum Latency

The Davis Rig will occasionally record false licks when the shutter opens. If the latency of the recorded 'first lick' is less than min_ILI, this 'first lick' is considered shutter openning rather than a true lick. The 1st, 2nd, 3rd...etc licks are summed until the latency is greater than 100ms by default. The number of summed ILIs is deleted from the Licks column in the .txt file. 
```python
import davis_rig_parser

davis_rig_parser.create_df(min_latency=100)
```
Possible false licks created by the shutter closing are not accounted for. 
#### Minimum Possible ILI

The parser will delete all interlick intervals (ILIs) under the min_ILI threshold. These small ILIs are not possible for a rat tounge to move faster than ~75ms. Their source is unknown for certain, but they might be created by the animals bumping into the spout. It is 75 by default. The number of deleted ILIs is deleted from the Licks column in the .txt file. 
```python
import davis_rig_parser

davis_rig_parser.create_df(min_ILI=75)
```
## License

This project is licensed under the terms of the GNU General Public License v3.0.

The GNU General Public License is a free, copyleft license for software and other kinds of works. The GNU General Public License is intended to guarantee your freedom to share and change all versions of a program--to make sure it remains free software for all its users.

For more details, please check the [LICENSE](./LICENSE) file in the repository, or read the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).

## Credits

Published by:
Avi Patel

Authors:
**Avi Patel**, 
**Dr. Bradly T. Stone**

Maintainers:
Avi Patel (avipnea@gmail.com),
Daniel Svedberg (dan.ake.svedberg@gmail.com)

Contributors:
Kathleen Maigler - Test Data

last updated: 06/28/2023
