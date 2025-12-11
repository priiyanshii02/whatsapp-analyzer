import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from urlextract import URLExtract


# Sidebar Title
st.sidebar.title("WhatsApp Chat Analyzer")

# File uploader
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8", errors="replace")
    df = preprocessor.preprocess(data)

    # Fetch unique users
    user_list = df['user'].unique().tolist()

    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        # ------------------ TOP STATISTICS ------------------ #
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # ------------------ TIMELINES ------------------ #
        # Monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        if not timeline.empty:
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], color='green')
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.write("No monthly timeline data available.")

        # Daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        if not daily_timeline.empty:
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.write("No daily timeline data available.")

        # ------------------ ACTIVITY MAP ------------------ #
        st.title('Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            if not busy_day.empty:
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values, color='purple')
                plt.xticks(rotation=45)
                st.pyplot(fig)
            else:
                st.write("No data available for busiest day.")

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            if not busy_month.empty:
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color='orange')
                plt.xticks(rotation=45)
                st.pyplot(fig)
            else:
                st.write("No data available for busiest month.")

        # ------------------ WEEKLY ACTIVITY HEATMAP ------------------ #
        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)

        # Define proper AM/PM order
        period_order = [
            '12 AM - 1 AM', '1 AM - 2 AM', '2 AM - 3 AM', '3 AM - 4 AM', '4 AM - 5 AM', '5 AM - 6 AM',
            '6 AM - 7 AM', '7 AM - 8 AM', '8 AM - 9 AM', '9 AM - 10 AM', '10 AM - 11 AM', '11 AM - 12 PM',
            '12 PM - 1 PM', '1 PM - 2 PM', '2 PM - 3 PM', '3 PM - 4 PM', '4 PM - 5 PM', '5 PM - 6 PM',
            '6 PM - 7 PM', '7 PM - 8 PM', '8 PM - 9 PM', '9 PM - 10 PM', '10 PM - 11 PM', '11 PM - 12 AM'
        ]

        if user_heatmap is not None and not user_heatmap.empty:
            user_heatmap = user_heatmap.reindex(columns=period_order, fill_value=0)
            fig, ax = plt.subplots(figsize=(12,6))
            sns.heatmap(user_heatmap, cmap="YlGnBu", linewidths=0.5, ax=ax)
            plt.yticks(rotation=0)
            st.pyplot(fig)
        else:
            st.write("No activity data available to display the heatmap.")

        # ------------------ BUSIEST USERS ------------------ #
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            col1, col2 = st.columns(2)

            with col1:
                if not x.empty:
                    fig, ax = plt.subplots()
                    ax.bar(x.index, x.values, color='red')
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
                else:
                    st.write("No data available for busy users.")

            with col2:
                st.dataframe(new_df if not new_df.empty else pd.DataFrame())

        # ------------------ WORDCLOUD ------------------ #
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        if df_wc is not None:
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.write("No data available to create wordcloud.")

        # ------------------ MOST COMMON WORDS ------------------ #
        most_common_df = helper.most_common_words(selected_user, df)
        if most_common_df is not None and not most_common_df.empty:
            fig, ax = plt.subplots()
            ax.barh(most_common_df[0], most_common_df[1])
            plt.xticks(rotation=45)
            st.title('Most Common Words')
            st.pyplot(fig)
        else:
            st.write("No common words found.")

        # ------------------ EMOJI ANALYSIS ------------------ #
        emoji_df = helper.emoji_helper(selected_user, df)
        st.title("Emoji Analysis")
        col1, col2 = st.columns(2)

        with col1:
            if emoji_df is not None and not emoji_df.empty:
                st.dataframe(emoji_df)
            else:
                st.write("No emojis found.")

        with col2:
            if emoji_df is not None and not emoji_df.empty:
                fig, ax = plt.subplots()
                ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f%%")
                st.pyplot(fig)
            else:
                st.write("No emojis available for pie chart.")
