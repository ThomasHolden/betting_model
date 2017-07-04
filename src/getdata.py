import pandas as pd
import scipy.stats
import numpy as np
import datetime

pd.set_option('display.width', 1000)
pd.set_option('max.columns', 100)


class HistoricGames(object):
    def __init__(self, league, season, bookmaker='BbAv'):
        """
        :param league: The league for which historical games should be retrived
        per football-data.co.uk standards. 'E0' for the English Premier League,
        'D1' for the German Bundesliga etc.
        :param season: A four digit integer or a list of four digit integers
        corresponding to the final year of the season of interest.
        If the season finishes in 2017, season should be 2017.
        """
        self.league = league
        self.season = season
        self.bookmaker = bookmaker

    def get_data(self):
        """
        :return: A pandas DataFrame with historic results for the league and
        season along with outcome probabilities for the chosen bookie.
        """
        data = pd.DataFrame()
        if type(self.season) == int:
            seasons = [self.season]
        else:
            seasons = self.season

        for s in seasons:
            base_url = "http://www.football-data.co.uk/mmz4281/"
            url = base_url + str(s - 1)[-2:] + str(s)[-2:] + '/' + self.league + '.csv'
            tmp = pd.read_csv(url)
            data = data.append(tmp)

        pb_rate = [1 / (1 / h + 1 / d + 1 / a) for h, d, a in
                   zip(data[self.bookmaker + 'H'], data[self.bookmaker + 'D'], data[self.bookmaker + 'A'])]

        pb_rateoverunder = [1 / (1 / o + 1 / u) for o, u in
                            zip(data['BbAv>2.5'], data['BbAv<2.5'])]

        data[self.bookmaker + 'H_prob'] = 1 / data[self.bookmaker + 'H'] * pb_rate
        data[self.bookmaker + 'D_prob'] = 1 / data[self.bookmaker + 'D'] * pb_rate
        data[self.bookmaker + 'A_prob'] = 1 / data[self.bookmaker + 'A'] * pb_rate
        data['OverProb'] = 1 / data['BbAv>2.5'] * pb_rateoverunder
        data['UnderProb'] = 1 / data['BbAv<2.5'] * pb_rateoverunder
        data[self.bookmaker + '_pbrate'] = pb_rate

        return data


def mu_from_prob(p):
    mu_vec = np.linspace(0, 10, 1000)
    probs_from_vec = scipy.stats.poisson.cdf(2, mu_vec)
    diff_vec = abs(probs_from_vec - p)
    minind = list(diff_vec).index(min(diff_vec))
    mu_val = mu_vec[minind]
    return mu_val


bookmaker = 'BbAv'

histgames = HistoricGames('E0', 2017, bookmaker)
data = histgames.get_data()

data['mu_val'] = [mu_from_prob(p) for p in data['UnderProb']]
data[bookmaker + '_h_mu'] = data[bookmaker + 'H_prob'] / (data[bookmaker + 'H_prob'] + data[bookmaker + 'A_prob']) * data['mu_val']
data[bookmaker + '_a_mu'] = data['mu_val'] - data[bookmaker + '_h_mu']

print(data)
