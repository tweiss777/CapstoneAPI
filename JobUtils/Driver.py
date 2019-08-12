#region import statements
import json
import re as regex
import sys
from collections import Counter
from pprint import pprint
import nltk
import numpy as np
from docx import Document
# from gensim.summarization import keywords

from JobUtils.DataProcessor import *

#endregion

'''Helper function to check for either stemmed or unstemmed terms and return a list of unique
terms found either stemmed or unstemmed'''
# Note: terms in setToCompareWith should be lower cased for best results
def filterByStemming(termsToStem, setToCompareWith):
    stemmer = nltk.PorterStemmer()

    stemmedRegTerms = []
    uniqueTerms = []

    for term in termsToStem:
        stemmedTerm = stemmer.stem(term)
        if stemmedTerm[-1] == "'" or stemmedTerm[-1] == "’":
            stemmedTerm = stemmedTerm.replace(stemmedTerm[-1], "")
        stemmedRegTerms.append((stemmedTerm, term.lower()))

    for i, (stemmedTerm, regTerm) in enumerate(stemmedRegTerms):
        if stemmedTerm not in setToCompareWith and regTerm not in setToCompareWith:
            uniqueTerms.append(termsToStem[i])
    return uniqueTerms

# helper method that takes in the resume as a word document and returns the resume text as a string
def process_resume(resume):
    file = open(resume,'rb')
    d = Document(file)
    fullText = []
    resumeText = ""

    # iterate through the paragraphs
    for p in d.paragraphs:
        fullText.append(p.text)
    
    for text in fullText:
        try:
            # Iterate through the array removing indices that have length of 0
            if len(text) == 0:
                fullText.remove(text)
        except IndexError:
            pass
    # iterate through the fullText array and strip \n and \t
    for i in range(len(fullText)):
        fullText[i] = re.sub("\s+", " ",
                                     fullText[i])  # if there is text remove the extra space and the and the tabs
        resumeText = resumeText + fullText[
                    i] + " "  # concatinate part of the resume text to the job description
    return resumeText



# This is the main algorithm
def main(jobSearch,zipcode,resumeFile):
    containsNumsSpecialChars = r'^[!@#$%^&*(),.?":{}|<>0-9]*$'
    # BEGIN SECTION FOR PRE-PROCESSING

    # initialize the data processor object
    dp = DataProcessor()
    
    # # System args for query,zipcode, and resume
    # jobSearch = sys.argv[1]
    # zipcode = sys.argv[2]
    # resumeFile = sys.argv[3]
    
    # Get the jobs from indeed.com
    print("Getting jobs")
    jobs, jobs2 = dp.get_jobs(jobSearch, zipcode, 10)
    originalJobs = jobs
    print("Jobs retrieved")
    for i in range(len(jobs)):
        jobs[i]["description"] = dp.joinByRegex(jobs[i]["description"])

    # get the bigrams for the paragraph separated jobs
    jobs2_bigrams = dp.get_all_bigrams_paragraphs(jobs2, 3)

    # strip certain parts of speech
    jobs2_bigrams_processed = dp.process_jobs_paragraphs(jobs2_bigrams)

    resumeStr = resumeFile
    resumeStr = dp.joinByRegex(resumeStr)

    # This segregates the paragraphs in the resume
    # resumeList = dp.process_resume(resumeFile, True)

    #filter out empty paragraphs
    # resumeList = [paragraph for paragraph in resumeList if len(paragraph) > 0]


    # pre process the resume
    resumeStrUpdated = dp.strip_resume_stopwords_punctuation_pos(resumeStr)
    # resumeListUpdated = dp.strip_resume_stopwords_punctuation_pos(resumeList)

    
    # get potential keywords filter by pos (NO LONGER USED GOING TO BE REMOVED IN FUTURE COMMITS)
    # resume_keywords = dp.filter_pos(resumeStrUpdated, ["NN", "NNS", "NNP", "NNPS"])
    # resume_keywords = list(set(resume_keywords))

    # #getting keywords via gensim, (NO LONGER USED GOING TO BE REMOVED IN FUTURE COMMITS)
    # resume_keywords = keywords(" ".join(w for w in resumeStrUpdated), split="\n")
    # resume_keywords = [w[0] for w in nltk.pos_tag(resume_keywords) if w[1] in ["NN", "NNS", "NNP", "NNPS"]]
    # resume_keywords = [w for w in resume_keywords if bool(regex.match(containsNumsSpecialChars, w)) is False]

    # pre process the jobs wihtout the bigrams
    processed_jobs = dp.process_jobs(jobs)
    processed_jobs_noBigrams = processed_jobs

    # Method that will retrieve the bigrams for the jobs
    # Bi-grams that appear twice or more
    processed_jobs_no_bigrams = processed_jobs
    for i in range(len(processed_jobs)):
        processed_jobs[i]["description"] = dp.get_bigrams(processed_jobs[i]["description"], 2)

    processed_jobs_all_bigrams = dp.get_all_bigrams(processed_jobs_no_bigrams, 3)

    

    # END OF PRE-PROCESSING SECTION
    # process tf-idf for the whole resume
    # x = the jobs
    # y = the resume
    # process tf-idf for the whole resume
    x1, y1, features = dp.tf_idf(processed_jobs_all_bigrams, resumeStrUpdated)

    similarity_score_whole = dp.get_cosine_similarity(x1, y1)
    # BEGIN OUTPUTTING RESULTS

    # retrieve the top 5 job indices using argsort
    # argsort sorts by putting the highest valued indice at the last index
    top_5_indices = similarity_score_whole.argsort()[:-6:-1]

    top_5_jobs = {}
    for i in top_5_indices:
        top_5_jobs[i] = (similarity_score_whole[i], jobs[i]["title"] + " " + jobs[i]["description"])

    # Take the top 5 scores and use them to get the relevant paragraphs.
    top_5_jobs_paragraphs = {}
    for i in top_5_indices:
        top_5_jobs_paragraphs[i] = {}
        top_5_jobs_paragraphs[i]["title"] = jobs2_bigrams_processed[i]["title"]
        top_5_jobs_paragraphs[i]["description"] = jobs2_bigrams_processed[i]["description"]

    # Section to get the matching keywords from the entire dataset sorted based on relevancy of job
    top_indices = similarity_score_whole.argsort()[::-1]


    # updated list of words from the resume filtered for proper nouns
    resumeStrUpdatedPosFiltered = dp.filter_pos(resumeStrUpdated, POS_to_keep=["NNP"])

    # Lowercase the terms from the resume to be used to find intersection with the propernouns
    resumeProperNouns = [t.lower() for t in resumeStrUpdatedPosFiltered]

    # tuple that consists of job id and list of all keywords from the job only
    jobKeyWordsOnly = []
    for indice in top_indices:
        jobKeywords = dp.findSkills(jobs[indice]["description"])
        # jobKeywords = dp.filter_pos(processed_jobs_all_bigrams[indice]["description"], POS_to_keep=["NNP"])
        jobKeyWordsOnly.append((indice, jobKeywords))

    # Counter object that keeps track of all the words in the dataset
    jobsKeyWordCount = Counter()
    for job_id, terms in jobKeyWordsOnly:
        for term in terms:
            jobsKeyWordCount[term] += 1

    # jobKeywordsOnlyFrequency = {}
    #
    # for job_id, terms in jobKeyWordsOnly:
    #     for term in terms:
    #         if term in jobKeywordsOnlyFrequency:
    #             jobKeywordsOnlyFrequency[term] += 1
    #         else:
    #             jobKeywordsOnlyFrequency[term] = 1

    sortedJobKeyWordCount = sorted(jobsKeyWordCount, key=lambda x: jobsKeyWordCount[x])

    # get the sum of the total number of words in the entire job set
    totalWordsInJobSet = 0
    for term, count in jobsKeyWordCount.items():
        totalWordsInJobSet = totalWordsInJobSet + count

    # filter the words with a frequency threshold greater than 1.5% (L1)
    sortedJobKeyWordCountFiltered = [term for term in sortedJobKeyWordCount if
                                     (jobsKeyWordCount[term] / totalWordsInJobSet) * (100) >= .15]

    # get the intersection of words from the resume and the proper nouns
    # initialize var called properNouns which will take the terms from the jobKeyWordsOnlyFrequencySortedUpdated and lower case the terms
    properNouns = [t.lower() for t in sortedJobKeyWordCountFiltered]

    # typecase properNouns to a set same with proper nouns from the resume
    properNounsSet = set(properNouns)
    resumeProperNounsSet = set(resumeProperNouns)

    # retrieve the intersection of resume terms and proper nouns below (L2)
    intersectionResumeJobs = resumeProperNounsSet.intersection(properNounsSet)

    # retrieve the intersection of the words from each of the top 5 jobs with the proper nouns (L3)
    matchingProperNounsPerTop5Jobs = []
    for indice in top_indices:
        nnps = dp.findSkills(jobs[indice]["description"])
        nnps = [t.lower() for t in nnps]
        matchingProperNounsPerTop5Jobs.append((indice, properNounsSet.intersection(set(nnps))))

    properNounsResumeNTop5Jobs = []
    # retrieve the intersection between the proper nouns in your resume and top 5 jobs
    for indice, properNouns in matchingProperNounsPerTop5Jobs:
        properNounsResumeNTop5Jobs.append((indice, properNouns.intersection(resumeProperNounsSet)))

    # retrieve the proper noun non-matches between each of the top 5 jobs and the resume
    nonMatchesPerTop5Jobs = []

    # add terms that are in the job description but not in the resume
    for jobId, terms in matchingProperNounsPerTop5Jobs:
        nonMatchesPerTop5Jobs.append((jobId, [t for t in terms if t not in intersectionResumeJobs]))

    # Add the difference of terms to a list to be sorted and filtered
    nonMatches = []
    for term, count in jobsKeyWordCount.items():
        for job, terms in nonMatchesPerTop5Jobs:
            for t in terms:
                if t == term.lower() and nonMatches.count(term) < 1:
                    nonMatches.append(term)

    # filter for non matching terms with a threshold greater than 0.5%
    sortedNonMatches = sorted(nonMatches, key=lambda x: jobsKeyWordCount[x])
    sortedNonMatchesFiltered = [t for t in sortedNonMatches if (jobsKeyWordCount[t] / totalWordsInJobSet) * 100 <= 0.5]

    # Split sortedNonMatchesFiltered based on this regular expression '[:\() \s]'
    sortedNonMatchesFilteredSplit = [regex.split(r'[:\()/ \s]', nonMatch) for nonMatch in sortedNonMatchesFiltered]

    # Create a list of possible missing skills from the resume
    possibleMissingSkills = []
    for lst in sortedNonMatchesFilteredSplit:
        for t in lst:
            if t.lower() not in intersectionResumeJobs:
                possibleMissingSkills.append(t)

    # Create a dictionary that holds bool value indicating a lower case occurence of proper noun
    lowerCaseOccurence = {}
    for term in possibleMissingSkills:
        lowerCaseOccurence[term] = False

    # search the dataset for lowercase occurences and change dict values to true if there is a lowercase occurence
    for term, value in lowerCaseOccurence.items():
        for i in range(len(processed_jobs_all_bigrams)):
            if term.lower() in processed_jobs_all_bigrams[i]["description"]:
                lowerCaseOccurence[term] = True

    possibleMissingSkillsUpdated = [t for t in possibleMissingSkills if lowerCaseOccurence[t] is not True]

    possibleMissingSkillsUpdated2 = filterByStemming(possibleMissingSkillsUpdated, resumeProperNounsSet)
    # print("Intersection between resume and job set (matching terms from both resume and the jobs)")
    # pprint(properNounsResumeNTop5Jobs)

    # print("Possible missing skills\n")
    # pprint(possibleMissingSkillsUpdated2)


    # JSON DATA NEEDS TO BE RESTRUCTURED
    data_dict = {}
    json_data = []
    possibleMissingSkillsLowered = [t.lower() for t in possibleMissingSkillsUpdated2]
    for i, indice in enumerate(top_indices):
        
        data_dict[int(indice)] = {}
        data_dict[int(indice)]["Title"] = originalJobs[indice]["title"]
        data_dict[int(indice)]["Description"] = originalJobs[indice]["description"]
        data_dict[int(indice)]["Matching_keywords"] = [keyword for keyword in properNounsResumeNTop5Jobs[i][1]]
        data_dict[int(indice)]["Missing_keywords"] = [keyword for keyword in nonMatchesPerTop5Jobs[i][1] if
                                                 keyword in possibleMissingSkillsLowered]
        data_dict[int(indice)]["JobUrl"] = originalJobs[indice]["job_url"]
    
    for jobID, info in data_dict.items():
        json_data.append(info)    

    print(json_data)
    return json_data
