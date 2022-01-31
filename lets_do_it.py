import streamlit as st
import pandas as pd
from itertools import groupby
from datetime import datetime


st.set_page_config(layout='wide')


def parse_blame(chunk):
    branch = chunk[0].split()[0]
    line_start = chunk[0].split()[1]
    author = chunk[1][7:]
    author_mail = chunk[2][13:-1]
    author_time_int = chunk[3][12:]
    author_time = datetime.fromtimestamp(int(author_time_int))
    filename = chunk[-2][9:]
    comment_text = chunk[-1]
    print(comment_text.find("TODO"))
    comment = comment_text[comment_text.find("TODO"):]
    return author, author_mail, author_time, filename, comment, branch, line_start


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


def make_path_clickable(branch, path, line_start, prefix='https://github.com/pytorch/pytorch'):
    return f'<a target="_blank" href="{prefix}/blob/{branch}/{path}#L{line_start}">{path}</a>'

st.title("Let's Do it")
blame_txt = st.sidebar.file_uploader("git blame results")

if blame_txt:
    content = blame_txt.readlines()
    print(content)
    content = [line.decode("utf-8").strip() for line in content]
    chunks = (list(g) for k, g in groupby(content, key=lambda x: x != '--blame-end--') if k)
    data = []

    for chunk in chunks:
        data.append(list(parse_blame(chunk)))
        
    df = pd.DataFrame(data, columns=['author', 'author_mail', 'author_time', 'filename', 'comment', "branch", "line_start"])
    df['tags'] = df.comment.map(apply_tags)
    unique_emails = df.author_mail.unique()

    search_option = st.sidebar.selectbox("search option", ['by email', 'by path prefix'])
    if search_option == 'by email':
        author_mail_input = st.sidebar.selectbox("email", [""] + unique_emails.tolist())
        if author_mail_input != '':
            to_show_df = df[df.author_mail == author_mail_input].copy()
            to_show_df['filename'] = df.apply(lambda x: make_path_clickable(x['branch'], x['filename'], x['line_start']), axis=1)
            st.write(to_show_df[['author', 'author_mail', 'author_time', 'filename', 'comment', 'tags']].to_html(escape=False, index=False), unsafe_allow_html=True)
    if search_option == 'by path prefix':
        path_input = st.sidebar.text_input("path_prefix")
        if path_input:
            length = len(path_input)
            to_show_df = df[df.filename.map(lambda x: x[:length] == path_input)]
            st.write(to_show_df[['author', 'author_mail', 'author_time', 'filename', 'comment', 'tags']].to_html(escape=False, index=False), unsafe_allow_html=True)
            