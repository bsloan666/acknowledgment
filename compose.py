#!/usr/bin/env python
"""
Given a CSV containing some fields, generate letters of thanks
and announcments to those on whose behalf gifts were made.
"""

import os
import sys 
import re
import htmlier
import datetime
from collections import Counter

donee_template = """Dear $DONEE$,
We are pleased to inform you that $TYPE$
$PARTICIPLE$ been made to the church
$HONOREE$
From
$DONOR$
We give thanks to God for these gifts.

West Los Angeles United Methodist Church
1913 Purdue Avenue
Los Angeles, CA 90025

$DATE$"""

donor_template = """Dear $DONOR$,
Thank you for your gift$PLURAL$
$$AMOUNT$
given to the church $HONOREE$
$ACK$$DONEE$
We give thanks to God for your gift.

West Los Angeles United Methodist Church
1913 Purdue Avenue, LA, CA 90025

No goods or services were provided by the
church in return for this contribution.

$DATE$"""

ack = """An acknowledgement of your gift
has been sent to
"""
acks = """Acknowledgements of your gifts
have been sent to
"""


def donor_thanks(donor, fields):
    print(fields)
    result = donor_template
    result = re.sub('\$DONOR\$',donor, result)
    multiple = False
    if len(fields['amounts']) > 1:
        multiple=True
        result = re.sub('\$AMOUNT\$', str(sum([int(float(x)) for x in fields['amounts']])), result)
    else:    
        result = re.sub('\$AMOUNT\$', fields['amounts'][0], result)
    tmp = ""    
    for hon in fields['honorees']:
        if hon:
            tmp+=hon+'\n'
    tmp = re.sub('of ', 'of\n', tmp)
    tmp = re.sub('In ', 'in ', tmp)
    result = re.sub('\$HONOREE\$', tmp, result)

    tmp = ""
    if fields['donees'] and fields['donees'][0]:
        if multiple:
            result = re.sub('\$ACK\$', acks, result)
        else:    
            result = re.sub('\$ACK\$', ack, result)
        for don in fields['donees']:
            if don:
                tmp+=don+'\n'
        result = re.sub('\$DONEE\$', tmp, result)
    else:
        result = re.sub('\$ACK\$', "", result)
        result = re.sub('\$DONEE\$', "", result)

    if multiple:
        result = re.sub('\$PLURAL\$', 's totaling', result)
    else:    
        result = re.sub('\$PLURAL\$', ' of', result)

    result = re.sub('\$DATE\$', datetime.date.today().strftime("%B %d, %Y"), result)
    return result

def donee_announce(donee, fields):
    result = donee_template
    result = re.sub('\$DONEE\$', donee, result)
    multiple_donors = len(fields['donors']) > 1
    counts = Counter(fields['types'])
    multiple_types = len(counts) > 1
    tmp=fields['honoree']
    tmp = re.sub('of ', 'of\n', tmp)
    tmp = re.sub('In ', 'in ', tmp)
    result = re.sub('\$HONOREE\$', tmp, result)
    tmp = ""
    for don in fields['donors']:
        if don:
            tmp+=don+'\n'
    result = re.sub('\$DONOR\$', tmp, result)
    if multiple_donors:
        result = re.sub('\$PARTICIPLE\$', 'have', result)
    else:
        result = re.sub('\$PARTICIPLE\$', 'has', result)
    tmp = ""
    if multiple_donors:
        tmp = "\n"
        for i, tp in enumerate(list(set(fields['types']))):
            if i:
                tmp+=' and '
            tmp+=tp+'s\n'
    else:
        tmp = "a\n"+fields['types'][0]
    result = re.sub('\$TYPE\$', tmp, result)

    result = re.sub('\$DATE\$', datetime.date.today().strftime("%B %d, %Y"), result)
    return result

def donor_totals(records):
    donor_dict = {}
    for rec in records:
        if rec['donor'] not in donor_dict:
            donor_dict[rec['donor']] = {'amounts':[], 'honorees':[], 'donees':[]}
        if rec['amount'] != '---':
            donor_dict[rec['donor']]['amounts'].append(rec['amount'])
        else:    
            donor_dict[rec['donor']]['amounts'].append('0')
        donor_dict[rec['donor']]['honorees'].append(rec['honoree'])
        donor_dict[rec['donor']]['donees'].append(rec['donee'])
    return donor_dict

def donee_totals(records):
    donee_dict = {}
    for rec in records:
        if rec['donee'] not in donee_dict:
            donee_dict[rec['donee']] = {'honoree':rec['honoree'], 'donors':[], 'types':[]}
        donee_dict[rec['donee']]['donors'].append(rec['donor'])
        donee_dict[rec['donee']]['types'].append(rec['type'])
    return donee_dict
        
def all_records(filename):
    handle = open(filename, 'r')
    lines = handle.readlines()
    handle.close()
    result = []
    for line in lines[1:]:
        values = re.split(',', line.strip())
        if values[0]:
            result.append( 
                dict(zip(
                    ['honoree', 'donor', 'amount', 'donee', 'type'], 
                    values)))
    return result


if __name__ == "__main__":
    records = all_records(sys.argv[1])
    don_tots = donor_totals(records)
    dee_tots = donee_totals(records)
    htm = htmlier.HTMLier()
    style = htm.tag('style', 
        "i {text-align: center; font-family: 'New Times Roman'; font-size: 12pt;} div {text-align: center; margin: 0 auto;} body{ margin: 0 auto; }")
    head = htm.tag('head', style)
    content = ""
    for donor,data in don_tots.items():
        note = '<p style="page-break-before: always">'
        note += '<hr class="pb">'
        temp = donor_thanks(donor, data)
        lines = re.split('\n', temp)
        mid = ""
        reg = True
        for line in lines:
            if "No goods" in line:
                reg = False
            if not reg:
                mid += htm.tag('i', line, style='font-size: 9pt;')
            else:    
                mid += htm.tag('i', line)
            mid += "<br>"
        note += htm.tag('div', mid) 
        content += note 

    for donee,data in dee_tots.items():
        note = '<p style="page-break-before: always">'
        note += '<hr class="pb">'
        temp = donee_announce(donee, data)
        lines = re.split('\n', temp)
        mid = ""
        for line in lines[0:-1]:
            mid += htm.tag('i', line)
            mid += "<br>"

        mid += htm.tag('i', lines[-1], style='font-size: 9pt;')    
        mid += "<br>"
        note += htm.tag('div', mid) 
        content += note

    
    body = htm.tag('body', content)
    page = htm.tag('html', head+body)
   
    handle = open(sys.argv[2], 'w')
    handle.write(page)
    handle.write('\n')
    handle.close()
