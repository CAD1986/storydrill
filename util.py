# Natural Language Toolkit: Chatbot Utilities
#
# Copyright (C) 2001-2010 NLTK Project
# Authors: Steven Bird <sb@csse.unimelb.edu.au>
# URL: <http://www.nltk.org/>
# For license information, see LICENSE.TXT

# Based on an Eliza implementation by Joe Strout <joe@strout.net>,
# Jeff Epler <jepler@inetnebr.com> and Jez Higgins <jez@jezuk.co.uk>.

import string
import re
import random
import logging
# import MontyLingua
from deltatime_py import *
# m = MontyLingua.MontyLingua()


reflections = {
  "am"     : "are",
  "was"    : "were",
  "i"      : "you",
  "i'd"    : "you would",
  "i've"   : "you have",
  "i'll"   : "you will",
  "my"     : "your",
  "are"    : "am",
  "you've" : "I have",
  "you'll" : "I will",
  "your"   : "my",
  "yours"  : "mine",
  "you"    : "me",
  "me"     : "you"
}

class Chat(object):
    def __init__(self, pairs, reflections={}): #timetext,
        """
        Initialize the chatbot.  Pairs is a list of patterns and responses.  Each
        pattern is a regular expression matching the user's statement or question,
        e.g. r'I like (.*)'.  For each such pattern a list of possible responses
        is given, e.g. ['Why do you like %1', 'Did you ever dislike %1'].  Material
        which is matched by parenthesized sections of the patterns (e.g. .*) is mapped to
        the numbered positions in the responses, e.g. %1.

        @type pairs: C{list} of C{tuple}
        @param pairs: The patterns and responses
        @type reflections: C{dict}
        @param reflections: A mapping between first and second person expressions
        @rtype: C{None}
        """
        #self._timetext = [(re.compile(x, re.IGNORECASE),y) for (x,y) in timetext]
        self._pairs = [(re.compile(x, re.IGNORECASE),y) for (x,y) in pairs]
        self._reflections = reflections
        self._regex = self._compile_reflections()


    def _compile_reflections(self):
        sorted_refl = sorted(self._reflections.keys(), key=len,
                reverse=True)
        return  re.compile(r"\b({0})\b".format("|".join(map(re.escape,
            sorted_refl))), re.IGNORECASE)

    def _substitute(self, str):
        """
        Substitute words in the string, according to the specified reflections,
        e.g. "I'm" -> "you are"

        :type str: str
        :param str: The string to be mapped
        :rtype: str
        """

        return self._regex.sub(lambda mo:
                self._reflections[mo.string[mo.start():mo.end()]],
                    str.lower())

    def _wildcards(self, response, match):
        pos = response.find('%')
        while pos >= 0:
            num = int(response[pos+1:pos+2])
            response = response[:pos] + \
                self._substitute(match.group(num)) + \
                response[pos+2:]
            pos = response.find('%')
        return response


    
    def respond(self, str):
        """
        Generate a response to the user input.
        
        @type str: C{string}
        @param str: The string to be mapped
        @rtype: C{string}
        """
        #for (pattern, response) in self._timetext:
            #match = pattern.match(str)

            # did the pattern match?
            #if  match:
                # now we have a matched string we need to get the date substring from str
              #  matchedSubString = match.findall(str)
                # cant find a method of etracting the above date substring other than using the single group [0]
                # returned by findall - remember the regex has only one set of () to return one group only hence-
               # dateString = str(matchedSubString[0])
                # now dateString is in a suitable format for parsing below
               # res = nlTimeExpression.parseString(dateString)
               # if "calculatedTime" in res:
                #    return res.calculatedTime
                    
        for (pattern, response) in self._pairs:
            # well it's not a time query, so go to general text converse
            logging.info(pattern)
            match = re.search(pattern,str)
            logging.info("+++++pre Match str = " + str)
            resp = "I am Trying to understand......not working!"
            
            # did the pattern match?
            if match:
                logging.info("-------its matched = match")
                resp = random.choice(response)    # pick a random response
                resp = self._wildcards(resp, match) # process wildcards

                # fix munged punctuation at the end
                if resp[-2:] == '?.': resp = resp[:-2] + '.'
                if resp[-2:] == '??': resp = resp[:-2] + '?'
                

                return resp
            
                
 

     # Hold a conversation with a chatbot
    def converse(self, quit="quit"):
        input = ""
        while input != quit:
            input = quit
            try: input = raw_input(":)")
            except EOFError:
                print input
            if input:
                while input[-1] in "!.": input = input[:-1]
                print self.respond(input)
                    

