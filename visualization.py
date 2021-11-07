"""
This module is built for visualizing results.
To plot the figures with Traditional Chinese properly, 
It's recommended to go through install_chinese_font.ipynb first.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use(['seaborn-colorblind', 'seaborn-talk'])
plt.rcParams['figure.dpi'] = 200
plt.rcParams['savefig.dpi'] = 200
plt.rcParams['savefig.bbox'] = 'tight'
plt.rcParams['font.sans-serif'] = ['Taipei Sans TC Beta']

class Waterlvl():
    """
    This a class to select sites that are having water level higher 
    than the chosen criteria. 
    """

    def __init__(
        self,
        ep_dir = 'data/wl_EP_20211107.csv'
    ):
        self.ep_df = pd.read_csv(ep_dir)

    def MarkbyEP(self, df, criteria='安全'):
        """
        This a function to mark sites that are having water level 
        higher than the chosen criteria. 
        The input data should be a pd.DataFrame, which has at least 
        columns of 日期時間, 井號, 水面至井口深度. Any extra columns 
        will be output also after marking.
        The output is a pd.DataFrame consisting the information (taken
        from the most recent data of each site) and the checked result
        of the input sites.
        """
        criterias = {
            'decreasing': {
                '安全': '75',
                '下限': '25',
                '嚴重': '10'
            },
            'increasing': {
                '安全': '85',
                '下限': '35',
                '嚴重': '20'
            } 
        }
        out_df = pd.DataFrame()
        check_list = []
        if criteria in criterias['decreasing'].keys():
            df = df.set_index('日期時間').sort_values('日期時間')
            for siteid in df['井號'].unique():
                X = df[df['井號'] == siteid].copy()
                # take the most recent data as the out put
                out_df = pd.concat([out_df, X.iloc[-1, :]], join='outer', axis=1)
                mask = (self.ep_df['月'] == X['月'].values[-1]) & (self.ep_df['井號'] == str(X['井號'].values[-1]))
                # find the slope of the measurements
                p = np.polyfit(range(len(X)), X['水面至井口深度'], 1)
                # the water level is at a decreasing or flat trend
                if p[0] <= 0:
                    if X['水面至井口深度'].values[-1] > self.ep_df.loc[mask, criterias['decreasing'][criteria]].values[0]:
                        check_list.append(True)
                    else:
                        check_list.append(False)
                # the water level is at a increasing trend
                else:
                    if X['水面至井口深度'].values[-1] > self.ep_df.loc[mask, criterias['increasing'][criteria]].values[0]:
                        check_list.append(True)
                    else:
                        check_list.append(False)
            out_df = out_df.T
            out_df['wl_check'] = check_list
            return out_df
        else:
            print('Please set the criteria in the list of {}'.format(criterias['decreasing'].keys()))        

class Waterquality():
    """
    This is a class to plot and filter the historical water quality by 
    inputing siteid (井號) and std_name (法規名稱). The outputs are (1)
    figures of individual analyte with the marked color of passing
    standard (法規) or not and (2) a pd.DataFrame containing the 
    boolean values (wa_check) as the mark of passing the selected 
    standard. The class use the data in 
    database_ZAF_wa_merged_20211031.xlsx and stds_and_cols.xlsx as 
    the initials.
    """

    def __init__(
        self, 
        wa_dir = 'data/database_ZAF_wa_merged_20211031.xlsx',
        excel_dir = 'data/stds_and_cols.xlsx',
        output_dir = 'results/',
        excel_cols = ['項目', '單位', '飲用水水源水質標準第五條', 
        '飲用水水源水質標準第六條', '地下水污染監測標準第一類', 
        '地下水污染監測標準第二類', '地下水污染管制標準第一類', 
        '地下水污染管制標準第二類', '灌溉用水水質標準', 
        '再生水用於工業用途水質基礎建議值一', 
        '再生水用於工業用途水質基礎建議值二']
    ):
        self.wa_df = pd.read_excel(wa_dir, parse_dates=['日期時間'])
        self.wa_df['日期'] = pd.to_datetime([_.strftime('%Y-%m-%d') for _ in self.wa_df['日期時間']])
        self.wa_df['井號'] = self.wa_df['井號'].astype(str)
        self.std_df = pd.read_excel(excel_dir, usecols=excel_cols)
        self.output_dir = output_dir
        self.std_names = excel_cols[2:]

    def plot(self, siteid, std_name, savefig=False):
        """
        siteid (井號) and std_name (法規名稱) need to be strings.
        Set savefig to True when you wish to output the figures, which
        is in png format (200 dpi).
        """
        if (siteid in self.wa_df['井號']) and (std_name in self.std_names):
            # collect the analytes having value in the standard (std_name) and '日期'
            cols = np.hstack([self.std_df.loc[~self.std_df[std_name].isna(), '項目'], '日期'])
            # select the data points of that siteid
            X = self.wa_df[self.wa_df['井號'] == siteid].reset_index(drop=True)
            # pick up the site name
            site_name = X['井名'][0]
            # select the analytes both have values in the water quality dataset
            # and in the standard.
            X = X.loc[:, X.columns.isin(cols)]
            X = X.loc[:, X.any(axis=0)].copy()
            #with open('results/error.txt', 'w', encoding='utf-8') as f:
            #        print(X.columns, file=f)
            # the last one is '日期'
            for analyte in X.columns[:-1]:
                #with open('results/error.txt', 'a', encoding='utf-8') as f:
                #    print(analyte, file=f)
                unit = self.std_df.loc[self.std_df['項目'] == analyte, '單位'].values[0]
                std_value = self.std_df.loc[self.std_df['項目'] == analyte, std_name].values[0]
                # there are three different scenarios about the standard value
                if analyte == '氫離子濃度指數':
                    lo_lim, up_lim = [float(_) for _ in std_value.split('-')]
                    mask = (X[analyte] >= lo_lim) & (X[analyte] <= up_lim)
                elif analyte == '溶氧量':
                    mask = X[analyte] > std_value
                else:
                    mask = X[analyte] < std_value

                plt.figure(figsize=(7, 5))
                plt.plot_date(X.loc[mask, '日期'], X.loc[mask, analyte], 
                    c='C0', fmt='o', xdate=True, label='符合')
                plt.plot_date(X.loc[~mask, '日期'], X.loc[~mask, analyte], 
                    c='gray', fmt='^', xdate=True, label='未符合')
                plt.xlabel('日期')
                plt.ylabel('{} ({})'.format(analyte, unit))
                plt.legend(title='井名: {}'.format(site_name))
                plt.suptitle('{}: {} {} ({})'.format(std_name, analyte, 
                                                     std_value, unit))
                plt.subplots_adjust(top=.93)
                #plt.show()
                # output figure when savefig is True
                if savefig:
                    plt.savefig('{}{}_{}_{}.png'.format(self.output_dir, siteid, std_name, analyte))
        elif siteid in self.wa_df['井號']:
            print('Please input the std_name (法規名稱) in the list: {}'.format(self.std_names))
        elif std_name in self.std_names:
            print('Please check the siteid (井號) again.')
        else:
            print('Both the siteid (井號) and std_name (法規名稱) are incorrect.')

    def MarkbySTD(self, df, std_name):
        """
        df needs to be a pd.DataFrame containing at least siteid 
        (井號, in string). Any extra columns will be output also after
        marking. std_name (法規名稱) need to be strings which in the list
        of cols_and_std.xlsx. df usually is the output of MarkbyEP.
        The output is like in MarkbyEP, a pd.DataFrame consisting the information 
        and the checked result of the input sites.
        """
        if std_name in self.std_names:
            df['井號'] = df['井號'].astype(str)
            check = True
            check_list=[]
            out_df = pd.DataFrame()
            for siteid in df['井號'].unique():
                # collect the analytes having value in the standard (std_name) and '日期'
                cols = np.hstack([self.std_df.loc[~self.std_df[std_name].isna(), '項目'], '日期'])
                # select the data points of that siteid
                X = self.wa_df[self.wa_df['井號'] == siteid].reset_index(drop=True)
                # There might be site not having measurement at all
                if len(X) > 0:
                    # select the analytes both have values in the water quality dataset
                    # and in the standard.
                    X = X.loc[:, X.columns.isin(cols)]
                    X = X.loc[:, X.any(axis=0)].copy()
                    # the last one is '日期'
                    for analyte in X.columns[:-1]:
                        std_value = self.std_df.loc[self.std_df['項目'] == analyte, std_name].values[0]
                        # there are three different scenarios about the standard value
                        if analyte == '氫離子濃度指數':
                            lo_lim, up_lim = [float(_) for _ in std_value.split('-')]
                            mask = (X[analyte] >= lo_lim) & (X[analyte] <= up_lim)
                        elif analyte == '溶氧量':
                            mask = X[analyte] > std_value
                        else:
                            mask = X[analyte] < std_value
                        # if there more than 3 historical measurements not passing std
                        # in an analyte, this siteid will be marked "no"
                        if ~mask.sum() > 3: 
                            check = False
                else:
                    print('{} has no water quality measurement'.format(siteid))
                    check = False
                check_list.append(check)
                out_df = pd.concat([out_df, df[df['井號'] == siteid]], join='outer', axis=0)
            #out_df = out_df.T
            out_df['wa_check'] = check_list
            return out_df
        else:
            print('Please input the std_name (法規名稱) in the list: {}'.format(self.std_names))
# test
if __name__ == '__main__':
    #plot = PlotWA()
    #plot.plot(siteid=4413, std_name='再生水用於工業用途水質基礎建議值一', savefig=True)
    #merge_df = pd.read_hdf('data/database_ZAF_clean_gps_20211104.hd5', key='wl')
    #mask = (merge_df['日期時間']>='2021-05-01') & (merge_df['日期時間']<'2021-05-15')
    #df = merge_df[mask].copy()
    #df.to_csv('data/test.csv', index=False)
    df = pd.read_csv('data/test.csv')
    select = Waterlvl()
    df = select.MarkbyEP(df=df)
    #print(out_df.shape, len(check_list))
    #with open('results/error.txt', 'w+', encoding='utf-8') as f:
    #    print(out_df, file=f)
    select = Waterquality()
    select.MarkbySTD(df=df, std_name='再生水用於工業用途水質基礎建議值一').to_csv('results/out.csv')