# By Kenneth Burchfiel; released under the MIT license

def pivot_with_subtotals(df, values, index, aggfunc, levels, include_margins = True, margins_name = 'All'): 
 
    '''This function expands on Pandas' pivot_table() function by adding subtotal and grand total columns to the core pivot table. 
    'levels' refers to the number of levels to add into the pivot table. 
    The order of the elements in the 'index' list is important, since each set of subtotal rows will be created by deleting the rightmost element of index.
    For example, suppose that 'index' equals ['Enrolled', 'Time', 'School', 'Grade'], and 'levels' equals 3. This means that the first pivot table will use 'Enrolled', 'Time', 'School', and 'Grade' as its index values; the second pivot table will use 'Enrolled', 'Time', and 'School' (thus grouping the values by grade); and the third table will use 'Enrolled' and 'Time' (thus grouping by school and grade and allowing totals to be calculated for all enrolled and non-enrolled students). The function concatenates each of these tables together, producing one unified pivot table.'''

    import pandas as pd
    modified_index = index.copy() # modified_index will store the index values used in each iteration of the pivot_table function below.  
    pivot_combined = pd.DataFrame() # This empty DataFrame will be populated with output from the pivot table.
    for i in range(levels): # The higher the levels value, the more subtotal levels will be added into the pivot table.
        pivot_individual = pd.pivot_table(data = df, values=values, index=modified_index, aggfunc=aggfunc, margins = ((i == levels-1) & (include_margins == True)), margins_name = margins_name) # See https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.pivot_table.html

        # If include_margins is set to true and i == levels-1 (e.g. when i is at the end of the for loop), a grand total will also be calculated for the pivot table. The name of this total column is set by the margins_name argument.


        pivot_individual.reset_index(inplace=True) # Resetting the index makes it easier to concatenate different pivot tables on top of each other.
        pivot_combined = pd.concat([pivot_combined,pivot_individual])
        del(modified_index[-1]) # Deletes the final element in modified_index, allowing the next run of pivot_table to create a subtotal row. 
    pivot_combined.columns = pivot_combined.columns.to_flat_index() # pivot_table() may output its results as a multindex. For the purposes of this program, I prefered to work with simple indices, so I used to_flat_index() to convert the multindex-formatted columns to a flat index.
    for column in pivot_combined.columns: # When columns are converted from a multindex to a flat index, the result is stored as a tuple. The following lines of code convert each tuple to a string. For instance, the code will convert the tuple ('count', 'Score') to count_Score.
        #print(type(column))
        if isinstance(column, tuple) == True:
            if len(column[1]) > 0:
                pivot_combined.rename(columns={column:column[0]+'_'+column[1]},inplace=True) # [0] and [1] represent the two elements of the tuple
            else: # Some tuples are in the format ('Column_name',''). In this case, there's no need to add an underscore after the first tuple element, so the following line of code simply replaces the tuple with its first element.
                pivot_combined.rename(columns={column:column[0]},inplace=True)
    # Currently, the combined DataFrame has NaN values in cells within columns that were not included in the subtotal/total rows. The following for loop changes these cells to 'Total'. The for loop only covers colunms included in index_i in order not to alter values columns.
    for i in range(len(index)):
        print(pivot_combined.columns[i])
        pivot_combined.fillna(value={pivot_combined.columns[i]:'Total'},axis=0,inplace=True) # See https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.fillna.html . Axis=0 may not be necessary.
    pivot_combined.reset_index(drop=True,inplace=True)
    return pivot_combined
