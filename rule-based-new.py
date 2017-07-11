from textblob import TextBlob
from textblob import Word
import random
import sys
import cmd2
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import numpy as np
import warnings
warnings.filterwarnings("ignore")


class Chatbot(cmd2.Cmd):

	#class variables
	quantity_main=[]
	sub_cat_item=[]
	cost=[]

	#start of the main function
	def do_in(self, sentence):
		
		
		#converts words to numbers(like two->2)

		sentence=convert_w2n(sentence)

		#TextBlob is used  preprocessing the input
		parsed=TextBlob(sentence)
		parsed=parsed.lower()

		#correct the spelling if present
		parsed=parsed.correct()
		
		#check main category menu,subcategory menu,and quantity
		
		resp=check_for_main_category(parsed)
		if resp==None:
			resp=check_for_menu(parsed)
			
		if resp==None:
			resp=check_for_greeting(parsed)
		if(resp==None):
			check_for_quantity(parsed)
		
		#prints the output
		if resp!=None:
			print (resp)

		elif((len(Chatbot.sub_cat_item)!=0) and (len(Chatbot.quantity_main)!=0)):
			
		 	print "Total cost of your order placed for  is",find_cost()	

		else:
			print (construct_response(parsed))
			
	#end of the main function

	def do_EOF(self, sentence):
		return True

#function to converts words to number(two->2)		
def convert_w2n(sentence):

	dictionary={'one':'1','two':'2','three':'3','four':4}
		
	for i,j in dictionary.items():

		if i in sentence:
			new_sentence=sentence.replace(i,dictionary[i])
			sentence=new_sentence

	return sentence

#function to show menu card
def check_for_menu(parsed):

	for word in parsed.words:
		word = Word(word)
 		word.lemmatize()
		if word.lower()=="menu":
			return "We provide coffee,deserts,snacks"

#function to show greetings			

def check_for_greeting(parsed):

	Greetings_KeyWords=("hello","hi","greetings","sup","hey")
	Greetings_Responses=["hi,we welcome you","Hello","How you doing?"]

	for word in parsed.words:
		word = Word(word)
 		word.lemmatize()
		if word.lower() in Greetings_KeyWords:
			return random.choice(Greetings_Responses)

#function to check for main category			
def check_for_main_category(parsed):

	main_category_keywords=("coffee","deserts","snacks")
	main_category_response=("Can U specify some details,like which kind of ","what kind of")

	for  word in parsed.words:
		word = Word(word)
 		word.lemmatize()
		if word.lower() in main_category_keywords:

			check_for_quantity(parsed)
			return  random.choice(main_category_response)+" "+word+" "+"would you like to have?"

		else:

			for i in main_category_response:

				if(fuzz.ratio(word,i)>85):

					check_for_quantity(parsed)
					return  random.choice(main_category_response)+" "+i+" "+"would you like to have?"

	sub_cat=check_for_sub_category(parsed)

	return sub_cat


#function to check for sub-category
def check_for_sub_category(parsed):

	
	sub_category_keywords={"cappucinno":20,"mocha":20,"latte":30,"sandwich":30,"roll":25,"pasteries":30,"cookies":10}
	sub_category_response=("How many")

	for  word in parsed.words:
		word = Word(word)
 		word.lemmatize()
		if word.lower() in sub_category_keywords:
			
			Chatbot.sub_cat_item.append(word)
			
			Chatbot.cost.append(int(sub_category_keywords[word]))


		else :

			for i,j in sub_category_keywords.items():
				if (fuzz.ratio(word,i)>85):
					
					Chatbot.sub_cat_item.append(i)
					Chatbot.cost.append(int(sub_category_keywords[i]))
	check_for_quantity(parsed)

	# if (len(Chatbot.quantity_main)!=0):
		
	#  	pass
	# else:
	# 	check_for_quantity(parsed)
	
	if(len(Chatbot.sub_cat_item)!=0):

		if(len(Chatbot.quantity_main)!=0):
								
				return "Total cost of your placed order is",find_cost()
					
		else:
				return "how many"


#function to find the bill
def find_cost():
	

	total_bill	= np.multiply(Chatbot.cost,Chatbot.quantity_main)
	
	return sum(total_bill)		
	
#function to check quantity
def check_for_quantity(parsed):
	
	prev_word=None

	for word,part_of_speech in parsed.pos_tags:
		word = Word(word)
 		word.lemmatize()
		if part_of_speech=='CD':

			Chatbot.quantity_main.append(int(word))

		elif  prev_word=='a' and part_of_speech=='NN':
			
			Chatbot.quantity_main.append(1)

		prev_word=word
		

# none of the special cases matched so we're going to try to construct a 
# full sentence that uses as much of the user's input as possible	
def construct_response(parsed):
	
	resp = []

	#assigning pos tags
	pronoun,noun,verb,adjective=find_Pos(parsed)


	if pronoun:
		resp.append(pronoun)

	if verb:
		verb_word = verb[0]

		if verb_word in ('be', 'am', 'is', "'m",'hmmm'):  

			if pronoun.lower() == 'you':

				# The bot will always tell the person they aren't whatever they said they were
				resp.append("aren't really")
					
			else:
				resp.append(verb_word)

		elif verb_word in ('have','want'):
				
					resp.append(" ")
	if adjective:
		resp.append(" "+ adjective)

	if noun:
		
		resp.append(" " + noun)

	resp.append(random.choice(("cool", "lol", "huh","oh!")))
	resp.append(", Can you ask something else please?")

	return " ".join(resp)

#function to parse sentence and find pos tags
def find_Pos(parsed):

	pronoun=None
	noun=None
	adjective=None
	verb=None

	for sent in parsed.sentences:

		#pos tags
		pronoun=find_pronoun(sent)
		noun=find_noun(sent)
		verb=find_verb(sent)
		adjective=find_adjective(sent)

	return pronoun,noun,verb,adjective

#finds pronoun
def find_pronoun(sent):

	pronoun=None

	for word,part_of_speech in sent.pos_tags:
		
		if part_of_speech=='PRP' and word.lower()=='you':
			pronoun='I'

		elif part_of_speech=='PRP' and word.lower=='i':
			pronoun='You'
	
	return pronoun

#finds noun
def find_noun(sent):

	noun=None

	for word,part_of_speech in sent.pos_tags:

		if part_of_speech=='NN':
			noun=word

	return noun

#finds verb
def find_verb(sent):
	verb=None
	for word,part_of_speech in sent.pos_tags:
		if part_of_speech=='VB':
			verb=word
	return verb

def find_adjective(sent):

	adjective=None

	for word,part_of_speech in sent.pos_tags:

		if part_of_speech=='JJ':
			adjective=word

	return adjective


#execution starts here
if __name__ == '__main__':
	Chatbot().cmdloop()