11 
# Natural Language Toolkit: Eliza
#
# Copyright (C) 2001-2010 NLTK Project
# Authors: Steven Bird <sb@csse.unimelb.edu.au>
#          Edward Loper <edloper@gradient.cis.upenn.edu>
# URL: <http://www.nltk.org/>
# For license information, see LICENSE.TXT

# Based on an Eliza implementation by Joe Strout <joe@strout.net>,
# Jeff Epler <jepler@inetnebr.com> and Jez Higgins <mailto:jez@jezuk.co.uk>.

# a translation table used to convert things you say into things the
# computer says back, e.g. "I am" --> "you are"
import re
from util import *

# a table of response pairs, where each pair consists of a
# regular expression, and a list of possible responses,
# with group-macros labelled as %1, %2.
message = "cjjmurray@gmail.com"
person = message.split( '@', 1 )[0]

START_PAT_1 = r"""(.*)"""
END_PAT_1 = """(.*)"""	 
TIME_HOUR_MIN_PAT = """
	 (?P<hourmin>         # $time: 24hr or 12hr clock AM/PM time.
	   (?:                # Group for 24hr options.
	   [2][0-3]           # Hour is either 20, 21, 22, 23,
	   | [01]?[0-9]       # or 0-9, 00-09 or 10-19
	   )                  # End group of 24HR options.
	   (?:                # Group for optional minutes.
	   :                  # Hours and minutes separated by ":" 
	   [0-5][0-9]         # 00-59 minutes
	   )?                 # 24hr minutes are optional.
	 |                    # or time is given in AM/PM format.
	   (?:1[0-2]|0?[1-9]) # 1-12 or 01-12 AM/PM options (hour)
	   (?::[0-5][0-9])?   # Optional minutes for AM/PM time.
		 \s*              # Optional whitespace before AM/PM.
	   [ap]m              # Required AM or PM (case insensitive)
	 )                    # End group of time options.
"""

TIME_INFORMAL_TIME_PAT = """
	 \s?                  # Optional whitespace.
	 (?P<informal>noon|midday|midnight|lunch.?(time)?)
	 \s?                  # Optional whitespace 
"""

TIME_AS_TEXT_PAT = """
	 \s?                  # Optional whitespace.
	 (?P<timeastext>one|two|couple|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty
	 |twenty one|twenty two|twenty three|twenty four|twenty five|twenty six|twenty seven|twenty eight|twenty nine|thirty|thirty one|thirty two|thirty three
	 |thirty four|thirty five|thirty six|thirty seven|thirty eight|thirty nine|fourty|fourty one||fourty two|fourty three|fourty four|fourty five|fourty six
	 |fourty seven|fourty eight|fourty nine|fifty|fifty one|fifty two|fifty three|fifty four||fifty five|fifty six|fifty seven|fifty eight|fifty nine|sixty)
	 \s?                  # Optional whitespace 
"""

TIME_ORD_WORD_PAT = """
	 \s?                  # Optional whitespace.
	 (?P<ordword>first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth)
	 \s?                  # Optional whitespace 
"""

TIME_OFFSET_PAT = """
	 \s?                  # Optional whitespace.
	 (?P<offset> \d+ )    # $offset: count of time increments.
	 \s?                  # Optional whitespace.
"""

TIME_ORD_DIGIT_PAT = """
	 \s?                  # Optional whitespace.
	 (?P<orddig> \d+ ?(st|nd|rd|th) )    # $ordinal of digits: first, second, third, fourth etc.
	 \s?                  # Optional whitespace.
"""

TIME_UNITS_PAT = """
	 \s?
	 (?P<units>           # $units: units of time increment.
	   (?:sec(?:ond)?|min(ute)?|hour|day|week|month|year|decade|century)
	   s?                 # Time units may have optional plural "s".
	 )                    # End $units: units of time increment.
"""

TIME_MONTH_PAT = """
	 \s?
	 (?P<month>           # $units: units of time increment.
	   (jan(uary)?|feb(uary)?|mar(ch)?|apr(il)?|may|jun(e)?|jul(y)?|aug(ust)?|sep(tember)?|oct(tober)?|nov(ember)?|dec(ember)?)
	   s?                 # Time units may have optional plural "s".
	 )                    # End $units: units of time increment.
"""

TIME_DIR_PAT = """
	 \s?                  # Optional whitespace.
	 (?P<dir>from|before|since|last|ago|next|on|after) # #dir: Time offset direction.
	 \s?                  # Optional whitespace.
"""

TIME_BASE_PAT = """
	 \s?                  # Optional whitespace.
	 (?P<base>yesterday|today|tomorrow|(?:right )?now|monday|tuesday|wednsday|thursday|friday|saturday|sunday)
	 \s?                  # Optional whitespace 
"""

TIME_COMB_PAT_1 = START_PAT_1+TIME_HOUR_MIN_PAT+END_PAT_1 # 2pm, 23:00
TIME_COMB_PAT_2 = START_PAT_1+TIME_HOUR_MIN_PAT+END_PAT_1 # 
# list of prepositions taken from article on wikipedia http://en.wikipedia.org/wiki/Preposition

gram_prepositions=("on", "in", "to", "by", "for", "with", "at", "of", "from", "as")

gram_conjunction=("and","nor","but","or","yet","so")

gram_correlative_conjunctions=("either","neither""not only","both","whether")

gram_pronouns=("you","ye","thou","we","they","them","it","our","something")

gram_interjections=("uh", "ahem", "oops", "so", "like", "whoops", "uh", "er", "um")

timetext = (
  (TIME_COMB_PAT_1,
  ( "ampm"))
)

# timetext2 = (
  # (r'(.*)([0-9]|1[012])(am|pm) \d+ (days? on|days? next|days? from) (((monday|tuesday|wednsday|thursday|friday|saturday|sunday)|(yesterday|today|now|tomorrow))(.*)',
  # ( "TimeNeedLength")),

  # (r'(.*)\d+ (days? on|days? next|days? from) ((monday|tuesday|wednsday|thursday|friday|saturday|sunday)|(yesterday|today|now|tomorrow))(.*)',
  # ( "TimeNeedHour")),

  # (r'(.*)a couple of days from (monday|tuesday|wednsday|thursday|friday|saturday|sunday|yesterday|today|now|tomorrow)(.*)',
  # ( "TimeNeedHour")),

  # (r'(.*)next (monday|tuesday|wednsday|thursday|friday|saturday|sunday) at ([0-9]|1[012])(am|pm)(.*)',
  # ( "TimeNeedLength"))
  
  # (r'(.*)\d+ minutes? ago(.*)',
  # ( "10 minutes ago")),
 
  # (r'(.*)([0-9]|1[012])(am|pm) next Sunday(.*)',
  # ( "2pm next Sunday")),

  # (r'(.*)in \d+ weeks?(.*)',
  # ( "in 2 weeks")),

  # (r'(.*)in \d+ days? at ([0-9]|1[012])(am|pm)(.*)',
  # ( "in 3 days at 5pm")),

  # (r'(.*)\d+ minutes? ago(.*)',
  # ( "10 minutes ago")),

  # (r'(.*)\d+ minutes? from now(.*)',
  # ( "10 minutes from now")),

  # (r'(.*)in \d+ minutes?(.*)',
  # ( "in 10 minutes")),

  # (r'(.*)in a minute(.*)',
  # ( "in a minute")),

  # (r'(.*) in a couple of minutes(.*)',
  # ( "in a couple of minutes")),

  # (r'(.*) 20 seconds ago(.*)',
  # ( "20 seconds ago")),

  # (r'(.*) in 30 seconds(.*)',
  # ( "in 30 seconds")),

  # (r'(.*) 20 seconds before noon(.*)',
  # ( "20 seconds before noon")),

  # (r'(.*) 20 seconds before noon tomorrow(.*)',
  # ( "20 seconds before noon tomorrow")),

  # (r'(.*) midnight(.*)',
  # ( "midnight")),

  # (r'(.*) noon tomorrow(.*)',
  # ( "noon tomorrow")),

  # (r'(.*) 6am tomorrow(.*)',
  # ( "6am tomorrow")),

  # (r'(.*) 0800 yesterday(.*)',
  # ( "0800 yesterday")),

  # (r'(.*) 12:15 AM today(.*)',
  # ( "12:15 AM today")),

  # (r'(.*) 3pm 2 days from today(.*)',
  # ( "3pm 2 days from today")),

  # (r'(.*) a week from today(.*)',
  # ( "a week from today")),  

  # (r'(.*) a week from now(.*)',
  # ( "a week from now")),

  # (r'(.*) 3 weeks ago(.*)',
  # ( "3 weeks ago")),
 
  # (r'(.*)today(.*)',
  # ( "TimeNeedHour")),

  # (r'(.*)tomorrow(.*)',
  # ( "TimeNeedHour")),

  # (r'(.*)yesterday(.*)',
  # ( "TimeNeedHour")),

  # (r'(.*)in a couple of days(.*)',
  # ( "TimeNeedHour")),

  # (r'(.*)in a day(.*)',
  # ( "TimeNeedHour")),

  # (r'(.*)a day ago(.*)',
  # ( "a day ago")),

  # (r'(.*) noon next Sunday(.*)',
  # ( "noon next Sunday")),

  # (r'(.*) noon Sunday(.*)',
  # ( "noon Sunday")),  

  # (r'(.*) noon last Sunday(.*)',
  # ( "noon last Sunday")),

  # (r'now(.*)',
  # ( "now")),

# )

	
pairs = (
  (r'I need (.*)',
  ( "Why do you need %1?",
    "Would it really help you to get %1?",
    "Are you sure you need %1?")),
  
  (r'Why don\'t you (.*)',
  ( "Do you really think I don't %1?",
    "Perhaps eventually I will %1.",
    "Do you really want me to %1?")),
  
  (r'Why can\'t I (.*)',
  ( "Do you think you should be able to %1?",
    "If you could %1, what would you do?",
    "I don't know -- why can't you %1?",
    "Have you really tried?")),
  
  (r'I can\'t (.*)',
  ( "How do you know you can't %1?",
    "Perhaps you could %1 if you tried.",
    "What would it take for you to %1?")),
  
  (r'I am (.*)',
  ( "Did you come to me because you are %1?",
    "How long have you been %1?",
    "How do you feel about being %1?")),
  
  (r'I\'m (.*)',
  ( "How does being %1 make you feel?",
    "Do you enjoy being %1?",
    "Why do you tell me you're %1?",
    "Why do you think you're %1?")),
  
  (r'Are you (.*)',
  ( "Why does it matter whether I am %1?",
    "Would you prefer it if I were not %1?",
    "Perhaps you believe I am %1.",
    "I may be %1 -- what do you think?")),
  
  (r'What (.*)',
  ( "Why do you ask?",
    "How would an answer to that help you?",
    "What do you think?")),
  
  (r'How (.*)',
  ( "How do you suppose?",
    "Perhaps you can answer your own question.",
    "What is it you're really asking?")),
  
  (r'Because (.*)',
  ( "Is that the real reason?",
    "What other reasons come to mind?",
    "Does that reason apply to anything else?",
    "If %1, what else must be true?")),
  
  (r'(.*) sorry (.*)',
  ( "There are many times when no apology is needed.",
    "What feelings do you have when you apologize?")),
  
  (r'Hi(.*)',
  ( "Hi.. " + person,
	"Hi there..."  + person + " how are you today?",
	"Hello, "  + person + " how are you feeling today?")),
  
  (r'Hello(.*)',
  ( "Hello..."  + person + " I'm glad you could drop by today.",
	"Hi there..."  + person + " how are you today?",
	"Hello, "  + person + " how are you feeling today?")),
  
  (r'I think (.*)',
  ( "Do you doubt %1?",
    "Do you really think so?",
    "But you're not sure %1?")),
  
  (r'(.*) friend (.*)',
  ( "Tell me more about your friends.",
    "When you think of a friend, what comes to mind?",
    "Why don't you tell me about a childhood friend?")),
  
  (r'Yes',
  ( "You seem quite sure.",
    "OK, but can you elaborate a bit?")),
  
  (r'(.*) computer(.*)',
  ( "Are you really talking about me?",
    "Does it seem strange to talk to a computer?",
    "How do computers make you feel?",
    "Do you feel threatened by computers?")),
  
  (r'Is it (.*)',
  ( "Do you think it is %1?",
    "Perhaps it's %1 -- what do you think?",
    "If it were %1, what would you do?",
    "It could well be that %1.")),
  
  (r'It is (.*)',
  ( "You seem very certain.",
    "If I told you that it probably isn't %1, what would you feel?")),
  
  (r'Can you (.*)',
  ( "What makes you think I can't %1?",
    "If I could %1, then what?",
    "Why do you ask if I can %1?")),
  
  (r'Can I (.*)',
  ( "Perhaps you don't want to %1.",
    "Do you want to be able to %1?",
    "If you could %1, would you?")),
  
  (r'You are (.*)',
  ( "Why do you think I am %1?",
    "Does it please you to think that I'm %1?",
    "Perhaps you would like me to be %1.",
    "Perhaps you're really talking about yourself?")),
  
  (r'You\'re (.*)',
  ( "Why do you say I am %1?",
    "Why do you think I am %1?",
    "Are we talking about you, or me?")),
  
  (r'I don\'t (.*)',
  ( "Don't you really %1?",
    "Why don't you %1?",
    "Do you want to %1?")),
  
  (r'I feel (.*)',
  ( "Good, tell me more about these feelings.",
    "Do you often feel %1?",
    "When do you usually feel %1?",
    "When you feel %1, what do you do?")),
  
  (r'I have (.*)',
  ( "Why do you tell me that you've %1?",
    "Have you really %1?",
    "Now that you have %1, what will you do next?")),
  
  (r'I would (.*)',
  ( "Could you explain why you would %1?",
    "Why would you %1?",
    "Who else knows that you would %1?")),
  
  (r'Is there (.*)',
  ( "Do you think there is %1?",
    "It's likely that there is %1.",
    "Would you like there to be %1?")),
  
  (r'My (.*)',
  ( "I see, your %1.",
    "Why do you say that your %1?",
    "When your %1, how do you feel?")),
  
  (r'You (.*)',
  ( "We should be discussing you, not me.",
    "Why do you say that about me?",
    "Why do you care whether I %1?")),
    
  (r'Why (.*)',
  ( "Why don't you tell me the reason why %1?",
    "Why do you think %1?" )),
    
  (r'I want (.*)',
  ( "What would it mean to you if you got %1?",
    "Why do you want %1?",
    "What would you do if you got %1?",
    "If you got %1, then what would you do?")),
  
  (r'(.*) mother(.*)',
  ( "Tell me more about your mother.",
    "What was your relationship with your mother like?",
    "How do you feel about your mother?",
    "How does this relate to your feelings today?",
    "Good family relations are important.")),
  
  (r'(.*) father(.*)',
  ( "Tell me more about your father.",
    "How did your father make you feel?",
    "How do you feel about your father?",
    "Does your relationship with your father relate to your feelings today?",
    "Do you have trouble showing affection with your family?")),
	
(r'(.*)fuck(.*)',
  ( "Millenia of human evolution, and that's all you can say to me, meh!",
    "What the f...")),

  (r'(.*) child(.*)',
  ( "Did you have close friends as a child?",
    "What is your favorite childhood memory?",
    "Do you remember any dreams or nightmares from childhood?",
    "Did the other children sometimes tease you?",
    "How do you think your childhood experiences relate to your feelings today?")),
    
  (r'(.*)\?',
  ( "Why do you ask that?",
    "Please consider whether you can answer your own question.",
    "Perhaps the answer lies within yourself?",
    "Why don't you tell me?")),
  
  (r'quit',
  ( "Thank you for talking with me.",
    "Good-bye.",
    "Thank you, that will be $150.  Have a good day!")),
  
  (r'(.*)',
  ( "Please tell me more.",
    "Let's change focus a bit... Tell me about your family.",
    "Can you elaborate on that?",
    "Why do you say that %1?",
    "I see.",
    "Very interesting.",
    "%1.",
    "I see.  And what does that tell you?",
    "How does that make you feel?",
    "How do you feel when you say that?"))
)

augmi_chatbot = Chat( pairs, reflections)

def augmi_chat():
    print "---------------------------"
    print "----- Augmi Chat 2011 -----"
    print "---------------------------"

    augmi_chatbot.converse()

def demo():
    augmi_chat()

if __name__ == "__main__":
    demo()
  
match = reobj.match(' 3 pm 2 days from today')
if match:
	print('Time:       %s' % (match.group('time')))
	print('Offset:     %s' % (match.group('offset')))
	print('Units:      %s' % (match.group('units')))
	print('Direction:  %s' % (match.group('dir')))
	print('Base time:  %s' % (match.group('base')))
else:
	print("No match.")

