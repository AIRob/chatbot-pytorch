# coding: utf-8

from global_config import *
import torch
from torch.autograd import Variable

# For Japanese tokenizer
import MeCab

tagger = MeCab.Tagger("-Owakati")

def japanese_tokenizer(sentence):
    assert type(sentence) is str

    result = tagger.parse(sentence)
    return result.split(' ')

class Lang:
    def __init__(self, name):
        self.name = name
        self.word2index = {}
        self.word2count = {}
        self.index2word = {0:'SOS', 1:'EOS'}
        self.n_words = 2
    
    def addWord(self, word):
        if word not in self.word2index:
            self.word2index[word] = self.n_words
            self.word2count[word] = 1
            self.index2word[self.n_words] = word
            self.n_words += 1

        else:
            self.word2count[word] += 1
    
    def addSentence(self, sentence):
        for word in japanese_tokenizer(sentence):
            self.addWord(word)

def readText(lang1, lang2, reverse = False):
    """
    Get Lang object and pairs
    """

    print("Reading lines...")

    # read the file and split into lines
    lines = open(PAIRS_PATH, 'r', encoding="utf-8").readlines()
    
    pairs = [[s for s in l.split('\t')] for l in lines]

    if reverse:
        pairs = [list(reversed(p)) for p in pairs]
        input_lang = Lang(lang2)
        output_lang = Lang(lang1)
    else:
        input_lang = Lang(lang1)
        output_lang = Lang(lang2)
    return input_lang, output_lang, pairs
    
    

def indexesFromSentence(lang, sentence):
    """
    Get index number list from sentence.  
    """
    return [lang.word2index[word] for word in japanese_tokenizer(sentence)]

def variableFromSentence(lang, sentence):
    """
    Get torch.LongTensor variable from sentence.
    """
    indexes = indexesFromSentence(lang, sentence)
    indexes.append(EOS_TOKEN)
    result = Variable(torch.LongTensor(indexes).view(-1, 1))
    if use_cuda:
        return result.cuda()
    else:
        return result

def variablesFromPair(input_lang, output_lang, pair):
    """
    Convert sequence to variable
    """
    
    input_variable = variableFromSentence(input_lang, pair[0])
    target_variable = variableFromSentence(output_lang, pair[1])
    return (input_variable, target_variable)

def filterPair(p):
    """
    Trimming sentence pairs. 
    """

    return len(japanese_tokenizer(p[0])) < MAX_LENGTH and \
            len(japanese_tokenizer(p[1])) < MAX_LENGTH

def filterPairs(pairs):
    """
    Get trimmed pairs.  
    """
    return [pair for pair in pairs if filterPair(pair)]

def prepareData(lang1, lang2, reverse  = False):
    if os.path.exists(PAIRS_PATH) is not True:
        print("Making pairs text...")
        with open(SOURCE_PATH) as s, open(TARGET_PATH) as t, \
            open(PAIRS_PATH, "w") as p:

            p.write(''.join([c1.strip("\n") + "\t" + c2 for c1, c2 in zip(s, t)]))

        print("Make pairs.txt .")
        
    input_lang, output_lang, pairs = readText(lang1, lang2, reverse)

    print("Read %s sentence pairs" % len(pairs))
    pairs = filterPairs(pairs)
    print("Trimmed to %s sentence pairs"% len(pairs))

    print("Counting words...")
    for pair in pairs:
        input_lang.addSentence(pair[0])
        output_lang.addSentence(pair[1])

    print("Counted words:")
    print(input_lang.name, input_lang.n_words)
    print(output_lang.name, output_lang.n_words)

    return input_lang, output_lang, pairs