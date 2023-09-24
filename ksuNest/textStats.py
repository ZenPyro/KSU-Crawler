import json
from pathlib import Path
import re
from matplotlib import pyplot as plt
import nltk
from nltk.corpus import stopwords

class textStats(object):
    json_file = Path("textData/text_data.json").open()

    # IMPORTANT NOTE: We have to make note that the `json` file `dict` instance that is ->
    #-> returned, is actually two dimensional, since we have the entry number, ->
    #-> as one sort of "key" and the actual entry data type (like `pageid` or `emails`) ->
    #-> as the other key
    json_data = json.load(json_file)

    docs = 0
    doc_len = 0
    known_emails = []
    numEmail = 0
    email = str
    total_emails = dict.fromkeys([email])
    word_dict = dict()
    # Definitely will optimize all of the code below one day, so that the time complexity ->
    #-> is not so high
    for entryid in json_data:
        docs = docs + 1
        # print(f"""{json_data[entryid]["pageid"]}""" + f"""{json_data[entryid]["emails"]}""")
        for token in json_data[entryid]["body"]:
            # Below line of code is regex to trim numbers and any leftover unwanted tokens ->
            #-> from the word tokens
            indiv_token = re.findall(r"[a-zA-Z]+", token)
            #print(indiv_token)
            for indiv in indiv_token:
                doc_len = doc_len + 1
                
                if indiv not in word_dict:
                    word_dict[indiv] = {"count": 1}
                    #print("WAHOO")
                else:
                    word_dict[indiv] = {"count": word_dict[indiv]["count"] + 1}

        for email in json_data[entryid]["emails"]:
            # Below line of code is using regex to trim hanging periods off the end of ->
            #-> emails (stop identical emails being seen as different from a left `.`)
            email = re.sub(r"[.]$", "", email)
            if email not in known_emails:
                known_emails.append(email)
                total_emails[email] = 1
            else:
                total_emails[email] = total_emails[email] + 1
        # Below `if-statement` keeps track of how many documents have emails at all
        if  len(json_data[entryid]["emails"]) != 0:
            numEmail = numEmail + 1


    print(f"Number of Documents: {docs}")
    print(f"Total Combined Document Length: {doc_len}")
    print(f"Average Document Length: {doc_len/docs}")
    print()

    print("Emails: ")
    i = 0
    for email in total_emails:
        if total_emails[email] is not None and i < 9:
            print(f"\tName: {email}")
            print(f"\tTotal Occurrences: {total_emails[email]}")
            print()
            i = i + 1

    print(f"Percentage of Documents Containing at Least One Email Address: {(numEmail/docs)*10}%")
    print()

    # Line below, may not clone
    #temp_word_dict = word_dict.copy()
    
    # for word in temp_word_list:
    #     # Below print out is super important because it shows the problem I was running ->
    #     #-> into earlier, which is I was treating the dictionary not as a dictionary ->
    #     #-> within a dictionary
    #     #print(word[1]["count"])

    #     # Below two lines is because dictionaries do not like to be compared (find out ->
    #     # #-> why later)
    #     # wordCount = temp_word_dict[word]["count"]
    #     # temp_word_dict[tempW]["count"]
    #     if temp_word_list[i][1]["count"] < temp_word_list[i+1][1]["count"]:
    #         temp = temp_word_list[i+1]
    #         temp_word_list[i+1] = temp_word_list[i]
    #         temp_word_list[i] = temp
    #     else:
    #           continue  
    #     i = i + 1
    
    # Doing the much easier way for this because I have to prepare for the Autumn Festival ->
    #-> tomorrow (re-do it later)
    print("rank\t\tterm\tfreq.\t\tperc.")
    print("-----\t\t-----\t-----\t\t-----\t\t")
    sorted_word = sorted(word_dict.items(), key = lambda x: x[1]["count"], reverse = True)
    distFig_word = sorted(word_dict.items(), key = lambda x: x[1]["count"], reverse = True)
    i = 0
    while i < 30:
        print(f"""{i+1}\t\t{sorted_word[i][0]}\t{sorted_word[i][1]["count"]}\t\t{sorted_word[i][1]["count"]/doc_len}""")
        i = i + 1
    

    nltk.download("stopwords")
    stopword_list = []
    for i in sorted_word:
        #NOTE: The `lower()` instance function just makes sure all of the words are ->
        #-> uniformally lowercase before being looked at as a "stop-word" ("stop-words" ->
        #-> in the library are only in lowercase)
        if i[0].lower() in stopwords.words("english"):
            stopword_list.append(i)
    # Had to make this second `for-loop` to remove the found "stop-words" after the whole ->
    #-> `list` instance had been iterated through because if I did not, the `list` instance ->
    #-> would shrink but the `for-loop` would carry on as if it did not, so it would skip ->
    #-> "stop-words"        
    for word in stopword_list:
        sorted_word.remove(word)        
            
            
    
    i = 0
    print("[Stop-Word Filtered]")
    print("rank\t\tterm\tfreq.\t\tperc.")
    print("-----\t\t-----\t-----\t\t-----\t\t")
    while i < 30:
        print(f"""{i+1}\t\t{sorted_word[i][0]}\t{sorted_word[i][1]["count"]}\t\t{(sorted_word[i][1]["count"]/doc_len)}""")
        i = i + 1
    
    # I need to reformat this `list` with a "hidden" `dict` instance inside because it is ->
    #-> becoming a huge problem when trying to feed it to these pre-made library functions
    final_sorted_word = dict()
    i = 0
    for word in distFig_word:
        i = i + 1
        final_sorted_word[i] = word[1]["count"]
    
    # BELOW IS OLD WAY OF PRINTING GRAPH:
    #print(final_sorted_word)
    # word_fdist = nltk.FreqDist(final_sorted_word)
    # fig, ax = plt.subplots(figsize = (10,6))
    # for label in ax.xaxis.get_minorticklabels():
    #     label.set_visible(False)
    # for label in ax.xaxis.get_ticklines():
    #     label.set_visible(False)
    # plt.tick_params()
    # word_fdist.plot(1000, cumulative = False)
    
    #IMPORTANT NOTE: The `dict` instance `final_sorted_word` must be split into ->
    #-> two seperate `list` like instances, that we can then use for the corresponding ->
    #-> `x` (keys) and `y` (values). We could have gave over just a dictionary that was ->
    #-> turned into a `FreqDist` instance, but it was creating a massive black blotch ->
    #-> on the bottom of the graph, due to it drawing every tick for every point on the ->
    #-> graph
    plt.plot(final_sorted_word.keys(), final_sorted_word.values())
    #NOTE: VSCode's terminal is a headless environment, so I have to save the figure ->
    #-> somewhere and open it
    plt.savefig("wordDist.png")

    #word_fdist = nltk.FreqDist(final_sorted_word)
    #plt.axis([0,1000,0,1000])
    plt.xscale("log")
    plt.yscale("log")
    plt.plot(final_sorted_word.keys(), final_sorted_word.values())
    #word_fdist.plot(cumulative = False)
    #NOTE: VSCode's terminal is a headless environment, so I have to save the figure ->
    #-> somewhere and open it
    plt.savefig("logDist.png")

