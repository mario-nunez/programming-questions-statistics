import logging

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


logger = logging.getLogger(__name__)


class GraphMaker:

    def create_graphs(self, data_parsed_df):

        fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(18,14))
        fig.subplots_adjust(hspace=0.3, wspace=0.5)
        fig.suptitle('Stackoverflow statistics', fontsize=20)

        # Top 5 questions with most views
        highest_views_df = data_parsed_df\
            .sort_values("views", ascending=False).head(5)
        sns\
            .barplot(x="question_id", y="views", data=highest_views_df,
                     orient="v", ax=axes[1,2], order=highest_views_df\
                        .sort_values("views", ascending=False).question_id)\
            .set(title="Top 5 questions with most views",
                 xlabel="Question ID", ylabel="Views")

        # Top 5 questions with most answers
        highest_num_ans_df = data_parsed_df\
            .sort_values("num_answers", ascending=False).head(5)
        sns\
            .barplot(x="question_id", y="num_answers", data=highest_num_ans_df,
                     orient="v", ax=axes[0,1], order=highest_num_ans_df\
                        .sort_values("num_answers", ascending=False).question_id)\
            .set(title="Top 5 questions with most answers",
                 xlabel="Question ID", ylabel="Number of answers")

        # Top 5 questions with most votes
        highest_votes_df = data_parsed_df\
            .sort_values("votes", ascending=False).head(5)
        sns\
            .barplot(x="question_id", y="votes", data=highest_votes_df,
                     orient="v", ax=axes[1,0], order=highest_votes_df\
                        .sort_values("votes", ascending=False).question_id)\
            .set(title="Top 5 questions with most votes",
                 xlabel="Question ID", ylabel="Votes")

        # Number of answers of the top 5 questions with most votes
        sns\
            .barplot(x="question_id", y="num_answers", data=highest_votes_df,
                     orient="v", ax=axes[1,1], order=highest_votes_df\
                        .sort_values("votes", ascending=False).question_id)\
            .set(title="Number of answers of the top 5 questions with most votes",
                 xlabel="Question ID", ylabel="Number of answers")

        # Top 5 questions with the highest response percentage
        data_parsed_df["answers_pct"] = (data_parsed_df.num_answers/data_parsed_df.views)*100
        highest_pct_df = data_parsed_df\
            .sort_values("answers_pct", ascending=False).head(5)
        sns\
            .barplot(x="question_id", y="answers_pct", data=highest_pct_df,
                     orient="v", ax=axes[0,2], order=highest_pct_df\
                        .sort_values("answers_pct", ascending=False).question_id)\
            .set(title="Top 5 questions with the highest response percentage",
                 xlabel="Question ID", ylabel="Response percentage (%)")

        # Top 10 most used tags
        total_tags = []
        data_parsed_df['tags'].apply(lambda x: total_tags.extend(x))
        tags_count = { i:total_tags.count(i) for i in total_tags }
        tags_df = pd.DataFrame(tags_count.items(), columns=['tag', 'count'])\
            .sort_values("count", ascending=False).head(10)
        sns\
            .barplot(x="count", y="tag", data=tags_df,
                     orient="h", ax=axes[0,0], order=tags_df\
                        .sort_values("count", ascending=False).tag)\
            .set(title="Top 10 most used tags",
                 xlabel="Count", ylabel="Tag")

        plt.show()
