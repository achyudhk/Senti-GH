from lib.data import download
from lib.util import db


def init_user_data(user_data, user_login):
    user_data[user_login] = dict()
    user_data[user_login]['issues'] = list()
    user_data[user_login]['commits'] = list()
    user_data[user_login]['pull_requests'] = list()
    user_data[user_login]['issue_comments'] = list()
    user_data[user_login]['commit_comments'] = list()
    user_data[user_login]['review_comments'] = list()


def by_user(full_repo_name, num_pages=1):
    user_data = dict()
    repo_data = dict()
    repo_data['issues'] = download.issues(full_repo_name, num_pages)
    repo_data['commits'] = download.commits(full_repo_name, num_pages)
    repo_data['pull_requests'] = download.pull_requests(full_repo_name, num_pages)
    repo_data['issue_comments'] = download.issue_comments(full_repo_name, num_pages)
    repo_data['commit_comments'] = download.commit_comments(full_repo_name, num_pages)
    repo_data['review_comments'] = download.review_comments(full_repo_name, num_pages)
    # Save repo data
    db.insert_repo(repo_data, 'data/repo/%s.json' % full_repo_name)
    # Collate user data
    for issue in repo_data['issues']:
        if not isinstance(issue, str) and 'pull_request' not in issue and issue['user'] is not None:
            if user_data.get(issue['user']['login'], None) is None:
                init_user_data(user_data, issue['user']['login'])
            text_obj = dict()
            text_obj['url'] = issue['url']
            text_obj['title'] = issue['title']
            text_obj['body'] = issue['body']
            text_obj['reactions'] = issue['reactions']
            text_obj['author_association'] = issue['author_association']
            user_data[issue['user']['login']]['issues'].append(text_obj)

    for commit in repo_data['commits']:
        if not isinstance(commit, str) and commit['author'] is not None and 'login' in commit['author']:
            if user_data.get(commit['author']['login'], None) is None:
                init_user_data(user_data, commit['author']['login'])
            text_obj = dict()
            text_obj['url'] = commit['url']
            text_obj['message'] = commit['commit']['message']
            user_data[commit['author']['login']]['commits'].append(text_obj)

    for pull_request in repo_data['pull_requests']:
        if not isinstance(pull_request, str) and pull_request['user'] is not None:
            if user_data.get(pull_request['user']['login'], None) is None:
                init_user_data(user_data, pull_request['user']['login'])
            text_obj = dict()
            text_obj['url'] = pull_request['url']
            text_obj['title'] = pull_request['title']
            text_obj['body'] = pull_request['body']
            text_obj['author_association'] = pull_request['author_association']
            user_data[pull_request['user']['login']]['pull_requests'].append(text_obj)

    for issue_comment in repo_data['issue_comments']:
        if not isinstance(issue_comment, str) and issue_comment['user'] is not None:
            if user_data.get(issue_comment['user']['login'], None) is None:
                init_user_data(user_data, issue_comment['user']['login'])
            text_obj = dict()
            text_obj['url'] = issue_comment['url']
            text_obj['body'] = issue_comment['body']
            text_obj['reactions'] = issue_comment['reactions']
            text_obj['author_association'] = issue_comment['author_association']
            user_data[issue_comment['user']['login']]['issue_comments'].append(text_obj)

    for commit_comment in repo_data['commit_comments']:
        if not isinstance(commit_comment, str) and commit_comment['user'] is not None:
            if user_data.get(commit_comment['user']['login'], None) is None:
                init_user_data(user_data, commit_comment['user']['login'])
            text_obj = dict()
            text_obj['url'] = commit_comment['url']
            text_obj['body'] = commit_comment['body']
            text_obj['reactions'] = commit_comment['reactions']
            text_obj['author_association'] = commit_comment['author_association']
            user_data[commit_comment['user']['login']]['commit_comments'].append(text_obj)

    for review_comment in repo_data['review_comments']:
        if not isinstance(review_comment, str) and review_comment['user'] is not None:
            if user_data.get(review_comment['user']['login'], None) is None:
                init_user_data(user_data, review_comment['user']['login'])
            text_obj = dict()
            text_obj['url'] = review_comment['url']
            text_obj['body'] = review_comment['body']
            text_obj['reactions'] = review_comment['reactions']
            text_obj['author_association'] = review_comment['author_association']
            user_data[review_comment['user']['login']]['review_comments'].append(text_obj)

    # Save user data
    db.insert_repo(user_data, 'data/user/%s.json' % full_repo_name)
