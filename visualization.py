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
plt.rcParams['font.sans-serif'] = ['Taipei Sans TC Beta'] # to plot Chinese words properly


class PlotWA():
    """
    This is a class to plot historical water quality by inputing 
    siteid (井號) and std_name (法規名稱). The outputs are the figures 
    of individual analyte with the marked color of passing standard
    (法規) or not.
    The visualization use the data in 
    database_ZAF_wa_merged_20211031.xlsx
    and stds_and_cols.xlsx.
    """

    def __init__(self, 
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
        self.std_df = pd.read_excel(excel_dir, usecols=excel_cols)
        self.output_dir = output_dir
        self.std_names = excel_cols[2:]

    def plot(self, siteid, std_name, savefig=False):
        """
        siteid (井號) and std_name (法規名稱) need to be strings.
        Set savefig to True when you wish to output the figures, which
        is in png format (200 dpi).
        """
        if siteid in self.wa_df['井號'] and std_name in self.std_names:
            # collect the analytes having value in the standard (std_name) and '日期'
            cols = np.hstack([self.std_df.loc[~self.std_df[std_name].isna(), '項目'], '日期'])
            # select the data points of that siteid
            X = self.wa_df[self.wa_df['井號'] == siteid]
            # pick up the site name
            site_name = X['井名'][0]
            # select the analytes both have values in the water quality dataset
            # and in the standard.
            X = X.loc[:, X.columns.isin(cols)]
            X = X.loc[:, X.any(axis=0)].copy()

            for analyte in X.columns[:3]:
                unit = self.std_df.loc[self.std_df['項目'] == analyte, '單位'].values[0]
                std_value = self.std_df.loc[self.std_df['項目'] == analyte, std_name].values[0]
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
                plt.show()
                # output figure when savefig is True
                if savefig:
                    plt.savefig('{}{}_{}_{}.png'.format(self.output_dir, siteid, std_name, analyte))
        elif siteid in self.wa_df['井號']:
            print('Please input the std_name (法規名稱) in the list: {}'.format(self.std_names))
        elif std_name in self.std_names:
            print('Please check the siteid (井號) again.')
        else:
            print('Both the siteid (井號) and std_name (法規名稱) are incorrect.')

# test
if __name__ == '__main__':
    plot = PlotWA()
    plot.plot(siteid=4413, std_name='飲用水水源水質標準第五條', savefig=True)