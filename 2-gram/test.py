#!/usr/bin/env python
# -*- coding: utf-8 -*- ##以utf-8编码储存中文字符,因为默认py脚本文件都是 ANSCII 编码

import sys 
import math  
import time
reload(sys) 
sys.setdefaultencoding("utf-8")
# 程序还木有来得及处理在语料库中没有的单的字，如果出现，整句都不会切分
# 文件中字符编码注意采用 无bom 的utf-8
# 概率取对数，然后将乘法改为加法
class NGram:
    def __init__(self):
        self.result_filename = '2017110758.txt'   # 最后展示结果的文件名称
        self.word1_dict = {}         #记录每个词语的概率
        self.word1_dict_count = {}  #记录每个词的词频
        self.word2_dict_count = {}  #记录词频,2-gram  

        self.all_words = 0  # 所有词语的个数

        self.all_freq = 0   # 所有词语的总出现次数
        self.max_prob = -100    # 一句话的最大概率大小
        self.max_prob_gap_list = []         # 最大概率时插入位置序列
        self.max_words_len = 9              # 认为的最大的词语长度
    #估算未出现的词的概率,根据beautiful data里面的方法估算  ，这里没有用到
    def get_unkonw_word_prob(self, word):  
        return math.log(10.0/(self.all_freq*10**len(word)))  

    # 获得各个词语的概率  
    def get_word_prob(self,word):
        if self.word1_dict.has_key(word):
            prob = self.word1_dict[word]
        else:
            prob = self.get_unkonw_word_prob(word)  
        return prob

    # 获取两个词语的转移概率，前提是forward_word在语料库中存在
    def get_word_trans(self,forward_word,next_word):
        trans_word = forward_word+' '+next_word
        if self.word2_dict_count.has_key(trans_word):
            return math.log((self.word2_dict_count[trans_word]+1.0)/(self.word1_dict_count[forward_word]+self.all_words))
        else:
            return math.log(1.0/(self.word1_dict_count[forward_word]+self.all_words))
        
    #加载词典,   之后调用seg进行分词
    def initial_dict(self, gram1_file, gram2_file):
        #读取语料库文件
        dict_file = open(gram1_file,"r")
        #因为读取文件是一行一行读取的
        for line in dict_file:
            sequence= line.strip()
            sequence = sequence.decode("utf-8")
            # print sequence
            list = sequence.split('  ')     # 文本中间两个空格
            forward_key = 's'  # 最初的前面一个key为 s
            # 取出每个词，暂时不理会词性
            for unit in list:
                key =  unit.split('/')[0]
                if '199801' in key: pass
                elif self.word1_dict_count.get(key):
                    self.word1_dict_count[key] = self.word1_dict_count[key]+1.0
                else:
                    self.word1_dict_count.setdefault(key,1.0)

                # 记录词频,2-gram   
                if '199801' in key: pass 
                else:   
                    combination_key = forward_key+' '+key
                    if self.word2_dict_count.get(combination_key):
                        self.word2_dict_count[combination_key] = self.word2_dict_count[combination_key]+1.0
                    else:
                        self.word2_dict_count.setdefault(combination_key,1.0)
                    forward_key = key


        self.all_freq = sum(self.word1_dict_count.itervalues())  # 所有词的词频
        for key in self.word1_dict_count.iterkeys():            # 所有词的个数
            self.all_words = self.all_words+1 
        # print self.all_freq
        # print self.all_words
        # for key in self.word2_dict_count.iterkeys():
        #     print key.decode("utf-8") +' -->'
        #     print self.word2_dict_count[key]
        # 计算每个词语出现的概率,放入word1_dict
        for key in self.word1_dict_count.keys():
            self.word1_dict.setdefault(key,math.log(self.word1_dict_count[key]/self.all_freq))

        # 下面是对测试案例进行计算

        test_file = open(gram2_file,"r")
        open(self.result_filename, 'w').write('')           # 先将文件内容清空
        result_file = open(self.result_filename,'w+')
        for line in test_file: 
            line = line.strip() 
            result = self.split_line(line)
            # print '--->'+result
            result_file.write(result)
            result_file.write('\n')
        
        
        # print self.split_line('国家主席江泽民今天在中南海会见了美国联邦快递公司董事长弗雷德里克·史密斯及由他率领的')
        

        print "all things over" 
    # 将句子进行拆分后处理,所有标点符号都进行拆分，并且处理后将结果合并返回,保证处理时每句不会太长.
    def split_line(self,line):
        sequence = line.decode("utf-8")
        result_str = ''
        work_sequence = ''
        for tag in range(len(sequence)):
            work_sequence = work_sequence+sequence[tag]
            if (tag+1)==len(sequence) or sequence[tag]=='，' or sequence[tag]=='。'or sequence[tag]==','or sequence[tag]=='、'or sequence[tag]=='（'or sequence[tag]=='）'or sequence[tag]=='；'or sequence[tag]=='：'or sequence[tag]=='！'or sequence[tag]=='的':
                if result_str=='':
                    result_str = self.seg(work_sequence)
                    work_sequence = ''
                else:
                    result_str = result_str+' '+self.seg(work_sequence)
                    work_sequence = ''
        return result_str
    # 对单个句子进行分词处理
    def seg(self,sequence):
        words_list = {}         # 其中的格式为   {(下标,后接几个字):值}，em 这个 值 没什么用
        # 将句子中的max_words_len个字以内的词语都提取出来
        for t in range(self.max_words_len):
            if len(sequence)>t:
                for i in range(len(sequence)-t):
                    str = ''+sequence[i]
                    for k in range(t):
                        str = str+sequence[i+k+1]
                    if self.word1_dict_count.has_key(str):
                        words_list.setdefault((i,t),1)
                        # print str
        gap_list = []
        prob = 0            # 当前的概率 （这里是经过log之后的值）
        self.max_prob = -10000
        self.max_prob_gap_list = []
        self.seg_detail(sequence,0,words_list,gap_list,prob,'s')
        # print self.max_prob_gap_list[:]
        str_test = ''
        t= 0
        for i in range(len(sequence)):
            str_test = str_test+sequence[i]
            if len(self.max_prob_gap_list)>0:           # 表示如果max_prob_gap_list不为空才执行插入空格操作,以插入空格的方式分词
                if i == self.max_prob_gap_list[t]-1:
                    str_test = str_test+' '
                    if (t+1)<len(self.max_prob_gap_list):
                        t = t+1
        return str_test

    #具体循环实现比较概率
    def seg_detail(self,sequence,index,words_list,gap_list,prob,forward_word):
        for t in range(self.max_words_len):
            if words_list.has_key((index,t)):
                if index == 0:
                    prob = self.get_word_prob(sequence[0:(t+1)])
                else:
                    p_trans = self.get_word_trans(forward_word,sequence[index:(index+t+1)])  # 获取转移概率
                    prob = p_trans+prob                                                 # 当前总概率
                forward_word  = sequence[index:(index+t+1)]
                if (index+t+1)>=len(sequence):          #  结束
                    if prob>self.max_prob:
                        max_prob = prob
                        self.max_prob_gap_list = list(gap_list)
                else:
                    gap_l = list(gap_list)
                    gap_l.append(index+t+1)
                    self.seg_detail(sequence,index+t+1,words_list,gap_l,prob,forward_word)



if __name__ == '__main__':
    start = time.time()
    myseg = NGram()
    file1 = "北大(人民日报)语料库199801.txt"
    file2 = "testset.txt"
    myseg.initial_dict(file1.decode("utf-8"),file2.decode("utf-8"))
    # 将utf-8转化为gbk
    content = open('2017110758.txt').read() 
    new_content = content.decode("utf-8").encode("gbk") 
    open('2017110758.txt', 'w').write(new_content) 
    print time.time() - start
    
