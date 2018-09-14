#!/usr/bin/env pythom3

"""
File format I/O handlings
"""

from sys import stderr

from .token import Token
from .analysis import Analysis


def next_plaintext(f):
    '''tokenise a line of text.

    @todo should get sentence from plaintext in the future.'''
    tokens = list()
    for line in f:
        surfs = line.strip().split()
        pos = 1
        for surf in surfs:
            token = Token(surf)
            if pos == 1:
                token.firstinsent = True
            else:
                token.firstinsent = False
            token.pos = pos
            pos += 1
            tokens.append(token)
        sep = Token()
        sep.nontoken = "separator"
        tokens.append(sep)
        return tokens
    eoft = Token()
    eoft.nontoken = "eof"
    tokens.append(eoft)
    return tokens


def next_conllu(f):
    '''tokenise a conllu sentence or comment.

    Should be used a file-like iterable that has CONLL-U sentence or
    comment or empty block coming up.'''
    tokens = list()
    for line in f:
        fields = line.strip().split('\t')
        token = Token()
        if len(fields) != 10:
            if line.startswith('#'):
                token.nontoken = "comment"
                token.comment = line.strip()
                tokens.append(token)
                return tokens
            elif line.strip() == '':
                token.nontoken = "separator"
                token.comment = ''
                tokens.append(token)
                return tokens
            else:
                token.nontoken = "error"
                token.error = line.strip()
                tokens = [token]
                return tokens
        token.gold = line.strip()
        try:
            index = int(fields[0])
        except ValueError:
            if '-' in fields[0]:
                # MWE
                continue
            elif '.' in fields[0]:
                # a ghost
                continue
            else:
                print("Cannot figure out token index", fields[0],
                      file=stderr)
                exit(1)
        token.pos = index
        if index == 1:
            token.firstinsent = True
        token.surf = fields[1]
        if fields[9] != '_':
            miscs = fields[9].split('|')
            for misc in miscs:
                k, v = misc.split('=')
                if k == 'SpaceAfter':
                    token.spaceafter = v
                elif k in ['Alt', 'FTB-PronType', 'FTB-Rel',
                           'Missed-Rel', 'FTB-rel', 'Join',
                           'Missed-SUBCAT', 'FTB-Sub', 'Prefix',
                           'FTB1-InfForm', 'Missed-POSITION']:
                    # FTB stuff
                    pass
                else:
                    print("Unknown MISC", k, file=stderr)
                    exit(1)
        tokens.append(token)
    eoft = Token()
    eoft.nontoken = "eof"
    tokens.append(eoft)
    return tokens


def next_vislcg(f, isgold=True):
    '''Tokenises a sentence from VISL-CG format data.

    Returns a list of tokens when it hits first non-token block, including
    a token representing this non-token block. If the block contains analyses
    as well as surface forms, they will be processed too.

    Args:
        isgold: if True, the VISL CG-3 analyses are read into token's gold
                analysis data, otherwise they are appended to token's analyses
                list.

    Returns:
        list of tokens found in f at its current read position, up to and
        including next non-token found (can be EOF).
    '''
    tokens = list()
    pos = 1
    token = None
    for line in f:
        line = line.rstrip()
        if not line or line == '':
            if token:
                tokens.append(token)
            token = Token()
            token.nontoken = "separator"
            token.comment = ''
            tokens.append(token)
            return tokens
        elif line.startswith("#") or line.startswith("<"):
            # # comment, or
            # <TAG> </TAG>
            if token:
                tokens.append(token)
            token = Token()
            token.nontoken = "comment"
            token.comment = line.strip()
            tokens.append(token)
            return tokens
        elif line.startswith('"<') and line.endswith('>"'):
            # "<surf>"
            if token:
                tokens.append(token)
            token = Token()
            token.pos = pos
            token.surf = line[2:-2]
            if pos == 1:
                token.firstinsent = True
            pos += 1
        elif line.startswith('\t"'):
            # \t"lemma" ANAL ANAL ANAL
            if isgold:
                token.gold = line.strip()
            else:
                anal = Analysis.fromvislcg(line)
                token.analyses.append(anal)
        elif line.startswith(';\t"'):
            # ;\t"lemma" ANAL ANAL ANAL KEYWORD:rulename
            token.nontoken = "comment"
            token.comment = line.strip()
        else:
            token.nontoken = "error"
            token.error = 'vislcg: ' + line.strip()
    if token:
        tokens.append(token)
    eoft = Token()
    eoft.nontoken = "eof"
    tokens.append(eoft)
    return tokens


def next_omorfi(f):
    '''Read next block in omorfi internal stream format.'''
    tokens = []
    return tokens
