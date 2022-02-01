import streamlit as st
import pandas as pd
from itertools import groupby
from datetime import datetime
import re
from pretty_html_table import build_table



st.set_page_config(layout='wide')
JIRA_REGEX= "[A-Z]{2,}-\d+"


def parse_blame(chunk):
    branch = chunk[0].split()[0]
    line_start = chunk[0].split()[1]
    author = chunk[1][7:]
    author_mail = chunk[2][13:-1]
    author_time_int = chunk[3][12:]
    author_time = datetime.fromtimestamp(int(author_time_int))
    filename = chunk[-2][9:]
    comment_text = chunk[-1]
    comment = comment_text[comment_text.find("TODO"):]
    jira_tickets = re.findall(JIRA_REGEX, comment)
    jira_ticket = jira_tickets[0] if jira_tickets else None
    return author, author_mail, author_time, filename, comment, branch, line_start, jira_ticket


def apply_tags(comment):
    comment = comment.lower()
    tags = []
    uncertainty_words = {"uncertainty": ["?", "maybe", "perhaps", "should we", "probably", "might", "not sure"]}
    hacky_words = {"hacky": ["temporary", "hack", "hacky"]}
    fixme_words = {"fix": ["fixme", "fix", "bug", "incorrect"]}
    dependency_words = {"dependency": ["once", "when", "blocked"]}
    
    for tw in [uncertainty_words, hacky_words, fixme_words, dependency_words]:
        for k, v in tw.items():
            for w in v:
                if w in comment:
                    tags.append(k)
    return tags


def make_table(df):
    return build_table(df, 'blue_light',  font_size='medium', 
        font_family='Century Gothic, sans-serif', 
        text_align='left', 
        width='auto', 
        index=False, 
        escape=False)

def make_path_clickable(branch, path, line_start, prefix='https://github.com/pytorch/pytorch'):
    return f'<a target="_blank" href="{prefix}/blob/{branch}/{path}#L{line_start}">{path}</a>'


col1, col2, col3 = st.columns(3)
with col1:
    st.title("✅ Let's Do it")
with col3:
    st.header("#TODO tracker")
st.sidebar.write("Run **todo_script.sh** to get blame results for a repo")
blame_txt = st.sidebar.file_uploader("Submit the git blame results.txt")


if blame_txt:
    content = blame_txt.readlines()
    content = [line.decode("utf-8").strip() for line in content]
    chunks = (list(g) for k, g in groupby(content, key=lambda x: x != '--blame-end--') if k)
    data = []

    for chunk in chunks:
        data.append(list(parse_blame(chunk)))
        
    df = pd.DataFrame(data, columns=['author', 'author_mail', 'author_time', 'filename', 'comment', "branch", "line_start", "jira_ticket"])
    df['tags'] = df.comment.map(apply_tags)
    df['clickable_filename'] = df.apply(lambda x: make_path_clickable(x['branch'], x['filename'], x['line_start']), axis=1)
    
    unique_emails = df.author_mail.unique()

    search_option = st.sidebar.selectbox("search option", ['by email', 'by path prefix'])
    if search_option == 'by email':
        author_mail_input = st.sidebar.selectbox("email (e.g. rongr@fb.com)", [""] + unique_emails.tolist())
        if author_mail_input != '':
            to_show_df = df[df.author_mail == author_mail_input].copy()
            st.write(make_table(to_show_df[['author', 'author_mail', 'author_time', 'clickable_filename', 'comment', 'tags', 'jira_ticket']]), unsafe_allow_html=True)
            
    if search_option == 'by path prefix':
        path_input = st.sidebar.text_input("path prefix (e.g. caffe2/contrib)")
        if path_input:
            length = len(path_input)
            to_show_df = df[df.filename.map(lambda x: x[:length] == path_input)].copy()
            st.write(make_table(to_show_df[['author', 'author_mail', 'author_time', 'clickable_filename', 'comment', 'tags', 'jira_ticket']]), unsafe_allow_html=True)
            