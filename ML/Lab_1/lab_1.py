import seaborn as sns
import numpy as np

DATASET_NAME = 'diamonds'
COLUMNS = ['carat', 'depth', 'price']

class Zscore:

    def __init__(self, df):
        self.df = df.copy()
        self.column_names = df.columns.tolist()
        print('--- Dataset initialization ---')
        print(f'Dataset columns: \n{self.column_names}.')
        self.dataset = df.values.astype(float)
        print(f'Dataset len: {len(dataset)}.')
        self.means = np.nanmean(self.dataset, axis=0)
        print('Means calculated.')
        print(self.means)
        self.stds = np.nanstd(self.dataset, axis=0)
        print('Stds calculated.')
        print(self.stds)
        self.zscore = None
        self.aggreg_zscore = None
        self.outliers_mask = None

    def calc_zscore(self):
        self.zscore = (self.dataset - self.means) / self.stds
        return self.zscore
    
    def calc_aggreg_zscore(self):
        if(self.zscore is None):
            self.calc_zscore()
        self.aggreg_zscore = np.nanmean(np.abs(self.zscore), axis=1)
        return self.aggreg_zscore
    
    def get_outliers(self, limit=3, count=5, top_n=10):
        if(self.aggreg_zscore is None):
            self.calc_aggreg_zscore()
        
        self.outliers_mask = self.aggreg_zscore > limit
        if(np.sum(self.outliers_mask) < count):
            print(f'Outliers count is less than required(< {limit}). Using top {top_n}.')
            top_idx = np.argsort(self.aggreg_zscore)[-top_n:]
            self.outliers_mask = np.zeros(len(self.aggreg_zscore), dtype=bool)
            self.outliers_mask[top_idx] = True
        print("--- Outliers ---")
        print(self.df[self.outliers_mask])
        return self.outliers_mask

    def plot_2d(self, column1, column2):
        if self.outliers_mask is None:
            self.get_outliers()

        x_idx = self.column_names.index(column1)
        y_idx = self.column_names.index(column2)

        import matplotlib.pyplot as plt

        plt.figure(figsize=(8,6))
        plt.scatter(self.dataset[:, x_idx][~self.outliers_mask],
                    self.dataset[:, y_idx][~self.outliers_mask],
                    alpha=0.3, s=10, label='inliers')
        plt.scatter(self.dataset[:, x_idx][self.outliers_mask],
                    self.dataset[:, y_idx][self.outliers_mask],
                    color='red', s=20, label='outliers')
        plt.xlabel(column1)
        plt.ylabel(column2)
        plt.title(f'2D Scatter: {column1} vs {column2}')
        plt.legend()
        plt.show()

    def plot_3d(self, column1, column2, column3):
        if self.outliers_mask is None:
            self.get_outliers()

        x_idx = self.column_names.index(column1)
        y_idx = self.column_names.index(column2)
        z_idx = self.column_names.index(column3)

        from mpl_toolkits.mplot3d import Axes3D
        import matplotlib.pyplot as plt

        fig = plt.figure(figsize=(10,8))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(self.dataset[:, x_idx][~self.outliers_mask],
                   self.dataset[:, y_idx][~self.outliers_mask],
                   self.dataset[:, z_idx][~self.outliers_mask],
                   alpha=0.2, s=10, label='inliers')
        ax.scatter(self.dataset[:, x_idx][self.outliers_mask],
                   self.dataset[:, y_idx][self.outliers_mask],
                   self.dataset[:, z_idx][self.outliers_mask],
                   color='red', s=20, label='outliers')
        ax.set_xlabel(column1)
        ax.set_ylabel(column2)
        ax.set_zlabel(column3)
        ax.set_title(f'3D Scatter: {column1}, {column2}, {column3}')
        ax.legend()
        plt.show()

        
dataset = sns.load_dataset(DATASET_NAME)
zscore = Zscore(dataset[COLUMNS])

print('--- Zscore ---')
print(zscore.calc_zscore())

print('Aggregated Zscore')
print(zscore.calc_aggreg_zscore())

zscore.plot_2d(COLUMNS[0], COLUMNS[2])
zscore.plot_2d(COLUMNS[1], COLUMNS[2])

zscore.plot_3d(COLUMNS[0], COLUMNS[1], COLUMNS[2])
