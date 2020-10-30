#!/usr/bin/env python
import os
import sys 
import re

donee_template = """We are pleased to inform you that
$TYPE$
$PARTICIPLE$ been made to the church
$HONOREE$
From
$NAMES$
We give thanks to God for these gifts.

West Los Angeles United Methodist Church
1913 Purdue Avenue
Los Angeles, CA 90025
"""

donor_template = """Dear $DONOR$,
Thank you for your gift$PLURAL$ of
$$AMOUNT$
given to the church $HONOREE$
$ACK$$DONEE$
We give thanks to God for your gift.

West Los Angeles United Methodist Church
1913 Purdue Avenue, LA, CA 90025

No goods or services were provided to the
church in return for this contribution.
October 30, 2020
"""

ack = """An acknowledgement of your gift
has been sent to
"""


def donor_thanks(fields):
    result = donor_template
    result = re.sub('\$DONOR\$',fields['donor'], result)
    result = re.sub('\$AMOUNT\$', fields['amount'], result)
    tmp = re.sub('of ', 'of\n', fields['honoree'])
    tmp = re.sub('In ', 'in ', tmp)
    result = re.sub('\$HONOREE\$', tmp, result)

    if fields['donee']:
        result = re.sub('\$ACK\$', ack, result)
        result = re.sub('\$DONEE\$', fields['donee'], result)
    else:
        result = re.sub('\$ACK\$', "", result)
        result = re.sub('\$DONEE\$', "", result)

    result = re.sub('\$PLURAL\$', '', result)
    print(result)
    print()

def donor_totals(records):
    donor_dict = {}
    for rec in records:
        if rec['donor'] not in donor_dict:
            donor_dict[rec['donor']] = {'amounts':[], 'honorees':[], 'donees':[]}
        donor_dict[rec['donor']]['amounts'].append(rec['amount'])
        donor_dict[rec['donor']]['honorees'].append(rec['honoree'])
        donor_dict[rec['donor']]['donees'].append(rec['donee'])
    return donor_dict

def donee_totals(records):
    donee_dict = {}
    for rec in records:
        if rec['donee'] not in donee_dict:
            donee_dict[rec['donee']] = {'honoree':rec['honoree'], 'donors':[]}
        donee_dict[rec['donee']]['donors'].append(rec['donor'])
    return donee_dict
        
def all_records(filename):
    handle = open(filename, 'r')
    lines = handle.readlines()
    handle.close()
    result = []
    for line in lines:
        result.append( dict(zip(['honoree', 'donor', 'amount', 'donee', 'type'], re.split(',', line.strip()))))
    return result


if __name__ == "__main__":
    records = all_records(sys.argv[1])

    don_tots = donor_totals(records)
    for d,t in don_tots.items():
        print(d,t)
    dee_tots = donee_totals(records)
    for d,t in dee_tots.items():
        print(d,t)

    for rec in records:
        donor_thanks(rec)
