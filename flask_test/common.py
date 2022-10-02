from flask import Flask, jsonify, request, abort
import re

DATABASE_URI = 'mariadb://test:wanted12@localhost/wanted'

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