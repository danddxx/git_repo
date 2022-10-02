from models import *
from common import *

app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/search')
def search_auto_complete():
    company_names = []
    language = request.headers.get('x-wanted-language')
    name = request.args.get('name')
    if language == 'ko':
        company = Company.query.filter(Company.company_ko.contains(name)).all()
    elif language == 'en':
        company = Company.query.filter(Company.company_en.contains(name)).all()
    else:
        company = Company.query.filter(Company.company_ja.contains(name)).all()
    for company_info in company:
        company_names.append(obj_to_dict(company_info, language, auto_complete = True))
    return jsonify(company_names)

@app.route('/companies', methods = ['POST', 'GET'])
def search_by_name():
    language = request.headers.get('x-wanted-language')
    if request.method == 'GET':
        company_list = []
        name = request.args.get('name')
        if language == 'ko':
            company = Company.query.filter_by(company_ko = name).all()
        elif language == 'en':
            company = Company.query.filter_by(company_en = name).all()
        else:
            company = Company.query.filter_by(company_ja = name).all()
        if not company: abort(404)
        for company_info in company:
            company_list.append(obj_to_dict(company_info, language))
        return jsonify(company_list)
    if request.method == 'POST':
        company_json = request.get_json()
        company = Company()
        company.company_ko = company_json['company_name']['ko']
        company.company_en = company_json['company_name']['en']
        company.company_ja = company_json['company_name']['ja']
        company.tag_ko = ''
        company.tag_en = ''
        company.tag_ja = ''
        for i in range(len(company_json['tags'])):
            company.tag_ko += company_json['tags'][i]['tag_name']['ko'] + '|'
            company.tag_en += company_json['tags'][i]['tag_name']['en'] + '|'
            company.tag_ja += company_json['tags'][i]['tag_name']['ja'] + '|'
        company.tag_ko = company.tag_ko[:-1]
        company.tag_en = company.tag_en[:-1]
        company.tag_ja = company.tag_ja[:-1]
        db.session.add(company)
        db.session.commit()
        return jsonify(obj_to_dict(company, language))

@app.route('/tags')
def search_by_tag():
    company_list = []
    language = request.headers.get('x-wanted-language')
    tag = request.args.get('tag')
    tag_no = re.sub(r'[^0-9]', '', tag)
    company = Company.query.filter(Company.tag_ko.contains(tag_no)).all()
    for company_info in company:
        if tag_no in re.findall(r'\d+', re.sub(r'[^0-9]', ' ', company_info.tag_ko)):
            company_list.append(obj_to_dict(company_info, language, null_check = True))
    return jsonify(company_list)

@app.route('/companies/<company_name>/tags', methods = ['POST', 'GET'])
def add_tag(company_name):
    if request.method == 'POST':
        language = request.headers.get('x-wanted-language')
        if language == 'ko':
            company = Company.query.filter_by(company_ko=company_name).one_or_none()
        elif language == 'en':
            company = Company.query.filter_by(company_en=company_name).one_or_none()
        else:
            company = Company.query.filter_by(company_ja=company_name).one_or_none()
        if not company: abort(404)
        tag_json = request.get_json()
        for i in range(len(tag_json)):
            company.tag_ko += '|' + tag_json[i]['tag_name']['ko']
            company.tag_en += '|' + tag_json[i]['tag_name']['en']
            company.tag_ja += '|' + tag_json[i]['tag_name']['ja']
        db.session.commit()
        return jsonify(obj_to_dict(company, language))

@app.route('/companies/<company_name>/tags/<tag_name>', methods = ['POST', 'GET'])
def delete_tag(company_name, tag_name):
    if request.method == 'POST':
        language = request.headers.get('x-wanted-language')
        if language == 'ko':
            company = Company.query.filter_by(company_ko=company_name).one_or_none()
        elif language == 'en':
            company = Company.query.filter_by(company_en=company_name).one_or_none()
        else:
            company = Company.query.filter_by(company_ja=company_name).one_or_none()
        if not company: abort(404)
        tag_no = re.sub(r'[^0-9]', '', tag_name)
        company.tag_ko = re.sub('태그_' + tag_no, '', company.tag_ko).replace('||', '|')
        company.tag_en = re.sub('tag_' + tag_no, '', company.tag_en).replace('||', '|')
        company.tag_ja = re.sub('タグ_' + tag_no, '', company.tag_ja).replace('||', '|')
        db.session.commit()
        return jsonify(obj_to_dict(company, language))

def obj_to_dict(obj, language, auto_complete = False, null_check = False):
    d = {}
    if language == 'ko':
        d['company'] = obj.company_ko
        if not auto_complete: d['tag'] = obj.tag_ko
    elif language == 'en':
        d['company'] = obj.company_en
        if not auto_complete: d['tag'] = obj.tag_en
    else:
        d['company'] = obj.company_ja
        if not auto_complete: d['tag'] = obj.tag_ja
    if null_check and not d['company']:
        if obj.company_ko: d['company'] = obj.company_ko
        elif obj.company_en: d['company'] = obj.company_en
        elif obj.company_ja: d['company'] = obj.company_ja
    return d

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(port=3200)