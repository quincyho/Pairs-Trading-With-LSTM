import pandas as pd
import numpy as np


class DataLoader:
    '''
    Dataloader for creating the train and test sets
    '''
    def __init__(self, dataset_fp, train_size, col_name_list):
        self.df = pd.read_csv(dataset_fp, infer_datetime_format=True, parse_dates=['Date'], index_col=['Date'])
        self.index_split = int(train_size*len(self.df))
        self.train_df = self.df[col_name_list].iloc[:self.index_split,:]
        self.test_df = self.df[col_name_list].iloc[self.index_split:,:]
        self.train_data = self.train_df.values
        self.test_data = self.test_df.values
        self.train_len = len(self.train_data)
        self.test_len = len(self.test_data)
    
    def get_train_data(self, lookback_window, normalize):
        '''
        Get training data for LSTM
        '''
        data_x = []
        data_y = []
        for i in range(self.train_len - lookback_window):
            x, y = self._next_window(i, lookback_window, normalize)
            data_x.append(x)
            data_y.append(y)
            
        return np.array(data_x), np.array(data_y)
    
    def get_test_data(self, lookback_window, normalize):
        '''
        Create x, y test data windows
        Warning: batch method, not generative, make sure you have enough memory to
        load data, otherwise reduce size of the training split.
        '''
        data_windows = []
        for i in range(self.test_len - lookback_window):
            data_windows.append(self.test_data[i:i+lookback_window])

        data_windows = np.array(data_windows).astype(float)
        data_windows = self.normalize_windows(data_windows, single_window=False) if normalize else data_windows

        x = data_windows[:, :-2] #-2 instead of -1 for 2 days ahead instead of 1 day ahead
        y = data_windows[:, -1, [0]]
        
        return x,y
    
    def _next_window(self, i, lookback_window, normalize):
        '''
        Generates the next data window
        '''
        
        window = self.train_data[i:i+lookback_window]
        window = self.normalize_windows(window, single_window=True)[0] if normalize else window
        x = window[:-2] #-2 instead of -1 for 2 days ahead instead of 1 day ahead
        y = window[-1, [0]]
        
        return x, y
    
    def normalize_windows(self, window_data, single_window=False):
        '''
        Normalize window with a base value of zero
        '''
        normalized_data = []
        window_data = [window_data] if single_window else window_data
        for window in window_data:
            normalized_window = []
            for col_i in range(window.shape[1]):
                #normalized_col = [((float(p) / float(window[0, col_i])) - 1) for p in window[:, col_i]]
                normalized_col = []
                for p in window[:, col_i]:
                    if float(window[0, col_i]) != 0:
                        normalized_col.append((float(p) /float(window[0, col_i])) - 1) 
                    else:
                        normalized_col.append(0)
                normalized_window.append(normalized_col)
            normalized_window = np.array(normalized_window).T # reshape and transpose array back into original multidimensional format
            normalized_data.append(normalized_window)
        return np.array(normalized_data)