from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import os, uuid, math, random
import re
from flask import Flask, flash, request, redirect, url_for, session, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from flask import Flask
import model
import connect
basedir=connect.basedir
UPLOAD_FOLDER = basedir + '/static/pdf'
ALLOWED_EXTENSIONS = set(['pdf'])
threshold = 100000
db=connect.db
app=connect.app
IP=connect.IP

# ==============================================================================================
# Tool class include some usual methods
# ==============================================================================================
class Tool:
    commentFlag = 0
    articleFlag = 0

    @staticmethod
    def find(subject):
        if (subject.pid == 'None'):
            print(subject.id)
        else:
            subject = model.model.Subject.query.filter_by(id=subject.pid).first()
            Tool.find(subject)

    # ==================================================================================================
    # @param subject object
    # @return subject's full url
    # ==================================================================================================
    @staticmethod
    def subject_url(subject):
        url = ''
        while subject.pid != 'None':
            url = subject.name + '/' + url
            subject = model.Subject.query.filter_by(id=subject.pid).first()
        url = subject.name + '/' + url
        return url[0:-1]

    # ==================================================================================================
    # @param request.path for example, /article/100
    # @return 100
    # ======================================================================================================
    @staticmethod
    def find_path_last_id(path):
        return path[path.rfind('/', 1) + 1:]

    # =====================================================================================================
    # @param some text
    # @return some text without sensitive words
    # ======================================================================================================
    @staticmethod
    def sensitive_words_filter(text):
        f = open(basedir + '/static/sensitive words/1.txt', 'r')
        result = ''
        flag = True
        for line in f:
            if line.strip() in text.split():
                flag = False
                result = text.replace(line.strip(), '**')
                text = result
        f.close()
        if flag:
            return text
        else:
            return result

    @staticmethod
    def check_short_time():
        if session.get('last_time') is None:
            session['last_time'] = str(datetime.now().strftime("%Y-%m-%d %H:%M"))
        else:
            x = (datetime.now() - datetime.strptime(session.get('last_time'), "%Y-%m-%d %H:%M")).seconds
            if x < 10:
                return "pivot"
            else:
                session['last_time'] = str(datetime.now().strftime("%Y-%m-%d %H:%M"))

    # =======================================================================================================
    # @param article orm object
    # @return article's metric
    # =======================================================================================================
    @staticmethod
    def calculate_metric(article):
        likes = article.upvote
        dislikes = article.downvote
        visits = article.visit
        comments = model.model.Comment.query.filter_by(article_id=article.id).count()
        # positive feedback
        visits_score = math.log2(visits)
        comments_score = comments * 3
        likes_score = likes * 2
        dislikes_score =  dislikes * 1  # dislike information is also important
        # negative feedback
        publish_time = article.time
        now_time = datetime.now()
        timeLag = int(((now_time - publish_time).total_seconds()) / 3600 / 24)
        time_score = math.exp(- timeLag / 100)
        metric = round((visits_score + comments_score + likes_score + dislikes_score) * time_score,2)
        return metric

    @staticmethod
    def email_display_filter(email):
        pre = email[:email.rfind('@')]
        display = pre[:len(pre) // 2]
        suf = email[email.rfind('@') + 1:]
        for i in range(len(pre[len(pre) // 2:])):
            display += '*'

        return display + suf

    @staticmethod
    def highlight_matched_parts(sentence, search_key_word):
        pattern = re.compile(re.escape(search_key_word), re.IGNORECASE)
        if pattern:
            return pattern.sub('<span style="background-color:yellow">%s</span>' % (search_key_word), sentence)
        else:
            return sentence

# =========================================================================================
# like and dislike
# ========================================================================================
@app.route('/article_upvote/<articleID>')
def article_upvote(articleID):
    # get goal article
    article = model.Article.query.filter_by(id=articleID).first()
    ip = session.get('ip')
    visitor = model.Visitor.query.filter_by(ip=ip).first()
    articlevote = model.ArticleVote.query.filter_by(visitor_id=visitor.id, article_id=articleID).first()

    # didn't vote this article before
    if articlevote is None and Tool.articleFlag != 1:
        articlevote = model.ArticleVote(visitor_id=visitor.id, article_id=articleID)
        article.upvote += 1
        article.metric = Tool.calculate_metric(article)
        db.session.add(articlevote)
        db.session.add(article)
    elif articlevote is not None and article.upvote != 0:
        article.upvote -= 1
        db.session.delete(articlevote)
    return jsonify({'upvote': article.upvote})


@app.route('/article_downvote/<articleID>')
def article_downvote(articleID):
    # get goal article
    article = model.Article.query.filter_by(id=articleID).first()
    ip = session.get('ip')
    visitor = model.Visitor.query.filter_by(ip=ip).first()
    articlevote = model.ArticleVote.query.filter_by(visitor_id=visitor.id, article_id=articleID).first()
    # didn't vote this article before
    if articlevote is None:
        articlevote = model.ArticleVote(visitor_id=visitor.id, article_id=articleID)
        article.downvote += 1
        article.metric = Tool.calculate_metric(article)
        db.session.add(articlevote)
        db.session.add(article)
        Tool.articleFlag = 1
    elif articlevote is not None and article.downvote != 0:
        article.downvote -= 1
        db.session.delete(articlevote)
        Tool.articleFlag = -1
    return jsonify({'downvote': article.downvote})


@app.route('/comment_upvote/<commentID>')
def comment_upvote(commentID):
    # get goal comment
    comment = model.Comment.query.filter_by(id=commentID).first()
    ip = session.get('ip')
    visitor = model.Visitor.query.filter_by(ip=ip).first()
    commentvote = model.CommentVote.query.filter_by(visitor_id=visitor.id, comment_id=commentID).first()
    # didn't vote this article before
    if commentvote is None and Tool.commentFlag != 1:
        commentvote = model.CommentVote(visitor_id=visitor.id, comment_id=commentID)
        comment.upvote += 1
        db.session.add(commentvote)
        db.session.add(comment)
    elif commentvote is not None and comment.upvote != 0:
        comment.upvote -= 1
        db.session.delete(commentvote)
    return jsonify({'upvote': comment.upvote})


@app.route('/comment_downvote/<commentID>')
def comment_downvote(commentID):
    # get goal comment
    comment = model.Comment.query.filter_by(id=commentID).first()
    ip = session.get('ip')
    visitor = model.Visitor.query.filter_by(ip=ip).first()

    commentvote = model.CommentVote.query.filter_by(visitor_id=visitor.id, comment_id=commentID).first()
    # didn't vote this article before
    if commentvote is None:
        commentvote = model.CommentVote(visitor_id=visitor.id, comment_id=commentID)
        comment.downvote += 1
        db.session.add(commentvote)
        db.session.add(comment)
        Tool.commentFlag = 1
    elif commentvote is not None and comment.downvote != 0:
        comment.downvote -= 1
        db.session.delete(commentvote)
        Tool.commentFlag = -1
    return jsonify({'downvote': comment.downvote})


# =========================================================================================
# check if a email is banned
# ========================================================================================
@app.route('/check/<mail>')
def check_mail(mail):
    author = model.Author.query.filter_by(mail=mail).first()
    if not author:
        return jsonify('ok')
    return jsonify(author.is_banned)


# ==================================================================================================
# subject
# ==================================================================================================
@app.route('/subject/<subjectID>')
def get_subject(subjectID):
    subject = model.Subject.query.filter_by(id=subjectID).first()
    url = Tool.subject_url(subject)
    page = request.args.get('page', 1, type=int)  # Set the default page to page 1
    articles = model.Article.query.filter_by(subject_id=subject.id, status=1).order_by(model.Article.time.desc()).paginate(
        page=page, per_page=20)

    # ==================================================
    # hot article
    # ==================================================
    hot_article = []
    total = 0
    a = db.session.query(model.Article).filter(
        model.Article.subject_id == subject.id,
        model.Article.metric > threshold
    ).all()
    for x in a:
        hot_article.append(x)


    if not subject.pid  == "None" :
        return render_template('subject.html', url=url, subject_id=subject.id,lasturl="/subject/"+str(subject.pid) ,articles=articles, hot_article=hot_article, Tool=Tool)
    else :
        return render_template('subject.html', url=url, subject_id=subject.id,lasturl="/" ,articles=articles, hot_article=hot_article, Tool=Tool)

# ============================================================================================
# before request
# ============================================================================================
@app.before_request
def before_request():
    ip = IP
    session['ip'] = ip
    visitor = model.Visitor.query.filter_by(ip=ip).first()
    if visitor is None:
        visitor = model.Visitor(ip=ip)
        db.session.add(visitor)
    else:
        # banned ip, can not visit
        if model.Visitor.query.filter_by(ip=ip).first().is_banned:
            print('you have beenn banned')
            return render_template('error.html', message='you have beenn banned')

        # ======================================================================================
        # from now on, ip is valid
        # ======================================================================================
        # about visit of a article
        if request.path.startswith('/article'):
            article_id = Tool.find_path_last_id(request.path)
            visitor = model.Visitor.query.filter_by(ip=ip).first()
            visitvote = model.VisitVote.query.filter_by(visitor_id=visitor.id, article_id=article_id).first()
            # first visit to this article
            if visitvote is None:
                article = model.Article.query.filter_by(id=article_id).first()
                article.visit += 1
                article.metric = Tool.calculate_metric(article)
                visitvote = model.VisitVote(visitor_id=visitor.id, article_id=article_id)
                db.session.add(visitvote)
                db.session.add(article)


# ============================================================================================#
#                                         index                                               #
# ============================================================================================#
@app.route('/')
def index():
    return render_template('io.html')


# ============================================================================================#
# used to out new index after new a subcategory.
# ============================================================================================#
@app.route('/newindex')
def create_index():
    out = open('templates/io.html', 'w', encoding='UTF-8', newline='')

    def find_subjects(subject, count):
        if count == 0:
            out.write('<a href="subject/' + str(subject.id) + '">' + subject.name + '</a><br>\n')
        else:
            for i in range(count):
                out.write('&emsp;\n')
            out.write('<a href="subject/' + str(subject.id) + '">' + subject.name + '</a><br>\n')
        for subject in model.Subject.query.filter_by(pid=subject.id).all():
            find_subjects(subject, count + 1)

    subjects = model.Subject.query.filter_by(pid='None').all()
    out.write('{% extends "template.html" %}' + '\n')
    out.write('{% block content %}' + '\n')
    for subject in subjects:
        find_subjects(subject, 0)
        print('\n')

    out.write('{%  endblock  %}' + '\n')
    out.flush()
    out.close()
    return render_template('io.html')


# ================================================================================
# Edit and add subject
# ================================================================================
@app.route('/edit_subcategory', methods=['GET', 'POST'])
def add_sub_category():
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        subject_name = request.form['subject_name']

        duplicate1 = model.Subject.query.filter_by(name=subject_name).first()
        duplicate2 = 'pivot'

        f = open('static/possible subject/subjects.txt', 'r')
        for line in f:
            if line.strip() == subject_name:
                duplicate2 = None
        f.close()

        if duplicate1 or duplicate2 is None:
            info = 'duplicate subject name!'
            return render_template('add_subcategory.html', info=info, subject_id=subject_id)
        else:
            subject = model.Subject(name=subject_name, pid=subject_id)
            if subject_id is None:
                subject = model.Subject(name=subject_name)
            db.session.add(subject)
            db.session.flush()
            create_index()
        return redirect('/')
    else:
        subject_id = request.args.get('subject_id')
        if request.args.get('add_father') == 'father':
            subject_id = str(None)
        return render_template('add_subcategory.html', subject_id=subject_id)


# ============================================================================================
# edit page
# ============================================================================================
@app.route('/edit', methods=['GET', 'POST'])
def post_article():
    if request.method == 'POST':
        email = request.form['email']
        # means that author isn't in database now
        if not model.Author.query.filter_by(mail=email).first():
            author = model.Author(mail=email, is_banned=False)
            db.session.add(author)

        # pdf only
        # ----------------------------------------------------------------
        message = 'only pdf file is allowed'
        file = request.files['file']
        filename = str(file.filename)[str(file.filename).rfind('.', 0):]
        if filename != '.pdf':
            return render_template('error.html', message=message)
        # ----------------------------------------------------------------

        # ----------------------------------------------------------------
        # prevent posting repeatedlly in a short period of time
        # ----------------------------------------------------------------
        if Tool.check_short_time() == 'pivot':
            email = request.form['email']
            subject_id = request.form['subject_id']
            title = request.form['title']
            abstract = request.form['abstract']
            highlight = request.form['highlight']
            message = 'You can\'t post articles repeatedlly!'
            return render_template('error.html', message=message)
        else:
            author_id = model.Author.query.filter_by(mail=email).first().id
            subject_id = request.form['subject_id']
            title = request.form['title']
            abstract = request.form['abstract']
            highlight = request.form['highlight']
            time = datetime.now()
            article = model.Article(author_id=author_id, subject_id=subject_id, title=title, abstract=abstract,
                              highlight=highlight, time=time, upvote=0, downvote=0, visit=0)
            db.session.add(article)
            db.session.flush()
            upload_file(article)
            return redirect(url_for('get_article', articleID=article.id))

    else:
        email = request.args.get('email')
        subject_id = request.args.get('subject_id')
        return render_template('post_article.html', email=email, subject_id=subject_id)


# =============================================================================================
# article
# =============================================================================================
@app.route('/article/<articleID>')
def get_article(articleID):
    article = model.Article.query.filter_by(id=articleID).first()
    ip = session.get('ip')

    if not model.Visitor.query.filter_by(ip=ip).first():
        article.visit += 1
        db.session.add(article)

    comments_tup = []
    comments = article.comments
    for n,i in enumerate(comments):
        comments_tup.append((n,i))

    return render_template('article.html', article=article, comments=comments_tup, Tool=Tool)



# ========================================================================
# upload pdf file
# ========================================================================
@app.route('/postPdf', methods=['GET', 'POST'])
def upload_file(article):
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            print('filename:--------------' + file.filename)
            u = str(uuid.uuid1())
            file.filename = u + file.filename
            filename = secure_filename(file.filename)
            article.fpath = filename
            db.session.add(article)
            db.session.flush()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    else:
        return render_template('io.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ===========================================================================
# download pdf file
# ===========================================================================
@app.route("/download/<filename>/<id>", methods=['GET'])
def download_file(filename, id):
    article = model.Article.query.get(id)
    article.downloadcount += 1
    db.session.add(article)
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename, as_attachment=True)


# ===========================================================================
# preview pdf file
# ===========================================================================
@app.route("/preview/<filename>", methods=['GET'])
def preview_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename)


# ======================================================================
# post comment
# ======================================================================
@app.route('/post_comment/<articleID>', methods=['POST'])
def post_comment(articleID):
    if Tool.check_short_time() == 'pivot':
        email = request.form['email']
        body = request.form['body']
        message = 'You have posted too many comments repeatedlly, please don\'t spam!'
        return render_template('error.html', message=message)

    email = request.form['email']
    body = request.form['body']
    time = datetime.now()
    # author is not in the database
    if not model.Author.query.filter_by(mail=email).first():
        author = model.Author(mail=email, is_banned=False)
        db.session.add(author)

    author_id = model.Author.query.filter_by(mail=email).first().id
    comment = model.Comment(author_id=author_id, article_id=articleID, body=body, upvote=0, downvote=0, time=time)
    db.session.add(comment)
    article = model.Article.query.filter_by(id=articleID).first()
    article.metric = Tool.calculate_metric(article)
    return redirect(url_for('get_article', articleID=articleID))


# ===============================================================================
# donation
# ===============================================================================
@app.route('/donation')
def donaton():
    return render_template('donation.html')


@app.route('/login', methods=['POST', 'GET'])
def login_verfaication():
    # admins login verification function
    # fetch the email and password from the html login form
    email = request.form['email']
    password = request.form['pass']
    # check if it's exists in the database.
    validate = db.session.query(model.Admin).filter_by(email=email, password=password).first()

    # allow access
    if validate:
        session['logged_in'] = True
        return redirect('/admin')
    else:
        # handle error
        error = 'invalid username or password!'
        return render_template('login.html', error=error)


@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        articles = model.Article.query.all()
        comments = model.Comment.query.all()
        return render_template('admin.html', articles=articles, comments=comments)


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect('/')


@app.route('/deletec/<int:id>')
def delete_comment(id):
    # delete the comment and its relating records from the database.
    comment = model.Comment.query.filter_by(id=id).first()
    comment_vote = model.CommentVote.query.filter_by(comment_id=id).first()

    try:
        # delete the comment
        if comment:
            db.session.delete(comment)
            db.session.commit()
        # delete its vote counter
        if comment_vote:
            db.session.delete(comment_vote)
            db.session.commit()
        return redirect('/admin')
    except:
        return 'Error deleting comment!.'


@app.route('/deletea/<int:id>')
def delete_article(id):
    # to delete an article, we have to consider deleting all its relating values
    # from the database. so for each article first select the article, then all its related records.
    article = model.Article.query.filter_by(id=id).first()
    visit_vote = model.VisitVote.query.filter_by(article_id=id).first()
    article_vote = model.ArticleVote.query.filter_by(article_id=id).first()
    article_comment = model.Comment.query.filter_by(article_id=id).all()

    # if the article has comments, delete them also
    for comment in article_comment:
        delete_comment(comment.id)

    try:
        # delete everything related to the article.
        if article:
            db.session.delete(article)
            db.session.delete(visit_vote)
            db.session.delete(article_vote)
            db.session.commit()

        return redirect('/admin')
    except:
        return 'Error deleting article!.'


@app.route('/article_is_hidden/<int:id>')
def article_is_hidden(id):
    # select the article by its id number
    article = model.Article.query.filter_by(id=id).first()
    # if there is an article with the given id number...
    if article:
        try:
            # if the article status is available switch it into hidden..
            if article.status == 1:
                article.status = 0
                db.session.add(article)
                db.session.commit()
            # if it's hidden switch it into available
            elif article.status == 0:
                article.status = 1
                db.session.add(article)
                db.session.commit()
            return redirect('/admin')
        except:
            return 'Error hiding the article!'


# ===========================================================================
# search function
# ===========================================================================
@app.route('/search')
def search():
    articles = None
    comments = None
    message = None

    content = request.args.get('content')

    matched_articles = db.session.query(model.Article).order_by(model.Article.metric.desc()).filter(or_(model.Article.title.contains(content), model.Article.highlight.contains(content), model.Article.abstract.contains(content))).all()
    matched_comments = db.session.query(model.Comment).filter(model.Comment.body.contains(content))

    return render_template('search.html', articles=matched_articles, comments=matched_comments, Tool=Tool, message=message,kwd=content)


@app.route('/error/<message>')
def error(message):
    return render_template('error.html', message=message)


@app.route('/author/<author_id>')
def author(author_id):
    author = model.Author.query.filter_by(id=author_id).first()
    articles = model.Article.query.order_by(model.Article.time.desc()).filter_by(author_id=author_id).all()
    comments = model.Comment.query.order_by(model.Comment.time.desc()).filter_by(author_id=author_id).all()
    return render_template('author.html', articles=articles, comments=comments, Tool=Tool, author=author)


if __name__ == '__main__':
    app.run(debug=True)
