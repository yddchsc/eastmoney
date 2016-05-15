# -*- coding: utf-8 -*-
__author__ = 'Bai Chenjia'

import text_process as tp
import numpy as np
import pymongo

# 1.读取情感词典和待处理文件
# 情感词典
print "reading..."
posdict = tp.read_lines("emotion_dict/pos_all_dict.txt")
negdict = tp.read_lines("emotion_dict/neg_all_dict.txt")
# 程度副词词典
mostdict = tp.read_lines('degree_dict/most.txt')   # 权值为2
verydict = tp.read_lines('degree_dict/very.txt')   # 权值为1.5
moredict = tp.read_lines('degree_dict/more.txt')   # 权值为1.25
ishdict = tp.read_lines('degree_dict/ish.txt')   # 权值为0.5
insufficientdict = tp.read_lines('degree_dict/insufficiently.txt')  # 权值为0.25
inversedict = tp.read_lines('degree_dict/inverse.txt')  # 权值为-1

# 2.程度副词处理，根据程度副词的种类不同乘以不同的权值
def match(word, sentiment_value):
	if word in mostdict:
		sentiment_value *= 2.0
	elif word in verydict:
		sentiment_value *= 1.75
	elif word in moredict:
		sentiment_value *= 1.5
	elif word in ishdict:
		sentiment_value *= 1.2
	elif word in insufficientdict:
		sentiment_value *= 0.5
	elif word in inversedict:
		#print "inversedict", word
		sentiment_value *= -1
	return sentiment_value


# 3.情感得分的最后处理，防止出现负数
# Example: [5, -2] →  [7, 0]; [-4, 8] →  [0, 12]
def transform_to_positive_num(poscount, negcount):
	pos_count = 0
	neg_count = 0
	if poscount < 0 and negcount >= 0:
		neg_count += negcount - poscount
		pos_count = 0
	elif negcount < 0 and poscount >= 0:
		pos_count = poscount - negcount
		neg_count = 0
	elif poscount < 0 and negcount < 0:
		neg_count = -poscount
		pos_count = -negcount
	else:
		pos_count = poscount
		neg_count = negcount
	return (pos_count, neg_count)


# 求单条新闻语句的情感倾向总得分
def single_review_sentiment_score(weibo_sent):
	single_review_senti_score = []
	cuted_review = tp.cut_sentence(weibo_sent)  # 句子切分，单独对每个句子进行分析

	for sent in cuted_review:
		seg_sent = tp.segmentation(sent)   # 分词
		seg_sent = tp.del_stopwords(seg_sent)[:]
		#for w in seg_sent:
		#	print w,
		i = 0    # 记录扫描到的词的位置
		s = 0    # 记录情感词的位置
		poscount = 0    # 记录该分句中的积极情感得分
		negcount = 0    # 记录该分句中的消极情感得分

		for word in seg_sent:   # 逐词分析
			#print word
			if word in posdict:  # 如果是积极情感词
				#print "posword:", word
				poscount += 1   # 积极得分+1
				for w in seg_sent[s:i]:
					poscount = match(w, poscount)
				#print "poscount:", poscount
				s = i + 1  # 记录情感词的位置变化

			elif word in negdict:  # 如果是消极情感词
				#print "negword:", word
				negcount += 1
				for w in seg_sent[s:i]:
					negcount = match(w, negcount)
				#print "negcount:", negcount
				s = i + 1

			# 如果是感叹号，表示已经到本句句尾
			elif word == "！".decode("utf-8") or word == "!".decode('utf-8'):
				for w2 in seg_sent[::-1]:  # 倒序扫描感叹号前的情感词，发现后权值+2，然后退出循环
					if w2 in posdict:
						poscount += 2
						break
					elif w2 in negdict:
						negcount += 2
						break
			i += 1
		#print "poscount,negcount", poscount, negcount
		single_review_senti_score.append(transform_to_positive_num(poscount, negcount))   # 对得分做最后处理
	pos_result, neg_result = 0, 0   # 分别记录积极情感总得分和消极情感总得分
	for res1, res2 in single_review_senti_score:  # 每个分句循环累加
		pos_result += res1
		neg_result += res2
	#print pos_result, neg_result
	result = pos_result - neg_result   # 该条新闻情感的最终得分
	result = round(result, 1)
	return result

# 链接pymongo,获取数据表xinwen和guyouhui中的所有新闻
def run_score():
	conn = pymongo.MongoClient("127.0.0.1",27017)
	db = conn.eastmoney #连接库
	stock = db.stock.find()
	xinresults = []
	guresults = []
	j = 0
	for news in stock:
		contents = {}
		comments = {}
		xinresults.append({'id':news['_id'],'name':news['name'],'score':{}})
		guresults.append({'id':news['_id'],'name':news['name'],'score':{}})
		if news.has_key('xinwen'):
			for data in news['xinwen']: # 将xinwen中的每天的新闻都分别连接起来，然后对每天的连接后的新闻分别进行评分。
				if contents.has_key(data['date']) == False:
					key = data['date']
					contents[key] = ""
				key = data['date']
				content = data['content'].strip()
				content = content.encode("UTF-8",'ignore')
				contents[key] = contents[key] + "。" + content
				score = single_review_sentiment_score(contents[key])  # 对每条新闻调用函数求得打分
				xinresults[j]['score'][key] = score # 将分数存入字典		
		if news.has_key('guyouhui'):			
			for data in news['guyouhui']:  # 将guyouhui中的每天的帖子正文和评论都分别连接起来，然后对每天的连接后的字符串分别进行评分。
				if comments.has_key(data['date']) == False:
					key = data['date']
					comments[key] = ""
				key = data['date']
				content = data['content'].strip() #获取帖子正文
				content = content.encode("UTF-8",'ignore')
				comments[key] = comments[key] + "。" + content
				for a in data['comments']: # 获取该帖子对应的所有评论
					content = data['comments'][a]['comment'].strip()
					content = content.encode("UTF-8",'ignore')
					comments[key] = comments[key] + "。" + content
				score = single_review_sentiment_score(comments[key])  #调用函数求得打分
				guresults[j]['score'][key] = score # 将分数存入字典
		j = j + 1
	return xinresults,guresults # 返回每天新闻得分和股友会得分的字典

# 将对应股票的每天的有效值按行写入结果文件中
def write_results(results,filename):
	fp_result = open(filename, 'w')
	for key in sorted(list(results.keys())):# 按日期排序写入
		fp_result.write(key)
		fp_result.write(' ')
		fp_result.write(str(results[key]))
		fp_result.write('\n')
	fp_result.close()

def prepare(xinresults,guresults):
	conn = pymongo.MongoClient("127.0.0.1",27017)
	db = conn.eastmoney #连接库
	geguyanbao = db.stock.find()
	geguyaowen = db.stock.find()
	gongsigonggao = db.stock.find()
	hangyeyaowen = db.stock.find()
	
	geguyanbao = get_data(geguyanbao,'geguyanbao','_id',guresults) # 获取每天个股研报的数量
	geguyaowen = get_data(geguyaowen,'geguyaowen','_id',guresults) # 获取每天个股要闻的数量 
	gongsigonggao = get_data(gongsigonggao,'gongsigonggao','_id',guresults) # 获取每天公司公告的数量
	hangyeyaowen = get_data(hangyeyaowen,'hangyeyaowen','_id',guresults)
	# 获取每天行业要闻的数量
	xinresults = get_data(xinresults,'score','id',guresults) # 获取每天新闻的分数
	return geguyanbao,geguyaowen,gongsigonggao,hangyeyaowen,xinresults
def get_data(arrays,sstr1,sstr2,guresults):
	number = len(guresults)
	a = {}
	for data in guresults: # 由于股友会的数据比较多，基本上每天都有，故以股友会的日期为基础筛选出其它5个的30天的数据。
		for i in xrange(0,number):
			if data['id'] == arrays[i][sstr2]:
				a[data['id']] = {}
				for key in data['score']:
					if arrays[i].has_key(sstr1) == False:
						a[data['id']][key] = 0
					else:
						if arrays[i][sstr1].has_key(key): # 判断这个日期是否存在，不存在就说明数量为0
							a[data['id']][key] = arrays[i][sstr1][key]
						else:
							a[data['id']][key] = 0
						
				break
	return a # 返回挑选出的30天的数据

if __name__ == '__main__':
	xinresults,guresults = run_score() # 得到30天里每天新闻和股吧的极性得分
	geguyanbao,geguyaowen,gongsigonggao,hangyeyaowen,xinresults = prepare(xinresults,guresults)
	for data in guresults:
		result = {}
		print data['name']
		print "-----------------------------"
		print u"日期      新闻（变化率） 要闻（变化率） 公告（变化率） 研报（变化率） 新闻情感  讨论情感"
		print "-----------------------------"
		for key in sorted(list(data['score'].keys())): # 按日期排序输出
			print key+"        "+str(hangyeyaowen[data['id']][key])+"        "+str(geguyaowen[data['id']][key])+"        "+str(gongsigonggao[data['id']][key])+"        "+str(geguyanbao[data['id']][key])+"        "+str(xinresults[data['id']][key])+"        "+str(data['score'][key])
			result[key] = 0
			if geguyanbao[data['id']][key] > np.asarray(geguyanbao[data['id']].values()).mean() + 0.2 * np.asarray(geguyanbao[data['id']].values()).std(): # 判断是否为有效值
				result[key] = result[key] + 1
			if geguyaowen[data['id']][key] > np.asarray(geguyaowen[data['id']].values()).mean() + 0.2 * np.asarray(geguyaowen[data['id']].values()).std(): # 判断是否为有效值
				result[key] = result[key] + 1
			if gongsigonggao[data['id']][key] > np.asarray(gongsigonggao[data['id']].values()).mean() + 0.2 * np.asarray(gongsigonggao[data['id']].values()).std(): # 判断是否为有效值
				result[key] = result[key] + 1
			if hangyeyaowen[data['id']][key] > np.asarray(hangyeyaowen[data['id']].values()).mean() + 0.2 * np.asarray(hangyeyaowen[data['id']].values()).std(): # 判断是否为有效值
				result[key] = result[key] + 1
			if xinresults[data['id']][key] > np.asarray(xinresults[data['id']].values()).mean() + 0.2 * np.asarray(xinresults[data['id']].values()).std(): # 判断是否为有效值
				result[key] = result[key] + 1
			if data['score'][key] > np.asarray(data['score'].values()).mean() + 0.2 * np.asarray(data['score'].values()).std(): # 判断是否为有效值
				result[key] = result[key] + 1
		write_results(result,data['name']+'.txt') # 将每只股票每天有效值的数量结果写入文件