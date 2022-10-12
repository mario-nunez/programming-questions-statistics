import logging

import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)


class GraphMaker:

    def create_graphs(self, data_type, data_parsed_df):

        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(11,9))
        fig.subplots_adjust(hspace=0.3, wspace=0.3)
        fig.suptitle('Stackoverflow visualizations', fontsize=20)

        # Top 5 questions with most views
        data_most_views = data_parsed_df\
            .sort_values("views", ascending=False).head(5)
        ax1 = sns\
            .barplot(x="question_id", y="views", data=data_most_views,
                     orient="v", ax=axes[0,0], order=data_most_views\
                        .sort_values("views", ascending=False).question_id)\
            .set(title="Top 5 questions with most views",
                 xlabel="Question ID", ylabel="Views")


        # Top 5 questions with most answers
        data_most_answers = data_parsed_df\
            .sort_values("num_answers", ascending=False).head(5)
        sns\
            .barplot(x="question_id", y="num_answers", data=data_most_answers,
                     orient="v", ax=axes[0,1], order=data_most_answers\
                        .sort_values("num_answers", ascending=False).question_id)\
            .set(title="Top 5 questions with most answers",
                 xlabel="Question ID", ylabel="Number of answers")

        # Top 5 questions with most votes
        data_most_votes = data_parsed_df\
            .sort_values("votes", ascending=False).head(5)
        sns\
            .barplot(x="question_id", y="votes", data=data_most_votes,
                     orient="v", ax=axes[1,0], order=data_most_votes\
                        .sort_values("votes", ascending=False).question_id)\
            .set(title="Top 5 questions with most votes",
                 xlabel="Question ID", ylabel="Votes")

        # Number of answers of the top 5 questions with most votes
        sns\
            .barplot(x="question_id", y="num_answers", data=data_most_votes,
                     orient="v", ax=axes[1,1], order=data_most_votes\
                        .sort_values("votes", ascending=False).question_id)\
            .set(title="Number of answers of the top 5 questions with most votes",
                 xlabel="Question ID", ylabel="Number of answers")

        fig2, axes = plt.subplots(nrows=2, ncols=2, figsize=(11,9))
        fig2.subplots_adjust(hspace=0.3, wspace=0.3)
        fig2.suptitle('Other visualizations', fontsize=20)
        
        plt.show()