import re
import jieba
from jieba import posseg


class DictClassifier():
    def __init__(self):
        self.__root_filepath = "f_dict/"
        jieba.load_userdict('f_dict/mydict.txt')

        # 准备句式结构/情感词典/连词/形容词/否定词/副词词典
        self.__phrase_dict = self.__get_phrase_dict()   #短语词典
        self.__positive_dict = self.__get_dict(self.__root_filepath + "positive_dict.txt")  #积极情感词典
        self.__negative_dict = self.__get_dict(self.__root_filepath + "negative_dict.txt")  #消极情感词典
        self.__conjunction_dict = self.__get_dict(self.__root_filepath + "conjunction_dict.txt")    #连接词词典
        self.__punctuation_dict = self.__get_dict(self.__root_filepath + "punctuation_dict.txt")    #标点符号词典
        self.__adverb_dict = self.__get_dict(self.__root_filepath + "adverb_dict.txt")  #副词词典
        self.__denial_dict = self.__get_dict(self.__root_filepath + "denial_dict.txt")  #否定词词典

    def classify(self, sentence):
        return self.analyse_sentence(sentence)  #屏蔽底层实现的细节

    def analyse_sentence(self, sentence):   #sentence是test.py文件中调用的每一条评论
        # 情感分析整体数据结构
        comment_analysis = {"score": 0}     #情感值初始化为0
        # 将评论分句
        the_clauses = self.__divide_sentence_into_clauses(sentence + "%")

        # 对每分句进行情感分析
        for i in range(len(the_clauses)):
            # 情感分析子句的数据结构
            sub_clause = self.__analyse_clause(the_clauses[i].replace("。", "."))
            # 将子句分析的数据结果添加到整体数据结构中
            comment_analysis["su-clause" + str(i)] = sub_clause
            comment_analysis['score'] += sub_clause['score']

        if comment_analysis["score"] > 1:#积极
            return '积极'
        elif comment_analysis["score"] >= -1 and comment_analysis["score"] <=1:#中性
            return '中性'
        else:#消极
            return '消极'

    def __analyse_clause(self, the_clause,):
        #首先定义一个字典，
        #score:分数  positive:积极地  negative：消极的  conjunction：连接词  punctuation：标点符号    pattern：特殊类型
        sub_clause = {"score": 0, "positive": [], "negative": [], "conjunction": [], "punctuation": [], "pattern": []}
        seg_result = jieba.lcut(the_clause)

        # 判断句式：如果……就好了
        judgement = self.__is_clause_pattern2(the_clause)
        if judgement != "":
            sub_clause["pattern"].append(judgement)
            sub_clause["score"] -= judgement["value"]
            return sub_clause

        # 判断句式：是…不是…
        judgement = self.__is_clause_pattern1(the_clause)
        if judgement != "":
            sub_clause["pattern"].append(judgement)
            sub_clause["score"] -= judgement["value"]

        # 判断句式：短语
        judgement = self.__is_clause_pattern3(the_clause, seg_result)
        if judgement != "":
            sub_clause["score"] += judgement["score"]
            if judgement["score"] >= 0:
                sub_clause["positive"].append(judgement)
            elif judgement["score"] < 0:
                sub_clause["negative"].append(judgement)
            match_result = judgement["key"].split(":")[-1]
            i = 0
            while i < len(seg_result):
                if seg_result[i] in match_result:
                    if i + 1 == len(seg_result) or seg_result[i + 1] in match_result:
                        del (seg_result[i])
                        continue
                i += 1

        # 逐个分析分词
        for i in range(len(seg_result)):
            mark, result = self.__analyse_word(seg_result[i], seg_result, i)
            if mark == 0:
                continue
            elif mark == 1:
                sub_clause["conjunction"].append(result)
            elif mark == 2:
                sub_clause["punctuation"].append(result)
            elif mark == 3:
                sub_clause["positive"].append(result)
                sub_clause["score"] += result["score"]
            elif mark == 4:
                sub_clause["negative"].append(result)
                sub_clause["score"] -= result["score"]

        # 综合连词的情感值
        for a_conjunction in sub_clause["conjunction"]:
            sub_clause["score"] *= a_conjunction["value"]

        # 综合标点符号的情感值
        for a_punctuation in sub_clause["punctuation"]:
            sub_clause["score"] *= a_punctuation["value"]

        return sub_clause

    @staticmethod
    def __is_clause_pattern2(the_clause):

        re_pattern = re.compile(r".*(如果|要是|希望).+就[\u4e00-\u9fa5]*(好|完美)了")
        """
        设置正则匹配的表达式
        如果匹配成功，将该句评论作为字典的key，并将其值value设置为1.0
        re.match 尝试从字符串的起始位置匹配一个模式，如果不是起始位置匹配成功的话，match()就返回none
        """
        match = re_pattern.match(the_clause)
        if match is not None:
            pattern = {"key": "如果…就好了", "value": 1.0}
            return pattern
        return ""

    def __is_clause_pattern3(self, the_clause, seg_result):
        #__phrase_dict 为底部处理的短语词典 __get_phrase_dict 的实例化
        #seg_result为分词过后的列表
        for a_phrase in self.__phrase_dict:
            keys = a_phrase.keys()
            """
            [\u4e00-\u9fa5]*表示0或多次汉字
            在此，是表示“服务……专业”类型的语句中，……替换为汉字
            使用正则表达式匹配“服务”开头、“专业”结尾的一句评论
            """
            to_compile = a_phrase["key"].replace("……", "[\u4e00-\u9fa5]*")

            if "start" in keys:
                to_compile = to_compile.replace("*", "{" + a_phrase["start"] + "," + a_phrase["end"] + "}")
            if "head" in keys:
                to_compile = a_phrase["head"] + to_compile

            """
            利用for循环依次从构建的短语词典中取出每一个元素的key
            然后将其与事先准备好的，经过分词的文本进行正则匹配
            """
            match = re.compile(to_compile).search(the_clause)   #search扫描整个字符串，并返回第一个成功地匹配
            if match is not None:
                can_continue = True

                """
                posseg.cut()功能是进行分词，并且进行词性标注，word变量是词，而flag变量是词性，如动词、名字、地名等等
                示例如下：
                    import jieba.posseg as pseg
                    words = pseg.cut('我爱北京天安门')
                    for w in words:
                        print(w.word, w.flag)
                    
                    我 r
                    爱 v
                    北京 ns
                    天安门 ns
                """
                pos = [flag for word, flag in posseg.cut(match.group())]    #pos列表中存储每一个词的词性
                if "between_tag" in keys:
                    if a_phrase["between_tag"] not in pos and len(pos) > 2:
                        can_continue = False

                if can_continue:
                    for i in range(len(seg_result)):
                        if seg_result[i] in match.group():
                            try:
                                if seg_result[i + 1] in match.group():
                                    return self.__emotional_word_analysis(a_phrase["key"] + ":" + match.group(), a_phrase["value"],seg_result, i)
                            except IndexError:
                                return self.__emotional_word_analysis(a_phrase["key"] + ":" + match.group(), a_phrase["value"],seg_result, i)
        return ""

    def __analyse_word(self, the_word, seg_result=None, index=-1):
        # 判断是否是连词
        judgement = self.__is_word_conjunction(the_word)
        if judgement != "":
            return 1, judgement

        # 判断是否是标点符号
        judgement = self.__is_word_punctuation(the_word)
        if judgement != "":
            return 2, judgement

        # 判断是否是正向情感词
        judgement = self.__is_word_positive(the_word, seg_result, index)
        if judgement != "":
            return 3, judgement

        # 判断是否是负向情感词
        judgement = self.__is_word_negative(the_word, seg_result, index)
        if judgement != "":
            return 4, judgement

        return 0, ""

    @staticmethod
    def __is_clause_pattern1(the_clause):
        #如果出现如下这种类型的评论，将其情感值设置为1
        re_pattern = re.compile(r".*(要|选)的.+(送|给).*")
        match = re_pattern.match(the_clause)
        if match is not None:
            pattern = {"key": "要的是…给的是…", "value": 1}
            return pattern
        return ""

    #返回连接词的情感信息
    def __is_word_conjunction(self, the_word):  #the_word为seg_result[i]，i为 for i in range(len(seg_result))
        if the_word in self.__conjunction_dict:
            conjunction = {"key": the_word, "value": self.__conjunction_dict[the_word]}
            return conjunction
        return ""
    #返回标点符号的情感信息
    def __is_word_punctuation(self, the_word):
        if the_word in self.__punctuation_dict:
            punctuation = {"key": the_word, "value": self.__punctuation_dict[the_word]}
            return punctuation
        return ""
    #返回积极情感的情感信息
    def __is_word_positive(self, the_word, seg_result, index):
        # 判断分词是否在情感词典内
        if the_word in self.__positive_dict:
            # 在情感词典内，则构建一个以情感词为中心的字典数据结构
            return self.__emotional_word_analysis(the_word, self.__positive_dict[the_word], seg_result,index)
        # 不在情感词典内，则返回空
        return ""

    #返回消极情感的情感信息
    def __is_word_negative(self, the_word, seg_result, index):
        # 判断分词是否在情感词典内
        if the_word in self.__negative_dict:
            # 在情感词典内，则构建一个以情感词为中心的字典数据结构
            return self.__emotional_word_analysis(the_word, self.__negative_dict[the_word],seg_result, index)
        # 不在情感词典内，则返回空
        else:
            return ""

    def __emotional_word_analysis(self, core_word, value, segments, index):
        # 在情感词典内，则构建一个以情感词为中心的字典数据结构
        orientation = {"key": core_word, "adverb": [], "denial": [], "value": value}
        orientation_score = orientation["value"]  # my_sentiment_dict[segment]

        # 在三个前视窗内，判断是否有否定词、副词
        view_window = index - 1
        if view_window > -1:  # 无越界
            # 判断前一个词是否是情感词
            if segments[view_window] in self.__negative_dict or segments[view_window] in self.__positive_dict:
                orientation['score'] = orientation_score
                return orientation
            # 判断是否是副词
            if segments[view_window] in self.__adverb_dict:
                # 构建副词字典数据结构
                adverb = {"key": segments[view_window], "position": 1,
                          "value": self.__adverb_dict[segments[view_window]]}
                orientation["adverb"].append(adverb)
                orientation_score *= self.__adverb_dict[segments[view_window]]
            # 判断是否是否定词
            elif segments[view_window] in self.__denial_dict:
                # 构建否定词字典数据结构
                denial = {"key": segments[view_window], "position": 1,
                          "value": self.__denial_dict[segments[view_window]]}
                orientation["denial"].append(denial)
                orientation_score *= -1
        view_window = index - 2
        if view_window > -1:
            # 判断前一个词是否是情感词
            if segments[view_window] in self.__negative_dict or segments[view_window] in self.__positive_dict:
                orientation['score'] = orientation_score
                return orientation
            if segments[view_window] in self.__adverb_dict:
                adverb = {"key": segments[view_window], "position": 2,
                          "value": self.__adverb_dict[segments[view_window]]}
                orientation_score *= self.__adverb_dict[segments[view_window]]
                orientation["adverb"].insert(0, adverb)
            elif segments[view_window] in self.__denial_dict:
                denial = {"key": segments[view_window], "position": 2,
                          "value": self.__denial_dict[segments[view_window]]}
                orientation["denial"].insert(0, denial)
                orientation_score *= -1
                # 判断是否是“不是很好”的结构（区别于“很不好”）
                if len(orientation["adverb"]) > 0:
                    # 是，则引入调节阈值，0.3
                    orientation_score *= 0.3
        view_window = index - 3
        if view_window > -1:
            # 判断前一个词是否是情感词
            if segments[view_window] in self.__negative_dict or segments[view_window] in self.__positive_dict:
                orientation['score'] = orientation_score
                return orientation
            if segments[view_window] in self.__adverb_dict:
                adverb = {"key": segments[view_window], "position": 3,
                          "value": self.__adverb_dict[segments[view_window]]}
                orientation_score *= self.__adverb_dict[segments[view_window]]
                orientation["adverb"].insert(0, adverb)
            elif segments[view_window] in self.__denial_dict:
                denial = {"key": segments[view_window], "position": 3,
                          "value": self.__denial_dict[segments[view_window]]}
                orientation["denial"].insert(0, denial)
                orientation_score *= -1
                # 判断是否是“不是很好”的结构（区别于“很不好”）
                if len(orientation["adverb"]) > 0 and len(orientation["denial"]) == 0:
                    orientation_score *= 0.3
        # 添加情感分析值
        orientation['score'] = orientation_score
        # 返回的数据结构
        return orientation

    def __divide_sentence_into_clauses(self, the_sentence):
        #the_sentence表示每一条评论
        #__split_sentence函数在本函数下边，作用为将评论根据标点符号进行分句，并存储在the_clauses列表中
        the_clauses = self.__split_sentence(the_sentence)
        # 识别“是……不是……”句式
        pattern = re.compile(r"([，、。%！；？?,!～~.… ]*)([\u4e00-\u9fa5]*?(要|选)"
                             r"的.+(送|给)[\u4e00-\u9fa5]+?[，。！%；、？?,!～~.… ]+)")
        #re.search作用是返回整个字符串中第一个成功的匹配，the_sentence.strip()作用是去除整条评论首尾的空格或者换行符
        match = re.search(pattern, the_sentence.strip())
        """
        如果match不为None值并且匹配的第2个值断句后长度小于等于2时成立
        match.group(2)表示返回第二个成功匹配的字符串
        """
        if match is not None and len(self.__split_sentence(match.group(2))) <= 2:
            #定义一个列表
            to_delete = []
            """
            the_clauses为 存储一条评论 断句后的 评论列表
            如下函数的意义为：
                通过for循环获取评论列表中的每一条评论，如果其在第二个成功匹配的字符串中，将其添加到定义的列表to_delete中
            """
            for i in range(len(the_clauses)):
                if the_clauses[i] in match.group(2):
                    to_delete.append(i)
            """
            如果列表to_delect的长度大于0，循环遍历列表中每一个元素，并将其依次从该条评论断句的列表中，移除
            然后将上边匹配的第二个成功匹配的字符串，添加到列表to_delect列表首位
            """
            if len(to_delete) > 0:
                for i in range(len(to_delete)):
                    the_clauses.remove(the_clauses[to_delete[0]])   #remove() 函数用于移除列表中某个值的第一个匹配项。
                the_clauses.insert(to_delete[0], match.group(2))    #insert用于将指定对象插入列表的指定位置，第一个参数代表位置

        # 识别“要是|如果……就好了”的假设句式
        pattern = re.compile(r"([，%。、！；？?,!～~.… ]*)([\u4e00-\u9fa5]*?(如果|要是|"
                             r"希望).+就[\u4e00-\u9fa5]+(好|完美)了[，。；！%、？?,!～~.… ]+)")
        match = re.search(pattern, the_sentence.strip())
        if match is not None and len(self.__split_sentence(match.group(2))) <= 3:
            to_delete = []
            for i in range(len(the_clauses)):
                if the_clauses[i] in match.group(2):
                    to_delete.append(i)
            if len(to_delete) > 0:
                for i in range(len(to_delete)):
                    the_clauses.remove(the_clauses[to_delete[0]])
                the_clauses.insert(to_delete[0], match.group(2))

        the_clauses[-1] = the_clauses[-1][:-1]
        return the_clauses

    @staticmethod
    def __split_sentence(sentence):
        pattern = re.compile("[，。%、！!？?,；～~.… ]+")
        #首先利用strip()函数去除字符串收尾的空格
        #然后利用split()函数通过指定的分隔符（patter中的标点符号）对字符串进行切片
        split_clauses = pattern.split(sentence.strip())
        punctuations = pattern.findall(sentence.strip())
        try:
            split_clauses.remove("")
        except ValueError:
            pass
        punctuations.append("")

        clauses = [''.join(x) for x in zip(split_clauses, punctuations)]

        return clauses

    def __get_phrase_dict(self):
        #定义语法词典
        sentiment_dict = []
        pattern = re.compile(r"\s+")    #匹配多个空白符
        with open(self.__root_filepath + "phrase_dict.txt", "r", encoding="utf-8") as f:
            for line in f:
                a_phrase = {}   #定义一个空字典
                result = pattern.split(line.strip())    #去除首尾空格然后依据中间的空白符分割
                if len(result) >= 2:
                    a_phrase["key"] = result[0]
                    a_phrase["value"] = float(result[1])
                    for i, a_split in enumerate(result):
                        """
                        i为索引，a_split为值
                        如果分割后元素超过2个，则对每一个值再次进行分割
                        """
                        if i < 2:
                            continue
                        else:
                            a, b = a_split.split(":")
                            a_phrase[a] = b
                    sentiment_dict.append(a_phrase)

        return sentiment_dict

    # 情感词典的构建
    @staticmethod
    def __get_dict(path, encoding="utf-8"):
        sentiment_dict = {}
        pattern = re.compile(r"\s+")
        with open(path, encoding=encoding) as f:
            for line in f:
                result = pattern.split(line.strip())
                if len(result) == 2:
                    sentiment_dict[result[0]] = float(result[1])
        return sentiment_dict