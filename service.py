from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import os, uuid ,math, random
from flask import Flask, flash, request, redirect, url_for, session, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from flask import Flask
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = basedir + '\static\pdf'
ALLOWED_EXTENSIONS = set(['pdf'])
threshold = 100000
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = os.path.join(basedir+'\static\pdf')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir+'\database.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
db = SQLAlchemy(app)
IP = '127.0.0.10'
class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(50), unique=True)
    is_banned = db.Column(db.Boolean, default=False)

    # OneToMany
    articles = db.relationship('Article', backref='author')
    comments = db.relationship('Comment', backref='author')


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    pid = db.Column(db.Integer)

    # OneToMany
    articles = db.relationship('Article', backref='subject')


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    title = db.Column(db.Text)
    abstract = db.Column(db.Text)
    highlight = db.Column(db.Text)
    time = db.Column(db.DateTime)
    visit = db.Column(db.Integer)
    upvote = db.Column(db.Integer)
    downvote = db.Column(db.Integer)
    metric = db.Column(db.Float, default=0)
    fpath = db.Column(db.String)
    status = db.Column(db.Integer, default=1)

    # OneToMany
    comments = db.relationship('Comment', backref='article')

    # def get_mail(self):
    #     # db.session.query(Author).filter(Author.id == articles[0].author_id).first().mail
    #     return db.session.query(Author).filter(Author.id == self.author_id).first().mail


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    body = db.Column(db.Text)
    upvote = db.Column(db.Integer)
    downvote = db.Column(db.Integer)

    time = db.Column(db.DateTime)

    # comment1.article.title


# ------------------------------------------------------#
#              record every visitor's ip               #
# ------------------------------------------------------#
class Visitor(db.Model):
    __tablename__ = 'visitors'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50), unique=True)
    is_banned = db.Column(db.Boolean, default=False)

    # OneToMangy
    article_votes = db.relationship('ArticleVote', backref='visitor')
    comment_votes = db.relationship('CommentVote', backref='visitor')
    visit_votes = db.relationship('VisitVote', backref='visitor')

class ArticleVote(db.Model):
    __tablename__ = 'article_votes'
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'))

    article_id = db.Column(db.Integer)
    #upvote_state = db.Column(db.Integer)


class CommentVote(db.Model):
    __tablename__ = 'comment_votes'
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'))
    comment_id = db.Column(db.Integer)
    #vote_state = db.Column(db.Integer)


class VisitVote(db.Model):
    _tablename__ = 'visit_votes'
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'))
    article_id = db.Column(db.Integer)


class SensitiveWord(db.Model):
    __tablename__ = 'sensitive_words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50))

    # =========================================================================
    # operating db by primary key
    # =========================================================================
class db_tool:

    @staticmethod
    def delete_article_relative(id):
        article = Article.query.filter_by(id=id).first()
        article_vote = ArticleVote.query.filter_by(article_id=id).first()

        if article:
            db.session.delete(article)
            db.session.commit()

        if article_vote:
            db.session.delete(article_vote)
            db.session.commit()

    @staticmethod
    def delete_comment_relative(id):
        comment = Comment.query.filter_by(id=id).first()
        comment_vote = CommentVote.query.filter_by(comment_id=id).first()

        if comment:
            db.session.delete(comment)
            db.session.commit()

        if comment_vote:
            db.session.delete(comment_vote)
            db.session.commit()

    @staticmethod
    def hide_article(id):
        article = Article.query.filter_by(id=id).first()
        if article:
            article.status = 0
            db.session.add(article)
            db.session.commit()







# ==============================================================================================
# Tool class include some usual methods
# ==============================================================================================
class Tool:

    @staticmethod
    def find(subject):
        if(subject.pid=='None'):
            print(subject.id)
        else:
            subject = Subject.query.filter_by(id=subject.pid).first()
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
            subject = Subject.query.filter_by(id=subject.pid).first()
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
        f = open('static/sensitive words/1.txt', 'r')
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
            if x < 120:
                return "pivot"
            else:
                session['last_time'] = str(datetime.now().strftime("%Y-%m-%d %H:%M"))


    # =======================================================================================================
    # @param article orm object
    # @return article's metric
    # =======================================================================================================
    @staticmethod
    def calculate_metric(article):
        '''
        newest_comment = Comment.query.filter_by(article_id=article.id).last()
        Avisit = math.log(article.visit, 10) * 4
        Ascore = article.upvote - article.downvote
        Aage = (newest_comment.time - article.time).seconds
        metric = Avisit * Ascore / Aage
        article.metric = metric
        '''
        likes = article.upvote
        dislikes = article.downvote
        visits = article.visit
        comments = Comment.query.filter_by(article_id=article.id).count()

        metric = likes * 50 - dislikes * 30 + visits * 10 + comments * 20
        return metric



    @staticmethod
    def email_display_filter(email):
        pre = email[:email.rfind('@')]
        display = pre[:len(pre) // 2]
        suf = email[email.rfind('@') + 1:]

        for i in range(len(pre[len(pre) // 2:])):
            display += '*'

        return display + suf


# =========================================================================================
# like and dislike
# ========================================================================================
@app.route('/article_upvote/<articleID>')
def article_upvote(articleID):
    # get goal article
    article = Article.query.filter_by(id=articleID).first()

    ip = session.get('ip')
    visitor = Visitor.query.filter_by(ip=ip).first()

    articlevote = ArticleVote.query.filter_by(visitor_id=visitor.id, article_id=articleID).first()


    # didn't vote this article before
    if articlevote is None:
        articlevote = ArticleVote(visitor_id=visitor.id, article_id=articleID)
        article.upvote += 1
        article.metric = Tool.calculate_metric(article)

        # Tool.calculate_metric(article)

        db.session.add(articlevote)
        db.session.add(article)
    else:
        return jsonify({'ht': 'you has been voted, please do not submit repeatedly', 'upvote': article.upvote})
    return jsonify({'upvote': article.upvote})


@app.route('/article_downvote/<articleID>')
def article_downvote(articleID):
    # get goal article
    article = Article.query.filter_by(id=articleID).first()

    ip = session.get('ip')
    visitor = Visitor.query.filter_by(ip=ip).first()

    articlevote = ArticleVote.query.filter_by(visitor_id=visitor.id, article_id=articleID).first()
    # didn't vote this article before
    if articlevote is None:
        articlevote = ArticleVote(visitor_id=visitor.id, article_id=articleID)
        article.downvote += 1
        article.metric = Tool.calculate_metric(article)

        db.session.add(articlevote)
        db.session.add(article)
    else:
        return jsonify({'ht': 'you has been voted, please do not submit repeatedly', 'downvote': article.downvote})
    return jsonify({'downvote': article.downvote})


@app.route('/comment_upvote/<commentID>')
def comment_upvote(commentID):
    # get goal comment
    comment = Comment.query.filter_by(id=commentID).first()
    ip = session.get('ip')
    visitor = Visitor.query.filter_by(ip=ip).first()

    commentvote = CommentVote.query.filter_by(visitor_id=visitor.id, comment_id=commentID).first()
    # didn't vote this article before
    if commentvote is None:
        commentvote = CommentVote(visitor_id=visitor.id, comment_id=commentID)
        comment.upvote += 1
        db.session.add(commentvote)
        db.session.add(comment)
    else:
        return jsonify({'ht': 'you has been voted, please do not submit repeatedly', 'upvote': comment.upvote})
    return jsonify({'upvote': comment.upvote})


@app.route('/comment_downvote/<commentID>')
def comment_downvote(commentID):
    # get goal comment
    comment = Comment.query.filter_by(id=commentID).first()
    ip = session.get('ip')
    visitor = Visitor.query.filter_by(ip=ip).first()

    commentvote = CommentVote.query.filter_by(visitor_id=visitor.id, comment_id=commentID).first()
    # didn't vote this article before
    if commentvote is None:
        commentvote = CommentVote(visitor_id=visitor.id, comment_id=commentID)
        comment.downvote += 1
        db.session.add(commentvote)
        db.session.add(comment)
    else:
        return jsonify({'ht': 'you has been voted, please do not submit repeatedly', 'downvote': comment.downvote})
    return jsonify({'downvote': comment.downvote})


# =========================================================================================
# check if a email is banned
# ========================================================================================
@app.route('/check/<mail>')
def check_mail(mail):
    author = Author.query.filter_by(mail=mail).first()
    if not author:
        return jsonify('ok')
    #return jsonify({'isbanned': author.is_banned})
    return jsonify(author.is_banned)


# ==================================================================================================
# subject
# ==================================================================================================
@app.route('/subject/<subjectID>')
def get_subject(subjectID):
    subject = Subject.query.filter_by(id=subjectID).first()
    url = Tool.subject_url(subject)

    # articles = subject.articles
    articles = Article.query.filter_by(subject_id=subject.id, status=1).all()

    # ==================================================
    # hot article
    # ==================================================
    hot_article = []
    total = 0

    a = db.session.query(Article).filter(
        Article.subject_id == subject.id,
        Article.metric > threshold
    ).all()

    '''
    if a:

        pivot = random.randint(1, len(a))

        print(pivot)

        for x in a:
            total += 1
            if pivot == total:
                hot_article = x
    '''
    for x in a:
        hot_article.append(x)




    return render_template('subject.html', url=url, subject_id=subject.id, articles=articles, hot_article=hot_article, Tool=Tool)


# ============================================================================================
# before request
# ============================================================================================
@app.before_request
def before_request():
    #ip = str(request.remote_addr)
    #ip = '127.0.0.5'
    ip = IP
    session['ip'] = ip
    visitor = Visitor.query.filter_by(ip=ip).first()
    if visitor is None:
        visitor = Visitor(ip=ip)
        db.session.add(visitor)
    else:
        # banned ip, can not visitor
        if Visitor.query.filter_by(ip=ip).first().is_banned:
            print('you have beenn banned')
            return render_template('error.html', message='you have beenn banned')

        # ======================================================================================
        # from now on, ip is valid
        # ======================================================================================

        # about visit of a article
        if request.path.startswith('/article'):
            article_id = Tool.find_path_last_id(request.path)
            visitor = Visitor.query.filter_by(ip=ip).first()
            visitvote = VisitVote.query.filter_by(visitor_id=visitor.id, article_id=article_id).first()
            # first visit this article
            if visitvote is None:
                article = Article.query.filter_by(id=article_id).first()
                article.visit += 1
                article.metric = Tool.calculate_metric(article)
                visitvote = VisitVote(visitor_id=visitor.id, article_id=article_id)
                db.session.add(visitvote)
                db.session.add(article)


# ============================================================================================#
#                                         index                                               #
# ============================================================================================#
@app.route('/')
def index():
    return render_template('io.html')


@app.route('/test')
def test_one():
    return render_template('test.html')


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
        for subject in Subject.query.filter_by(pid=subject.id).all():
            find_subjects(subject, count + 1)

    subjects = Subject.query.filter_by(pid='None').all()
    out.write('{% extends "template.html" %}' + '\n')
    out.write('{% block content %}' + '\n')
    for subject in subjects:
        find_subjects(subject, 0)
        print('\n')

    out.write('{%  endblock  %}' + '\n')
    out.flush()
    out.close()

    return render_template('io.html')
    # return redirect('/')


# ================================================================================
# Edit and add subject
# ================================================================================
@app.route('/edit_subcategory', methods=['GET', 'POST'])
def add_sub_category():
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        subject_name = request.form['subject_name']

        duplicate1 = Subject.query.filter_by(name=subject_name).first()
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
            subject = Subject(name=subject_name, pid=subject_id)
            if subject_id is None:
                subject = Subject(name=subject_name)
            db.session.add(subject)
            db.session.flush()
            # return render_template('add_subcategory.html',)
            create_index()
        # return render_template('io.html')
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
        # means that author didn't in database now
        if not Author.query.filter_by(mail=email).first():
            author = Author(mail=email, is_banned=False)
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
        # can not submit in short time
        # ----------------------------------------------------------------
        if Tool.check_short_time() == 'pivot':
            email = request.form['email']
            subject_id = request.form['subject_id']
            title = request.form['title']
            abstract = request.form['abstract']
            highlight = request.form['highlight']
            message = 'You post too many time in short time!'
            return render_template('error.html', message=message)
        else:
            author_id = Author.query.filter_by(mail=email).first().id
            subject_id = request.form['subject_id']
            title = request.form['title']
            abstract = request.form['abstract']
            highlight = request.form['highlight']
            time = datetime.now()
            article = Article(author_id=author_id, subject_id=subject_id, title=title, abstract=abstract, highlight=highlight, time=time, upvote=0, downvote=0, visit=0)
            db.session.add(article)
            db.session.flush()
            upload_file(article)

            return redirect(url_for('get_article', articleID=article.id))

        #return render_template('io.html')
    else:
        email = request.args.get('email')
        subject_id = request.args.get('subject_id')
        return render_template('post_article.html', email=email, subject_id=subject_id)


# ==============================================================================================================================
# add sub category
# ==============================================================================================================================


# ============================================================================================
# submit after edit
# ============================================================================================
@app.route('/postpaper', methods=['POST'])
def post_paper():
    #email = request.args.get('email')
    #subject_id = request.args.get('subject_id')
    pass


# =============================================================================================
# article
# =============================================================================================

@app.route('/article/<articleID>')
def get_article(articleID):
    article = Article.query.filter_by(id=articleID).first()
    ip = session.get('ip')

    if not Visitor.query.filter_by(ip=ip).first():
        article.visit += 1
        db.session.add(article)

    comments = article.comments
    #comments = Comment.query.order_by(Comment.time.desc())


    return render_template('article.html', article=article, comments=comments, Tool=Tool)


# ========================================================================
# upload pdf file
# ========================================================================
@app.route('/postPdf', methods=['GET', 'POST'])
def upload_file(article):
    if request.method == 'POST':

        file = request.files['file']

        # session['filename'] = file.filename
        if file and allowed_file(file.filename):
            print('filename:--------------' + file.filename)
            u = str(uuid.uuid1())
            file.filename = u + file.filename
            filename = secure_filename(file.filename)
            #
            # print(article.title)
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
@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename, as_attachment=True)


# ======================================================================
# post comment
# ======================================================================
@app.route('/post_comment/<articleID>', methods=['POST'])
def post_comment(articleID):
    if Tool.check_short_time() == 'pivot':
        email = request.form['email']
        body = request.form['body']
        message = 'You post too many time in short time!'
        return render_template('error.html', message=message)

    email = request.form['email']
    body = request.form['body']
    time = datetime.now()
    # means that author didn't in database now
    if not Author.query.filter_by(mail=email).first():
        author = Author(mail=email, is_banned=False)
        db.session.add(author)

    author_id = Author.query.filter_by(mail=email).first().id
    comment = Comment(author_id=author_id, article_id=articleID, body=body, upvote=0, downvote=0, time=time)
    db.session.add(comment)
    article = Article.query.filter_by(id=articleID).first()
    article.metric = Tool.calculate_metric(article)
    return redirect(url_for('get_article', articleID=articleID))


# ===============================================================================
# donation
# ===============================================================================
@app.route('/donation')
def donaton():
    return render_template('donation.html')

# ===========================================================================
# search function
# ===========================================================================
@app.route('/search')
def search():
    articles = None
    comments = None
    message = None

    select = request.args.get('select')
    content = request.args.get('content')

    a = db.session.query(Article).filter(or_(Article.title.contains(content), Article.highlight.contains(content), Article.abstract.contains(content))).all()
    c = db.session.query(Comment).filter(Comment.body.contains(content))



    if select == 'article':
        articles = a
    if select == 'comment':
        comments = c




    return render_template('search.html', articles=articles, comments=comments, Tool=Tool, message=message)


@app.route('/error/<message>')
def error(message):
    return render_template('error.html', message=message)


@app.route('/author/<author_id>')
def author(author_id):
    articles = Article.query.order_by(Article.time.desc()).filter_by(author_id=author_id).all()
    comments = Comment.query.order_by(Comment.time.desc()).filter_by(author_id=author_id).all()
    return render_template('author.html', articles=articles, comments=comments, Tool=Tool)



if __name__ == '__main__':
    app.run(port=8080, debug=True)







